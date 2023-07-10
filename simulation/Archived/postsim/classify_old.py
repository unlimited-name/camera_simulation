import numpy as np
from mathematics import get_cylindrical, rotation_matrix, get_angles, unit_vector
import datetime
import random
import matplotlib.pyplot as plt

"""
Merged with binning and indexing functions, now this is a file aiming at
photon processing including classifying them and draw the angular
"plots" for camera-reflector matching job.


==============================update===============================

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

# the mesh grid of angles. They are fixed in this file.
step_angle = 0.03
theta = np.arange(0+step_angle/2, np.pi, step_angle) # the center values of theta bins
phi = np.arange(0+step_angle/2, 2*np.pi, step_angle)
l_t = len(theta)
l_p = len(phi) # length of theta, phi table = number of intervals divided

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

def angular_paint(direction):
    """
    using input vectors of direction, "paint" on θ-φ plot. each input point will 
    have a "paint distance" of 1 degree; screening along θ-φ, and determine if 
    a pixel is painted.

    the input should be a collection of direction vectors; the normal vector of 
    a surface is also acceptable, and the angles will be recalculated correspondingly.
    returned "plot" is an array corresponding to θ-φ grid, with Boolean datatype.
    """
    # get the table of dir vectors. 
    direction = np.array(direction)
    
    plot = np.zeros(l_t*l_p, dtype=bool)
    thres = np.cos(1/180*np.pi) # distinguish 1 degree

    # paint
    for i in range(l_t):
        for j in range(l_p):
            vec = unit_vector(theta[i], phi[j])
            if np.inner(vec, direction)>thres:
                plot[i*l_p+j] = True

    return plot
    # A 1-d Boolean array - easy to read and write; 
    # for further analysis, use .reshape(l_t,l_p)

def interval_comparison(data, intervals):
    # should check intervals first. But, we are using it manually,
    # for the sake of efficiency, lets make sure the intervals are correct before using.
    # actually, no longer used - can be easily replaced by numpy.histogram
    for i in range(len(intervals)-1):
        if (data>=intervals[i]) and (data<intervals[i+1]):
            return i

def quick_binning(data, minimum):
    """
    An illustrative function, showing the algorithm of position binning
    We have a fixed range of position vectors, so adjusting our bin edges
    to bin them in a faster way should be ok:
    Use the digits of data itself to get and return an "index" number.
    """
    # DO NOT USE IT BEFORE MODIFYING
    # ONLY ILLUSTRATIVE
    xbins = 100
    ybins = 100
    mul = np.zeros(xbins*ybins, dtype=int)
    for i in range(len(data)):
        index = int((data[i]-minimum)*1000)
        mul[index] += 1
    return mul


if __name__ == '__main__':

    ti = datetime.datetime.now()
    
    pos_data = np.load('camera_position.npy')
    pos_data = pos_data[range(int(len(pos_data)/1000))]
    dir_data = np.load('camera_direction.npy')
    dir_data = dir_data[range(int(len(dir_data)/1000))]
    print('Length of datasheet:')
    print(len(pos_data))

    min1 = 0
    max1 = 0.1
    len1 = int((max1-min1)*100)
    print(len1)
    min2 = 0
    max2 = 0.34
    len2 = int((max2-min2)*100)
    print(len2)
    min3 = 0.2
    max3 = 0.34
    len3 = int((max3-min3)*100)
    print(len3)
    min4 = 0
    max4 = 0.15
    len4 = int((max4-min4)*100)
    print(len4)
    # The grouped area's position range (for z or r)
    # the coefficient in int() may be tuned outside (but it should be 10 times' number)
    # for our use, take 1mm level resolution

    phi_range = np.arange(0, 2*np.pi, 0.03)
    lenp = len(phi_range)
    print(lenp)

    mul1 = np.zeros(len1*lenp,dtype=int)
    print(len(mul1))
    mul2 = np.zeros(len2*lenp,dtype=int)
    mul3 = np.zeros(len3*lenp,dtype=int)
    mul4 = np.zeros(len4*lenp,dtype=int)
    # For a length_of_x by length_of_phi array, each row means different phi with same x
    # Also flattened, making it easier for r/w
    # to 'plot' it, use mul.reshape(len1,lenp); mul[x][phi] should be the wanted multiplicity.
    # A good reference may be numpy.histogram2d - we have similar output

    plot1 = np.zeros((len1*lenp, l_t*l_p), dtype=bool)
    plot2 = np.zeros((len2*lenp, l_t*l_p), dtype=bool)
    plot3 = np.zeros((len3*lenp, l_t*l_p), dtype=bool)
    plot4 = np.zeros((len4*lenp, l_t*l_p), dtype=bool)
    # Similar with multiplicity, we have a 2d array for angular paint
    # the first indice points to a flattened array of 'plot'
    # thus the first index should be the same with that in 'multiplicity'
    # for index algorithm, may refer to quick_binning() for details
    
    t1 = datetime.datetime.now()
    t1 = t1-t1
    t2 = t1
    for iter in range(len(pos_data)):
        tt0 = datetime.datetime.now()
        pos = pos_data[iter]
        dir = dir_data[iter]
        refnum = recognize(pos)
        z,r,p = get_cylindrical(pos)
        tt1 = datetime.datetime.now()
        # add to mul bins depending on the refnum
        if refnum==0 or refnum==1:
            index = int((r-min1)*100)*lenp + int(p/0.03)
            mul1[index] += 1
            plot1[index] += angular_paint(dir)
            tt2 = datetime.datetime.now()
        elif refnum==2:
            index = int((z-min2)*100)*lenp + int(p/0.03)
            mul2[index] += 1
            plot2[index] += angular_paint(dir)
            tt2 = datetime.datetime.now()
        elif refnum>2 and refnum<11:
            index = int((z-min3)*100)*lenp + int(p/0.03)
            mul3[index] += 1
            plot3[index] += angular_paint(dir)
            tt2 = datetime.datetime.now()
        elif refnum>=11 and refnum<14:
            index = int((r-min4)*100)*lenp + int(p/0.03)
            mul4[index] += 1
            plot4[index] += angular_paint(dir)
            tt2 = datetime.datetime.now()
        else:
            tt2 = datetime.timedelta(0)
        t1 += (tt1-tt0)
        t2 += (tt2-tt1)
    
    print('The process time:')
    print(t1)
    print(t2)

    # save these arrays
    np.save('classfied_mul1', mul1)
    np.save('classfied_mul2', mul2)
    np.save('classfied_mul3', mul3)
    np.save('classfied_mul4', mul4)
    np.save('classfied_plot1', plot1)
    np.save('classfied_plot2', plot2)
    np.save('classfied_plot3', plot3)
    np.save('classfied_plot4', plot4)
    """
    # generate a random plot, and plot it
    theta_rand = []
    phi_rand = []
    for i in range(20):
        theta_rand.append(random.random() * np.pi)
        phi_rand.append(random.random() * np.pi *2)

    plt.scatter(theta_rand,phi_rand,s=0.5)
    plt.savefig('ori.png')

    plot = np.zeros(l_t*l_p, dtype=bool)
    thres = np.cos(1/180*np.pi) # distinguish 1 degree

    # paint
    for i in range(l_t):
        for j in range(l_p):
            vec = unit_vector(theta[i], phi[j])
            for k in range(len(theta_rand)):
                if np.inner(vec, unit_vector(theta_rand[k], phi_rand[k]))>thres:
                    plot[i*l_p+j] = True
                    break

    plot = plot.reshape(l_t,l_p)
    theta_p = []
    phi_p = []
    for i in range(l_t):
        for j in range(l_p):
            if plot[i][j]:
                theta_p.append(theta[i])
                phi_p.append(phi[j])
    
    plt.scatter(theta_p,phi_p,s=0.5)
    plt.savefig('paint.png')
    """
    tf = datetime.datetime.now()
    dt = tf - ti
    print(l_p*l_t)
    print("The total time cost: ")
    print(dt)