import random
import numpy as np

"""
The math tools are all saved here. 
"""

def rotation_matrix(thetax,thetay,thetaz):
    """
    The 3d rotation matrix in spherical coord., for simplicity in adding solids
    note: the algorithm chroma uses: inner product(vertice, rot) + pos

    This function is tested and proved correct using Jupyter, at least in terms of x-z axis rotation.
    The rotation operated for each axis is clock-wise (if positive angle, and vice versa)
    The order of rotation is applied in Rot(x)->Rot(y)->Rot(z). Use np.dot(vector, Rotation) for correct functioning.
    Notice in chroma/geometry/Solid the add_geometry() use np.inner() - 
    This is also tested, it is not functioning properly. 
    Our version of rotation is recommended, since we can easily realize any rotation we want --
    The rotation function chroma has is dumb. 
    """
    rx = np.array([[1,0,0], [0,np.cos(thetax),-1*np.sin(thetax)], [0,np.sin(thetax),np.cos(thetax)]])
    ry = np.array([[np.cos(thetay),0,np.sin(thetay)], [0,1,0], [-1*np.sin(thetay),0,np.cos(thetay)]])
    rz = np.array([[np.cos(thetaz),-1*np.sin(thetaz),0], [np.sin(thetaz),np.cos(thetaz),0], [0,0,1]])
    m = np.dot(np.dot(rx, ry), rz)
    return m

def get_angles(vector):
    # calculate the spherical angles of a vector
    if vector[1]==0 and vector[0]==0:
        return 0,0

    if vector[2]==0:
        theta = np.pi /2
    else:
        theta = np.arctan(np.sqrt(vector[0]*vector[0]+vector[1]*vector[1])/vector[2])
    if theta<0 :
        theta += np.pi

    if (vector[0]==0) and (vector[1]>0):
        phi = np.pi/2
    elif (vector[0]==0) and (vector[1]<0):
        phi = -np.pi/2
    else: 
        phi = np.arctan(vector[1]/vector[0])
    if phi<0:
        phi += np.pi
    
    # there are actually two possible phi ... depending on the sqrt +/-
    # check it 
    if vector[1]==0:
        if vector[0]<0:
            phi += np.pi
    elif (np.sin(theta) * np.sin(phi) / vector[1]) < 0:
        # this means sin(phi) is actually < 0
        phi += np.pi
    return theta, phi

def get_angles_array(vector_array):
    x,y,z = np.transpose(vector_array)[:]
    r = np.sqrt(x*x+y*y)
    length = len(r)
    theta = np.zeros(length)
    phi = np.zeros(length)

    # if r=0, theta can be 0/pi; if z=0, theta is pi/2
    zeros = np.where(r==0)
    if (zeros[0].size>0):
        theta_upright = np.sign(z[zeros]) * (-np.pi/2) + np.pi/2
        theta[zeros] += theta_upright
    zeros = np.where(z==0)
    if (zeros[0].size>0):
        theta[zeros] += np.pi/2
    
    nonzero = np.where(z!=0)
    theta[nonzero] += np.arctan(r[nonzero]/z[nonzero])
    theta[np.where(theta<0)] += np.pi

    # now consider phi
    # select all the x=0 points: they have +/-pi/2
    zeros = np.where(x==0)
    if (zeros[0].size>0):
        phi_upright = np.sign(y[zeros]) * np.pi/2
        phi[zeros] += phi_upright

    nonzero = np.where(x!=0)
    phi[nonzero] += np.arctan(y[nonzero]/x[nonzero])
    phi[np.where(phi<0)] += np.pi
    # the problem here is, arctan() returns 1/4th quardrant, now converted to 1-2nd quard
    # distinguished by y value, but remember to discuss at y=0
    # for y=0 (x axis), phi can be 0 and pi, but above will only return 0
    axis = np.where(y==0)
    phi[axis] += np.sign(x[axis])* (-np.pi/2) + np.pi/2
    phi[np.where(y<0)] += np.pi

    # did not take care about x=y=0: they are simply 0
    phi[np.where(r==0)] = 0

    return theta,phi

def random_vector_2d():
    # generate a random unit point on x-y plane
    theta = 2*np.pi * random.random()
    x = np.cos(theta)
    y = np.sin(theta)
    return np.array([x,y,0])

def random_vector():
    # a copy of uniform_sphere, but return one vec at a time
    u = random.random()*2-1 # actually, cos(theta)
    phi = random.random() * 2*np.pi
    c = np.sqrt(1-u*u)
    return np.array([c*np.cos(phi), c*np.sin(phi), u])

def random_vector_half():
    # generate a random vector with theta restricted in [0, pi/2]
    u = random.random()
    phi = random.random() * 2*np.pi
    # used to add phi_restrict also, but seems not necessary
    c = np.sqrt(1-u*u)
    return np.array([c*np.cos(phi), c*np.sin(phi), u])

def random_vector_list(datalist):
    """
    generate a unit vector with specific [θ,phi] distribution.
    realized through picking a cos(θ) from datalist file. 
    The datalist is saved and loaded by np.save and np.load
    """
    # u = cos is picked from file
    # u = np.random.uniform(0.0, 1.0)
    u = random.choice(datalist)
    phi = random.random() * 2*np.pi
    c = np.sqrt(1-u*u)
    return np.array([c*np.cos(phi), c*np.sin(phi), u])

def random_vector_cosine():
    """
    generate a random vector obeying "cosine emission law"
    for random vector pick, cos(θ) is evenly distributed;
    but for cosine law emission, P(cosθ)~cosθ, θ in [0,pi/2]
    """
    x = 0
    y = 1
    while(x < y):
        x = random.random()
        y = random.random()
    phi = random.random()*2*np.pi
    c = np.sqrt(1-x*x)
    return np.array([c*np.cos(phi), c*np.sin(phi), x])

def uniform_sphere(size=None, dtype=np.double):

    theta, u = np.random.uniform(0.0, 2*np.pi, size), \
        np.random.uniform(-1.0, 1.0, size)

    c = np.sqrt(1-u**2)

    if size is None:
        return np.array([c*np.cos(theta), c*np.sin(theta), u])

    points = np.empty((size, 3), dtype)

    points[:,0] = c*np.cos(theta)
    points[:,1] = c*np.sin(theta)
    points[:,2] = u

    return points

def normalize(vector):
    """
    Normalize a vector. 
    """
    vector = np.array(vector)
    if (vector.ndim != 1):
        raise Exception("Invalid input vector for normalization!")
    if (len(vector) != 3):
        raise Exception("You are normalizing a non-3d vector!")
    norm = np.linalg.norm(vector)
    if (norm != 0):
        vnorm = vector / norm
    else: 
        vnorm = np.array([0,0,1]) # null vector.. return a default one.
    return vnorm

def generate_circle(r, number):
    points = []
    for i in range(number):
        x = 1
        y = 1
        while (x*x+y*y) > 1:
            x = random.random()*2 - 1
            y = random.random()*2 - 1
        points.append([x*r,y*r,0])
    return np.array(points)

def get_cylindrical(Row):
    x,y,z = Row[:]
    r = np.sqrt(x*x+y*y)
    if r==0:
        return np.array([z,r,0])
    
    if (x==0) and (y>0):
        phi = np.pi/2
    elif (x==0) and (y<0):
        phi = -np.pi/2
    else:
        phi = np.arctan(y/x)
    if phi<0:
        phi += np.pi
    # now phi belong to [0, pi]
    
    if y==0:
        if x<0:
            phi += np.pi
    elif y<0:
        phi += np.pi

    return z,r,phi

def get_cylindrical_array(pos_array):
    x,y,z = np.transpose(pos_array)[:]
    r = np.sqrt(x*x+y*y)
    length = len(r)
    phi = np.zeros(length)
    
    # select all the x=0 points: they have +/-pi/2
    zeros = np.where(x==0)
    if (zeros[0].size>0):
        phi_upright = np.sign(y[zeros]) * np.pi/2
        phi[zeros] += phi_upright

    nonzero = np.where(x!=0)
    phi[nonzero] += np.arctan(y[nonzero]/x[nonzero])
    phi[np.where(phi<0)] += np.pi
    # the problem here is, arctan() returns 1/4th quardrant, now converted to 1-2nd quard
    # distinguished by y value, but remember to discuss at y=0
    # for y=0 (x axis), phi can be 0 and pi, but above will only return 0
    axis = np.where(y==0)
    phi[axis] += np.sign(x[axis])* (-np.pi/2) + np.pi/2
    phi[np.where(y<0)] += np.pi

    # did not take care about x=y=0: they are simply 0
    phi[np.where(r==0)] = 0

    return np.transpose(np.array([z,r,phi]))

def unit_vector(theta, phi):
    # generate a unit vector for given angles
    # update: overloaded for arrays of angles
    x = np.sin(theta) * np.cos(phi)
    y = np.sin(theta) * np.sin(phi)
    z = np.cos(theta)
    if isinstance(x, np.ndarray):
        return np.transpose(np.array([x,y,z]))
    else:
        return np.array([x,y,z])

def check_if_normalized(array):
    sum = np.sum(array*array, axis=1) - 1
    ab = abs(sum)
    length = len(ab)
    dev = 0.0001
    cal = np.piecewise(ab, [ab>=0, ab>=dev], [0,1])
    lendev = len(np.nonzero(cal)[0])
    print('The total length of data:')
    print(length)
    print('The number of un-normalized vectors:')
    print(lendev)
    return lendev

def cosine_similarity(array1, array2, threshold = 0.99):
    # return the result of cosine sim judge. posdir is the result of cam-ref simulation,
    # target is the generated photon pos-dir vector. 
    if (array1.shape != array2.shape):
        raise Exception('Different shape between arrays!')
    
    sim = np.sum(array1*array2, axis=1)/np.sqrt(np.sum(array1*array1, axis=1)*np.sum(array2*array2, axis=1))
    #print('Cosine value:')
    #print(sim)
    judge = np.piecewise(sim, [sim>=threshold, sim<threshold], [True, False])
    return judge.astype(bool)