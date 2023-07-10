import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from mathematics import get_cylindrical

filename = 'cam.npy'
data = np.load(filename, allow_pickle=True)
a=np.arange(10)
data = data[a]
# data[i] is a Photon.pos - 2D np array
# plot these points as dotted line
"""
fig = plt.figure()
ax = plt.axes(projection='3d')
for pos in data:
    x,y,z = np.transpose(pos)[:]
    ax.plot(x,y,z)
    ax.scatter(x,y,z,s=5)

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
fig.savefig(filename+'_plot.png',facecolor='w')
"""

# Plot a y-z section view then
fig = plt.figure(figsize=(6,6))
ax = plt.axes()
ax.set_xlim(-0.2,0.2)
ax.set_ylim(0,0.5)
for pos in data:
    x,y,z = np.transpose(pos)[:]
    ax.plot(y,z)
    ax.scatter(y,z,s=5)
    
ax.set_xlabel('y')
ax.set_ylabel('z')
fig.savefig(filename+'_2d.png',facecolor='w')

# turn cartesian to cylindrical, plot r-z
fig = plt.figure(figsize=(6,6))
ax = plt.axes()
ax.set_xlim(0,0.2)
ax.set_ylim(0,0.4)
for pos in data:
    R = []
    Z = []
    for row in pos:
        z,r,phi = get_cylindrical(row)
        ax.scatter(r,z,s=5)
        R.append(r)
        Z.append(z)
    ax.plot(R,Z)
ax.set_ylabel('r')
ax.set_ylabel('z')
fig.savefig(filename+'_rz.png',facecolor='w')