import numpy as np
from mathematics import get_cylindrical_array, unit_vector
import time
import random
import matplotlib.pyplot as plt
from scipy.sparse import csr_matrix, vstack, save_npz

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

xstep = 0.002
min = np.array([0., 0., 0., h_oj, 0.])
max = np.array([0., 0.11, h_oj + 0.02, h_distinguish + 0.01, r_threshold + 0.01])
length_x = ((max-min)/xstep +1).astype(int)
length_x[0] = 0
print('length of x bins:')
print(length_x)

pstep = 0.03
phi_range = np.arange(0, 2*np.pi, pstep)
length_p = len(phi_range)
length_xp = np.cumsum(length_x * length_p)
print('length of total bins:')
print(length_xp)

# the mesh grid of angles. They are fixed in this file.
step_angle = 0.03
theta = np.arange(0+step_angle/2, np.pi, step_angle) # the center values of theta bins
phi = np.arange(0+step_angle/2, 2*np.pi, step_angle)
l_t = len(theta)
l_p = len(phi) # length of theta, phi table = number of intervals divided

thres = np.cos(1/180*np.pi) # distinguish 1 degree

matrix_of_angle = []
# paint
for i in range(l_t):
    for j in range(l_p):
        matrix_of_angle.append(unit_vector(theta[i], phi[j]))
matrix_of_angle = np.array(matrix_of_angle)

def recognize_array(position):
    t1 = time.time()
    z,r,p = np.transpose(position)[:]
    length = len(z)
    """
    z_condition = [(z<h_ij+0.001) , ((z>=0) and (z<= h_oj)), ((z>h_oj) and (z<h_distinguish)), ((z>h_distinguish) and (z<h_space))]
    r_condition = [(r<=r_ij_bottom), ((r<r_oj+0.001) and (r>=r_oj-0.001)), (r<r_threshold), (r<r_threshold)]
    encode = [0b0001, 0b0010, 0b0100, 0b1000]"""
    z1 = np.zeros(length)
    r1 = np.zeros(length)
    z2 = np.zeros(length)
    r2 = np.zeros(length)
    z3 = np.zeros(length)
    r3 = np.zeros(length)
    z4 = np.zeros(length)
    r4 = np.zeros(length)

    z1 += np.piecewise(z, [z>=0, z<h_ij+0.001], [0, 0b0001])
    r1 += np.piecewise(r, [r>=0, r<=r_ij_bottom], [0, 0b0001])
    zr1 = z1.astype(int) & r1.astype(int)
    #print(zr1)

    z2 += np.piecewise(z, [z>=0, z<= h_oj], [0, 0b0010])
    r_temp = np.piecewise(r, [r>=0, r<r_oj+0.001], [0, lambda x:x])
    r2 += np.piecewise(r_temp, [r_temp>=0, r_temp>=r_oj-0.001], [0, 0b0010])
    zr2 = z2.astype(int) & r2.astype(int)
    #print(zr2)

    z_temp = np.piecewise(z, [z>=0, z<h_distinguish], [0, lambda x:x])
    z3 += np.piecewise(z_temp, [z_temp>=0, z_temp>h_oj], [0, 0b0100])
    r3 += np.piecewise(r, [r>=0, r<r_threshold], [0, 0b0100])
    zr3 = z3.astype(int) & r3.astype(int)
    #print(zr3)

    z_temp = np.piecewise(z, [z>=0, z<h_space], [0, lambda x:x])
    z4 += np.piecewise(z_temp, [z_temp>=0, z_temp>h_distinguish], [0, 0b1000])
    r4 += np.piecewise(r, [r>=0, r<r_threshold], [0, 0b1000])
    zr4 = z4.astype(int) & r4.astype(int)
    #print(zr4)

    zr = zr1 + zr2 + zr3 + zr4
    refnum = np.piecewise(zr, [zr>0, zr&0b0100, zr&0b1000], [lambda x:x, 3,4])
    t2 = time.time()
    print('Time cost for recognizing:')
    print(t2-t1)
    return refnum

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
    t1 = time.time()
    direction = np.array(direction)

    # if the inner product is bigger than thershold value,
    # it is painted.
    length_slice = 1000
    length_data = len(direction)
    if length_data<=length_slice:
        prod = np.inner(direction, matrix_of_angle)- thres + 1
        #print(prod)
        plot = csr_matrix(prod.astype(int).astype(bool))
        #print(prod.astype(int).astype(bool))
    else:
        num = length_data//length_slice
        res = length_data%length_slice
        plot_list = []
        for i in range(num):
            index = range(i*length_slice, (i+1)*length_slice)
            prod = np.inner(np.take(direction,index,axis=0), matrix_of_angle) - thres + 1
            plot_list.append(csr_matrix(prod.astype(int).astype(bool)))
        index = range(num*length_slice, num*length_slice+res)
        prod = np.inner(np.take(direction,index,axis=0), matrix_of_angle) - thres + 1
        plot_list.append(csr_matrix(prod.astype(int).astype(bool)))
        plot = vstack(plot_list, format='csr')

    t2 = time.time()
    print('Time cost for painting:')
    print(t2-t1)
    return plot
    # A 2-d Boolean array - easy to read and write; 
    # plot[index] is the list of 'angular paint' results

def indexing_array(position, refnum):
    """
    Given the position and refnum array, return an index array
    """
    t1 = time.time()
    z,r,p = np.transpose(position)[:]
    z[np.where(refnum==1)] = r[np.where(refnum==1)]
    z[np.where(refnum==4)] = r[np.where(refnum==4)]
    index = ((z - min[refnum])/xstep).astype(int) * length_p + (p/pstep).astype(int) + length_xp[refnum-1]
    index[np.where(refnum==0)] = 0
    t2 = time.time()
    print('Time cost for indexing:')
    print(t2-t1)
    print('The minimum index:')
    print(index.min())
    print('The maximum index:')
    print(index.max())
    
    return index

def organize(index, plot):
    t1 = time.time()

    mul = np.zeros(length_xp[4]).astype(int)
    bpl = np.zeros(length_xp[4]*l_t*l_p).astype(bool).reshape(length_xp[4], l_t*l_p)
    for i in range(len(index)):
        if index[i]:
            mul[index[i]] += 1
            bpl[index[i]] += plot[i]
    t2 = time.time()
    print('Time cost for organizing:')
    print(t2-t1)
    
    return mul,bpl

def make_pos_list(pos_cy, index):
    t1 = time.time()
    # from pos_cylinder and index, generate a file aiming at
    # func(index) -> pos
    # the inverse func of recognize()
    pos_sum = np.zeros((length_xp[4],3), dtype=float)
    # summed position vector for indexed position
    pos_mul = np.zeros(length_xp[4])
    # multiplicity for indexed position
    for i in range(len(pos_cy)):
        if index[i]:
            pos_sum[index[i]] += pos_cy[i]
            pos_mul[index[i]] += 1
    
    for i in range(len(pos_mul)):
        if pos_mul[i]:
            pos_sum[i] = pos_sum[i]/pos_mul[i]

    t2 = time.time()
    print('Time cost for pos_list:')
    print(t2-t1)
    return pos_sum

def make_plot(plot, length=50000):
    index = int(random.random()*length)
    plot = plot[index].reshape(l_t,l_p)
    theta_p = []
    phi_p = []
    for i in range(l_t):
        for j in range(l_p):
            if plot[i][j]:
                theta_p.append(np.take(theta,i))
                phi_p.append(np.take(phi,j))
    
    plt.scatter(theta_p,phi_p)
    plt.savefig('paint_'+str(index))
    return

if __name__ == '__main__':

    ti = time.time()
    
    pos_data = np.load('reflector_position.npy')
    pos_data = pos_data[range(100000)]
    dir_data = np.load('reflector_direction.npy')
    dir_data = dir_data[range(100000)]
    print('Length of datasheet:')
    print(len(pos_data))

    pos_cy = get_cylindrical_array(pos_data)
    refnum = recognize_array(pos_cy)
    index = indexing_array(pos_cy, refnum)
    np.save('pos_list', make_pos_list(pos_cy, index))

    np.save('mat_of_angle', matrix_of_angle)
    plot = angular_paint(dir_data)
    mul, plot = organize(index, plot.toarray())
    """
    for i in range(5):
       make_plot(plot)"""
    plot = csr_matrix(plot, dtype=bool)

    np.save('mul', mul)
    save_npz('plot.npz', plot)
    # save numpy files for reference

    t1 = time.time()
    mul_list = []
    mul = mul.tolist()
    for ind in range(len(mul)):
        num = mul[ind]
        mul_list.append(np.repeat(ind,num))
    np.save('mul_list', np.concatenate(mul_list))
    t2 = time.time()
    print('Time cost to make mul_list:')
    print(t2-t1)

    tf = time.time()
    dt = tf - ti
    print("The total time cost: ")
    print(dt)

