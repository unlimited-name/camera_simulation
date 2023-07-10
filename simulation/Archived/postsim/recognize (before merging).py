import numpy as np
from mathematics import get_cylindrical, normalize, rotation_matrix, get_angles, unit_vector

"""
A file used to determine which reflector a photon is hitting onto

We encode the reflectors as follow:
0 - inner jar ref (flat part)
1 - inner jar ref (cone part)
2 - outer jar ref
3 to 10 - head ref num 1-8; the one with phi=0 is labeled 1, and sequenced in counter-clockwise direction
11 to 13 - dome ref num 1-3; labeled the same as above

for quick use, import recognize() or diffuse_direction()
"""

normal_head = []
vec_head = np.array([0, -np.cos(14.82/180*np.pi), np.sin(14.82/180*np.pi)])
for i in range(8):
    normal_head.append(np.dot(vec_head, rotation_matrix(0,0,np.pi/4*i)))
normal_dome = []
vec_dome = np.array([0, -np.sin(22.5/180*np.pi), -np.cos(22.5/180*np.pi)])
for i in range(3):
    normal_head.append(np.dot(vec_head, rotation_matrix(0,0,2*np.pi/3*i)))
# data taken from meshes.py
r_ij_bottom = 0.092075
r_ij_top = 0.0762/2
L = 0.05771    
h_ij = np.sqrt(L*L - (r_ij_bottom-r_ij_top)*(r_ij_bottom-r_ij_top))
r_oj = 0.12235
h_oj = 0.22225
r_threshold = 0.15 # recongnized "escaped" photons, if larger than this value
h_distinguish = 0.34 # measured height of distinguish between two sets of reflectors
h_space = 0.4 # upper cap of geometry
slope_ij = np.arctan((r_ij_bottom-r_ij_top) / h_ij)
vec_ij = np.array([np.cos(slope_ij), 0, np.sin(slope_ij)])
vec_oj = np.array([-1,0,0])

def recognize(position):
    z,r,phi = get_cylindrical(position)
    if (r<=r_ij_top) and (z<h_ij+0.001) and (z>h_ij-0.001):
        return 0
    elif (r<=r_ij_bottom) and (z<h_ij+0.001) and (z>=0):
        return 1
    elif (r<r_oj+0.001) and (r>=r_oj-0.001) and (z>=0) and (z<= h_oj):
        return 2
    elif (z>h_oj) and (z<h_distinguish) and (r<r_threshold):
        delta = phi-np.pi/2+np.pi/8
        return int(delta/np.pi*4)+3
    elif (z>h_distinguish) and (z<h_space) and (r<r_threshold):
        delta = phi-np.pi/2+np.pi/3
        return int(delta/np.pi/2*3)+11
    else:
        return 15

# normal vectors used, obtained depending on the position of photon
def normal_inner(position):
    theta,phi = get_angles(position)
    return np.dot(vec_ij, rotation_matrix(0,0,phi))

def normal_outer(position):
    theta,phi = get_angles(position)
    return np.dot(vec_oj, rotation_matrix(0,0,phi))

def diffuse_direction(position):
    """
    depending on the initial photon position hitting on the reflector,
    generate a random direction vector, depending on the mechanism of diffuse reflection.
    """
    refnum = recognize(position)
    if refnum==0:
        return np.array([0,0,1])
    elif refnum==1:
        # the normal vector on inner jar ref
        return normal_inner(position)
    elif refnum==2:
        # the normal vector on outer jar ref
        return normal_outer(position)
    elif (refnum>2) or (refnum<11):
        # the normal vector should be that of the reflector
        return normal_head[refnum-3]
    elif (refnum>=11) and (refnum<14):
        # the normal vector should be that of the reflector
        return normal_dome[refnum-11]
    else:
        # junk photon
        return None

def angular_paint(direction, normal = np.array([0,0,1])):
    """
    using input vectors of direction, "paint" on θ-φ plot. each input point will 
    have a "paint distance" of 5 degree; screening along θ-φ, and determine if 
    a pixel is painted.

    the input should be a collection of direction vectors; the normal vector of 
    a surface is also acceptable, and the angles will be recalculated correspondingly.
    """
    # get the table of dir vectors. 
    direction = np.array(direction) - normal + np.array([0,0,1])
    if (len(direction.shape)!=2) or (direction.shape[1]!=3):
        raise Exception("invalid direction input!")
    
    # the mesh grid of angles
    step = 0.01
    theta = np.arange(0+step/2, np.pi/2, step)
    phi = np.arange(0+step/2, 2*np.pi, step)
    plot = np.zeros((len(theta), len(phi)), dtype=bool)
    thres = np.cos(5/180*np.pi)

    # paint
    for i in range(len(theta)):
        for j in range(len(phi)):
            vec = unit_vector(theta[i], phi[j])
            for k in range(len(direction)):
                if np.inner(vec, direction[k])>thres:
                    plot[i][j] = True
                    break
    
    return plot

def recognize_photon(Photon):
    """
    from input Photon, - find out which ref it hits
    - binning in position(mul) and direction (θ, φ)
    will return 3 arrays, mul, theta and phi
    theta and phi will be 10000 bins
    """
    pos = 0
