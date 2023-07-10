import numpy as np
import scipy.sparse as sp
from classify import recognize_array, indexing_array
from mathematics import get_cylindrical_array, get_angles_array
import matplotlib.pyplot as plt

"""A test file for position painting. The painting method is no longer used now."""

mul = np.load('mul_list.npy')
index_select = np.random.choice(mul)

# recognize the ref.pos, find all that falls in index
# plot the points in scatter (anguler)
ref_pos = np.load('reflector_position.npy')
ref_dir = np.load('reflector_direction.npy')
pos_cy = get_cylindrical_array(ref_pos)
refnum = recognize_array(pos_cy)
index = indexing_array(pos_cy, refnum)
t, f = get_angles_array(ref_dir)
theta = []
phi = []
for i in range(len(pos_cy)):
    if (index[i] == index_select):
        theta.append(t[i])
        phi.append(f[i])

plt.scatter(theta,phi,s=1, alpha=0.7, color='r')
plt.xlim([0,np.pi])
plt.ylim([0,np.pi*2])

# load the plot and matrix_of_angle, plot it in scatter
plot_load = sp.load_npz('plot.npz').toarray()
plot_v1 = plot_load[index_select]
mat_of_angle = np.load('mat_of_angle.npy')
dir_list = []
for i in range(len(plot_v1)):
    if plot_v1[i]:
        dir_list.append(mat_of_angle[i])
theta,phi = get_angles_array(dir_list)
plt.scatter(theta,phi,s=1, alpha=0.7, color='b')

# generate photons from source.py, plot it in scatter
index_array = np.arange(np.shape(plot_load)[1])
plot_v2 = (plot_load[index_select]*index_array)
plt_real = plot_v2[np.nonzero(plot_v2)]
ang_select = np.random.choice(plt_real, 10)
dir_take = np.take(mat_of_angle, ang_select, axis=0)
theta,phi = get_angles_array(dir_take)
plt.scatter(theta,phi,s=1, alpha=0.7, color='g')
plt.savefig('Paint.png')
plt.show()