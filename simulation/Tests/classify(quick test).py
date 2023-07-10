import numpy as np
from mathematics import get_cylindrical_array, unit_vector
import time
import random

""" This file is used to test the status of simulated position and direction data, 
such as the ratio of photons hitting inner jar reflector - just for inspection
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

xstep = 0.01
min = np.array([0., 0., 0., h_oj, 0.])
max = np.array([0., 0.11, h_oj + 0.02, h_distinguish + 0.01, r_threshold + 0.01])
length_x = ((max-min)/xstep +1).astype(int)
length_x[0] = 0

pstep = 0.03
phi_range = np.arange(0, 2*np.pi, pstep)
length_p = len(phi_range)
length_xp = np.cumsum(length_x * length_p)
#print(length_xp)

# the mesh grid of angles. They are fixed in this file.
step_angle = 0.03
theta = np.arange(0+step_angle/2, np.pi, step_angle) # the center values of theta bins
phi = np.arange(0+step_angle/2, 2*np.pi, step_angle)
l_t = len(theta)
l_p = len(phi) # length of theta, phi table = number of intervals divided

thres = np.cos(2/180*np.pi) # distinguish 1 degree

matrix_of_angle = []
# paint
for i in range(l_t):
    for j in range(l_p):
        matrix_of_angle.append(unit_vector(theta[i], phi[j]))
matrix_of_angle = np.array(matrix_of_angle)

def recognize_array(position):
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
    #print('Refnum:')
    #print(refnum)
    return refnum

def indexing_array(position, refnum):
    """
    Given the position and refnum array, return an index array
    """
    z,r,p = np.transpose(position)[:]
    z[np.where(refnum==1)] = r[np.where(refnum==1)]
    z[np.where(refnum==4)] = r[np.where(refnum==4)]
    index = ((z - min[refnum-1])/xstep).astype(int) * length_p + (p/pstep).astype(int) + length_xp[refnum-1]
    index[np.where(refnum==0)] = 0

    print('Index:')
    print(index)
    return index

def make_pos_list(pos_cy, index):
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

    print('make_pos_list:')
    print(pos_sum)
    return pos_sum

if __name__ == '__main__':
    ti = time.time()

    pos_data = np.load('camera_position.npy')
    pos_data = pos_data[range(20)]
    dir_data = np.load('camera_direction.npy')
    dir_data = dir_data[range(20)]

    pos_cy = get_cylindrical_array(pos_data)
    refnum = recognize_array(pos_cy)
    index = indexing_array(pos_cy, refnum)
    pl = make_pos_list(pos_cy, index)

    print('matrix of angle:')
    print(matrix_of_angle)