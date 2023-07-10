import pymesh
import numpy as np
import argparse
from numpy.linalg import norm

"""
The meshes generated by Pymesh functions are pointing outside; The ones generated by chroma defaults are pointing inside.
Use invert_mesh to turn chroma mesh into outside one;
The rotation_extrusion is rotated in y-axis: use a pi/2 rotation to turn into z-axis diretion
"""
thickness = 0.001

def rotation_matrix(thetax,thetay,thetaz):

    rx = np.array([[1,0,0], [0,np.cos(thetax),-1*np.sin(thetax)], [0,np.sin(thetax),np.cos(thetax)]])
    ry = np.array([[np.cos(thetay),0,np.sin(thetay)], [0,1,0], [-1*np.sin(thetay),0,np.cos(thetay)]])
    rz = np.array([[np.cos(thetaz),-1*np.sin(thetaz),0], [np.sin(thetaz),np.cos(thetaz),0], [0,0,1]])
    m = np.dot(np.dot(rx, ry), rz)
    return m

def invert_mesh(mesh):
    # from the imported mesh, generate a inverted one: 
    # Triangles reverted
    # the input ought to be a mesh object
    vertices = mesh.vertices
    triangles = mesh.faces
    triangles_new = np.flipud(triangles)

    # for chroma mesh, rotate pi/2 in x axis to turn into z-axis
    vertices_new = np.dot(vertices,rotation_matrix(-np.pi/2,0,0))
    mesh_new = pymesh.meshio.form_mesh(vertices_new, triangles_new, voxels=None)
    return mesh_new

def generate_circular_vertex(theta,r,steps):
    # generate vertices on a circle, centering (0,0,0), starting from theta=0
    x = r * np.cos(np.linspace(0,theta/180*np.pi,steps))
    y = r * np.sin(np.linspace(0,theta/180*np.pi,steps))
    z = np.zeros((1,len(x)))[0]
    points = np.transpose([x,y,z])
    return points

def generate_linear_vertex(start,end,steps):
    # 3d linear space
    x = np.linspace(start[0],end[0],steps)
    y = np.linspace(start[1],end[1],steps)
    z = np.linspace(start[2],end[2],steps)
    points = np.transpose([x,y,z])
    return points

def displacement(vertices, dx=0, dy=0, dz=0):
    # x-y-z dispacement for a numpy array
    points = vertices
    cache = points[:] + np.array([dx,dy,dz])
    return cache

def distance(vertice, x,y,z):
    # get the distance (squared) to point x,y,z
    p = np.array([x,y,z])
    delta = vertice - p
    d = np.dot(delta,delta)
    return d


def fix_mesh(mesh, detail="normal"):
    bbox_min, bbox_max = mesh.bbox
    diag_len = norm(bbox_max - bbox_min)
    if detail == "normal":
        target_len = diag_len * 5e-3
    elif detail == "high":
        target_len = diag_len * 2.5e-3
    elif detail == "low":
        target_len = diag_len * 1e-2
    print("Target resolution: {} mm".format(target_len))

    count = 0
    mesh, __ = pymesh.remove_degenerated_triangles(mesh, 100)
    mesh, __ = pymesh.split_long_edges(mesh, target_len)
    num_vertices = mesh.num_vertices
    while True:
        mesh, __ = pymesh.collapse_short_edges(mesh, 1e-6)
        mesh, __ = pymesh.collapse_short_edges(mesh, target_len,
                                               preserve_feature=True)
        mesh, __ = pymesh.remove_obtuse_triangles(mesh, 150.0, 100)
        if mesh.num_vertices == num_vertices:
            break

        num_vertices = mesh.num_vertices
        print("#v: {}".format(num_vertices))
        count += 1
        if count > 10: break

    mesh = pymesh.resolve_self_intersection(mesh)
    mesh, __ = pymesh.remove_duplicated_faces(mesh)
    mesh = pymesh.compute_outer_hull(mesh)
    mesh, __ = pymesh.remove_duplicated_faces(mesh)
    mesh, __ = pymesh.remove_obtuse_triangles(mesh, 179.0, 5)
    mesh, __ = pymesh.remove_isolated_vertices(mesh)

    return mesh

def clean(mesh):
    # clean the redundancies before exporting
    mesh, info = pymesh.remove_isolated_vertices(mesh)
    mesh, info = pymesh.remove_duplicated_vertices(mesh, 0.00001)
    mesh, info = pymesh.remove_duplicated_faces(mesh)
    return mesh

# ====================================================================================
# meshes below

def sapphire_viewpoint():
    # pick out the sensitive surface
    # mesh object: the center (0,0,0) being the lower surfece of the column
    d = 0.03647
    h = 0.001
    mesh = pymesh.generate_cylinder([0,0,0], [0,0,h], d/2, d/2, num_segments=64)
    return mesh

#head_ref.stl
def cut(mesh):
    # used to cut a hole at (x0,y0) with diameter D
    D = 0.12065
    d = 0.02476
    x0 = 0
    y0 = 0
    vertices = mesh.vertices
    faces = mesh.faces
    # step 1: tagging all the vertices inside the hole
    hole_index = []
    for i in vertices:
        hole_index.append(distance(i,x0,y0,0) < ((D*D/4) - 0.0005))
    hole_index = np.arange(len(vertices))[np.array(hole_index)]
    # step 2: exclude all the (vertices and ?) triangles related
    index = [] # label these triangles
    for i in faces:
        a = i[0] in hole_index
        b = i[1] in hole_index
        c = i[2] in hole_index
        index.append(not (a or b or c)) # any triangle containing vertice in the hole will be "False"

    index_array = np.array(index)
    faces_new = faces[index_array]
    
    # step 3: tagging all the vertices at the hole boundary
    hole_vert_index = []
    for i in vertices:
        hole_vert_index.append( (distance(i,x0,y0,0) < ((D*D/4) + 0.0005)) and (distance(i,x0,y0,0) > ((D*D/4) - 0.0005)) )
    hole_vert_index = np.arange(len(vertices))[np.array(hole_vert_index)]
    # step 4: exclude the triangles with 3 hole_vertices
    index_vert = [] # label these triangles
    for i in faces_new:
        a = i[0] in hole_vert_index
        b = i[1] in hole_vert_index
        c = i[2] in hole_vert_index
        index_vert.append(not (a and b and c))
    
    index_vert_array = np.array(index_vert)
    faces_new = faces_new[index_vert_array]
    mesh_new = pymesh.meshio.form_mesh(vertices, faces_new, voxels=None)
    
    return mesh_new

def head_reflector():
    # a sector in x-y plane. The symmetry axis is y. The hole is the center.
    L = 0.15239 # sector radius
    D = 0.12065 # hole diameter
    d = 0.02476
    # distance_to_center = 0.08385791
    vertices = generate_circular_vertex(64,L,50)
    endpoint = vertices[len(vertices)-1]
    vertices = np.concatenate((vertices,generate_linear_vertex(endpoint,[0,0,0],100)))
    vertices = np.concatenate((vertices, np.dot(vertices, np.diag([1,-1,1])))) # mirror in x-z plane
    # the bigger sector shape, centered at (0,0,0)
    hole = displacement(generate_circular_vertex(360,D/2,100), d+D/2, 0, 0)
    # the smaller circular hole inside, centered at x = d+D/2
    vertices = np.concatenate((vertices, hole))
    vertices = np.dot(displacement(vertices, -d-D/2, 0,0), rotation_matrix(0,0,-np.pi/2))
    tri = pymesh.triangle()
    tri.max_num_steiner_points = 100
    tri.points = vertices
    tri.verbosity = 1
    tri.run()
    mesh = tri.mesh
    # the initial pymesh triangle method. This mesh has failed in creating the hole
    mesh_cut = cut(mesh)
    return mesh_cut

    # use pymesh to remove isolated vertice / remesh

    # Tried boolean method, fails (not PWN mesh)
    """
    tri_hole = pymesh.triangle()
    tri_hole.max_num_steiner_points = 50
    tri_hole.points = hole
    tri_hole.verbosity = 1
    tri_hole.run()
    mesh_hole = tri_hole.mesh
    mesh_final = pymesh.boolean(mesh, mesh_hole, operation = 'difference', engine = 'igl')
    return mesh_final"""

# head_cone.stl
def head_cone():
    # mesh object: the center (0,0,0) being the lower plane of the tube
    D = 0.12065
    d = 0.0508
    h = 0.060325
    mesh = pymesh.generate_tube([0,0,0], [0,0,h], D/2 + thickness, d/2 + thickness, D/2, d/2, num_segments=64, with_quad=False)
    return mesh

# dome_ref.stl
def dome_reflector():
    # mesh object: the center (0,0,0) being the center of the object, lies in x-y plane 

    d = 0.09805/2
    D = 0.11294/2
    L = 0.09119
    h = np.sqrt(L*L-(D-d)*(D-d))
    vertices = np.array([[D,h/2,0],[-D,h/2,0],[d,-h/2,0],[-d,-h/2,0]])
    tri = pymesh.triangle()
    tri.points = vertices
    tri.verbosity = 1
    tri.run()
    mesh = tri.mesh
    return mesh

# oj_ref.stl
def oj_ref():
    # mesh object: center (0,0,0) being the bottom
    r = 0.12235
    h = 0.22225
    mesh = pymesh.generate_tube([0,0,0], [0,0,h], r + thickness, r + thickness, r, r, num_segments=64, with_quad=False)
    return mesh

# ij_ref.stl
def ij_ref():
    # mesh object: center (0,0,0) being the bottom 
    R = 0.092075
    d = 0.0762
    L = 0.05771
    h = np.sqrt(L*L - (R-d/2)*(R-d/2)) # around 0.02042
    mesh = pymesh.generate_cylinder([0,0,0], [0,0,h], R, d/2, num_segments=64)
    return mesh

def sipm():
    # no longer used. replaced by newly written function in detector construction
    a = 0.0141
    mesh = pymesh.generate_box_mesh([0, 0], [a, a], num_samples=1, keep_symmetry=False, subdiv_order=0, using_simplex=True)
    return mesh

def mesh_grid(grid):
    begin = grid[:-1].flatten()
    end = grid[1:].flatten()
    begin_roll = np.roll(grid[:-1],-1,1).flatten()
    end_roll = np.roll(grid[1:],-1,1).flatten()
    
    mesh = np.empty(shape=(2*len(begin),3), dtype=begin.dtype)
    mesh[:len(begin),0] = begin
    mesh[:len(begin),1] = end
    mesh[:len(begin),2] = end_roll
    mesh[len(begin):,0] = begin
    mesh[len(begin):,1] = end_roll
    mesh[len(begin):,2] = begin_roll
    return mesh

def norm(x):
    "Returns the norm of the vector `x`."
    return np.sqrt((x*x).sum(-1))

def normalize(x):
    "Returns unit vectors in the direction of `x`."
    x = np.atleast_2d(np.asarray(x, dtype=float))
    return (x/norm(x)[:,np.newaxis]).squeeze()

def rotate(x, phi, n):
    """
    Rotate an array of points `x` through an angle phi counter-clockwise
    around the axis `n` (when looking towards +infinity).
    """
    n = normalize(n)
    x = np.atleast_2d(x)
    phi = np.atleast_1d(phi)

    return (x*np.cos(phi)[:,np.newaxis] + n*np.dot(x,n)[:,np.newaxis]*(1-np.cos(phi)[:,np.newaxis]) + np.cross(x,n)*np.sin(phi)[:,np.newaxis]).squeeze()

def rotate_extrude(x, y, nsteps=64):
    """
    Return the solid mesh formed by extruding the profile defined by the x and
    y points `x` and `y` around the y axis.

    .. note::
        The path traced by the points `x` and `y` should go counter-clockwise,
        otherwise the mesh will be inside out.

    Example:
        >>> # create a bipyramid
        >>> m = rotate_extrude([0,1,0], [-1,0,1], nsteps=4)
    """
    if len(x) != len(y):
        raise Exception('`x` and `y` arrays must have the same length.')

    points = np.array([x,y,np.zeros(len(x))]).transpose()

    steps = np.linspace(0, 2*np.pi, nsteps, endpoint=False)
    vertices = np.vstack([rotate(points,angle,(0,-1,0)) for angle in steps])
    triangles = mesh_grid(np.arange(len(vertices)).reshape((len(steps),len(points))).transpose()[::-1])
    mesh = pymesh.meshio.form_mesh(vertices, triangles, voxels=None)

    return mesh

def draw_a_circle(center,angle,r,theta):
    steps = 64
    x = r * np.cos(np.linspace(angle, angle+theta, steps)) + center[0]
    y = r * np.sin(np.linspace(angle, angle+theta, steps)) + center[1]
    return [x,y]

def oj_out():
    # mesh object: center (0,0,0) being the bottom
    h = 0.22225
    r = 0.12
    r1 = 0.04
    t1 = 66.4/180*np.pi
    c1 = [r-r1,h]
    r2 = 0.24
    t2 = 47.2/180*np.pi/2
    c2 = [0,h-r2*np.cos(t2)+r1*np.sin(t1)]
    # 2 lines, 2 curves. All suppose sitting at z = 0 (thus, starting from (0,0))
    X = np.array([0,r,r])
    Y = np.array([0,0,h])
    circle = draw_a_circle(c1, 0, r1, t1)
    X = np.concatenate((X,circle[0]))
    Y = np.concatenate((Y,circle[1]))
    circle = draw_a_circle(c2, np.pi/2-t2, r2, t2)
    X = np.concatenate((X,circle[0]))
    Y = np.concatenate((Y,circle[1]))

    mesh = rotate_extrude(X, Y, nsteps=64)
    return invert_mesh(mesh)

def oj_in():
    # mesh object: center (0,0,0) being the bottom
    h = 0.22225
    r = 0.115
    r1 = 0.035
    t1 = 66.4/180*np.pi
    c1 = [r-r1,h]
    r2 = 0.235
    t2 = 47.2/180*np.pi/2
    c2 = [0,h-r2*np.cos(t2)+r1*np.sin(t1)]
    # 2 lines, 2 curves. All suppose sitting at z = 0 (thus, starting from (0,0))
    X = np.array([0,r,r])
    Y = np.array([0,0,h])
    circle = draw_a_circle(c1, 0, r1, t1)
    X = np.concatenate((X,circle[0]))
    Y = np.concatenate((Y,circle[1]))
    circle = draw_a_circle(c2, np.pi/2-t2, r2, t2)
    X = np.concatenate((X,circle[0]))
    Y = np.concatenate((Y,circle[1]))

    mesh = rotate_extrude(X, Y, nsteps=64)
    return invert_mesh(mesh)

def ij_out():
    # mesh object: center (0,0,0) being the bottom
    h = 0
    r = 0.105
    r1 = 0.03
    t1 = 65.4/180*np.pi
    c1 = [r-r1,h]
    r2 = 0.21
    t2 = 49.2/180*np.pi/2
    c2 = [0,h-r2*np.cos(t2)+r1*np.sin(t1)]
    # 2 lines, 2 curves. All suppose sitting at z = 0 (thus, starting from (0,0))
    X = np.array([0,r,r])
    Y = np.array([0,0,h])
    circle = draw_a_circle(c1, 0, r1, t1)
    X = np.concatenate((X,circle[0]))
    Y = np.concatenate((Y,circle[1]))
    circle = draw_a_circle(c2, np.pi/2-t2, r2, t2)
    X = np.concatenate((X,circle[0]))
    Y = np.concatenate((Y,circle[1]))

    mesh = rotate_extrude(X, Y, nsteps=64)
    return invert_mesh(mesh)

def ij_in():
    # mesh object: center (0,0,0) being the bottom
    h = 0
    r = 0.1
    r1 = 0.025
    t1 = 65.4/180*np.pi
    c1 = [r-r1,h]
    r2 = 0.205
    t2 = 49.2/180*np.pi/2
    c2 = [0,h-r2*np.cos(t2)+r1*np.sin(t1)]
    # 2 lines, 2 curves. All suppose sitting at z = 0 (thus, starting from (0,0))
    X = np.array([0,r,r])
    Y = np.array([0,0,h])
    circle = draw_a_circle(c1, 0, r1, t1)
    X = np.concatenate((X,circle[0]))
    Y = np.concatenate((Y,circle[1]))
    circle = draw_a_circle(c2, np.pi/2-t2, r2, t2)
    X = np.concatenate((X,circle[0]))
    Y = np.concatenate((Y,circle[1]))

    mesh = rotate_extrude(X, Y, nsteps=64)
    return invert_mesh(mesh)

def head_ref_try():
    L = 0.15239
    D = 0.12065
    d = 0.02476
    vertices = generate_circular_vertex(64,L,50)
    endpoint = vertices[len(vertices)-1]
    vertices = np.concatenate((vertices,generate_linear_vertex(endpoint,[0,0,0],100)))
    vertices = np.concatenate((vertices, np.dot(vertices, np.diag([1,-1,1])))) # mirror in x-z plane
    # the bigger sector shape, centered at (0,0,0)
    hole = displacement(generate_circular_vertex(360,D/2,100), d+D/2, 0, 0)
    # the smaller circular hole inside, centered at x = d+D/2
    vertices = np.concatenate((vertices, hole))
    tri = pymesh.triangle()
    tri.max_num_steiner_points = 100
    tri.points = vertices
    tri.verbosity = 1
    tri.run()
    mesh = tri.mesh
    return mesh

# ============================edit: merged with meshes_new==========================
def bubble_1():
    radius = 0.005
    center = [0,0,0]
    mesh = pymesh.generate_icosphere(radius, center, refinement_order=1)
    return mesh

def bubble_2():
    radius = 0.005
    center = [0,0,0]
    mesh = pymesh.generate_icosphere(radius, center, refinement_order=2)
    return mesh

def fix_mesh(mesh, detail="normal"):
    bbox_min, bbox_max = mesh.bbox
    diag_len = norm(bbox_max - bbox_min)
    if detail == "normal":
        target_len = diag_len * 5e-3
    elif detail == "high":
        target_len = diag_len * 2.5e-3
    elif detail == "low":
        target_len = diag_len * 1e-2
    print("Target resolution: {} mm".format(target_len))

    count = 0
    mesh, __ = pymesh.remove_degenerated_triangles(mesh, 100)
    mesh, __ = pymesh.split_long_edges(mesh, target_len)
    num_vertices = mesh.num_vertices
    while True:
        mesh, __ = pymesh.collapse_short_edges(mesh, 1e-6)
        mesh, __ = pymesh.collapse_short_edges(mesh, target_len,
                                               preserve_feature=True)
        mesh, __ = pymesh.remove_obtuse_triangles(mesh, 150.0, 100)
        if mesh.num_vertices == num_vertices:
            break

        num_vertices = mesh.num_vertices
        print("#v: {}".format(num_vertices))
        count += 1
        if count > 10: break

    mesh = pymesh.resolve_self_intersection(mesh)
    mesh, __ = pymesh.remove_duplicated_faces(mesh)
    mesh = pymesh.compute_outer_hull(mesh)
    mesh, __ = pymesh.remove_duplicated_faces(mesh)
    mesh, __ = pymesh.remove_obtuse_triangles(mesh, 179.0, 5)
    mesh, __ = pymesh.remove_isolated_vertices(mesh)

    return mesh

if __name__ == '__main__':
    #pymesh.meshio.save_mesh('sapphire.stl', clean(sapphire_viewpoint()))
    #pymesh.meshio.save_mesh('head_cone.stl',clean(head_cone()))
    #pymesh.meshio.save_mesh('head_ref.stl',clean(head_reflector()))
    #pymesh.meshio.save_mesh('head_ref_try.stl',head_ref_try())
    #pymesh.meshio.save_mesh('dome_ref.stl',clean(dome_reflector()))
    pymesh.meshio.save_mesh('oj_ref.stl',fix_mesh(oj_ref(), detail="low"))
    pymesh.meshio.save_mesh('ij_ref.stl',fix_mesh(ij_ref(), detail="low"))
    mesh = clean(oj_out())
    pymesh.meshio.save_mesh('oj_out.stl',fix_mesh(mesh, detail="low"))
    mesh = clean(ij_out())
    pymesh.meshio.save_mesh('ij_out.stl',fix_mesh(mesh, detail="low"))
    mesh = clean(oj_in())
    pymesh.meshio.save_mesh('oj_in.stl',fix_mesh(mesh, detail="low"))
    mesh = clean(ij_in())
    pymesh.meshio.save_mesh('ij_in.stl',fix_mesh(mesh, detail="low"))
    #pymesh.meshio.save_mesh('sipm.stl',sipm())
    pymesh.meshio.save_mesh('bubble_1.stl', clean(bubble_1()))
    pymesh.meshio.save_mesh('bubble_2.stl', clean(bubble_2()))