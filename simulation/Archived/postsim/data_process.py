import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import sys
import datetime
from mpl_toolkits.mplot3d import Axes3D

"""
This file is used for data i/o and satisfying different types of processing
use code number for specific functions. 
Try hexadecimal - or binary - code: The functions of analysis code is controlled by
the input hexadecimal number, every digit represents answer to such questions: 
- Info (True) / Running (False)? 
- Verbose (True) / Silent (False)?
- Conduct recoordination of camera view? 
- Saving to histogram (True) / scatter point (False)? 
- Turning to cylindrical coord. (True) / cartesian (False)? 
For example, the illumination map process code - saving a cylindrical histogram - is hex(0011)=3. 
For any code>7, pump out information and terminate it. Be careful about negative numbers!
"""

def rotation_matrix(thetax,thetay,thetaz):
    #the 3d rotation matrix in spherical coord., for simplicity in adding solids
    #the algorithm chroma uses: inner product(vertice, rot) + pos
    rx = np.array([[1,0,0], [0,np.cos(thetax),-1*np.sin(thetax)], [0,np.sin(thetax),np.cos(thetax)]])
    ry = np.array([[np.cos(thetay),0,np.sin(thetay)], [0,1,0], [-1*np.sin(thetay),0,np.cos(thetay)]])
    rz = np.array([[np.cos(thetaz),-1*np.sin(thetaz),0], [np.sin(thetaz),np.cos(thetaz),0], [0,0,1]])
    m = np.dot(np.dot(rx, ry), rz)
    return m

def recoordinate(Row):
    # generates a new 3d tuple with proper coordinates, for optical analysis
    # focal point at (0,0,z0)
    pos = Row[0]
    dir = Row[1]
    z0 = 0.0184 / np.tan(84.1/180*np.pi) # back "focal" point of lens
    origin = np.array([0.11545,0,0.21560]) + np.array([0,0,0.22225]) # the center of lens
    focal = np.array([0,0,z0])
    pos_rel = pos - origin #relative position
    iris = 0.00165 / 2.8 /2
    index_delete = []
    for i in range(len(pos_rel)):
        if np.dot(pos_rel,pos_rel) > (iris*iris):
            index_delete.append(i)
    rotation = rotation_matrix(22.5/180*np.pi,0,0) # rotate along x axis so the optical axis is z
    pos_rel = np.dot(pos_rel,rotation) - focal #relative to focal point
    dir_rel = np.dot(dir,rotation)
    pos_rel = np.delete(pos_rel, index_delete, 0) # filter out by the iris
    dir_rel = np.delete(dir_rel, index_delete, 0)
    return [pos_rel, dir_rel]

def repropagate_plane(Row):
    # given the position and direction of ONE photon, find the point on focal plane
    pos = Row[0]
    dir = Row[1]
    f = 0.0016
    l = -1*abs(f/dir[2])
    end = dir * l + pos
    return end

def repropagate_sphere(Row):
    # given inital position, find the spherical coordinates theta, phi
    pos = Row[0]
    dir = Row[1]
    pos_new = pos
    R = 0.300
    while np.dot(pos_new,pos_new) < R:
        pos_new = pos_new - dir * 0.001
    x,y,z = pos_new[:]
    theta = np.arctan(np.sqrt(x*x+y*y)/abs(z))
    phi = np.arctan(abs(y)/abs(x))
    return theta, phi

def projection(points):
    # given a tuple of points on focal plane, get the ones on image plane
    # only x, y coordinates are preserved
    m_proj = np.array([[-2,0,0],[0,-2,0],[0,0,1]])
    p = np.dot(points, m_proj)
    x = np.transpose(p)[0]
    y = np.transpose(p)[1]
    return np.transpose([x,y])

def equidistant_projection(theta, phi):
    # the function of Fisheye lens
    i0 = 400
    j0 = 600
    p = 0.000003
    f = 0.00165
    i = i0 + int(f*theta / p *np.cos(phi))
    j = j0 + int(f*theta / p *np.sin(phi))
    return np.array([i,j])

def to_cylindrical(Row):
    # from original cartesian coordinate to cylindrical coordinate
    x = Row[0]
    y = Row[1]
    z = Row[2]
    r = np.sqrt(x*x+y*y)
    if x==0:
        phi = np.pi/2
    else:
        phi = np.arctan(y/x)
    return np.array([z, r, phi])

if __name__ == '__main__':
    # name dependent on the time of running
    namestr = str(datetime.datetime.now())
    ti = datetime.datetime.now()
    if len(sys.argv)==1:
        raise Exception("Please enter a filename! ")
    else:
        filename = sys.argv[1]
    if (len(sys.argv)<3):
        code = 8
    else:
        code = int(sys.argv[2], 16) # accepts hexodecimal input

    if (code>15):
        print("================Information mode=================")
        print("Please enter a valid hexadecimal number as process code. ")
        print("Each digit represents meaning as such:")
        print("Info (True) / Running (False)")
        print("Verbose (True) / Silent (False)")
        print("Recoordination--camera (True) / Normal (False)") 
        print("Histogram (True) / Scatter point (False)")
        print("Cylindrical (True) / Cartesian (False)")
        print("For detailed information, view comments of this file.")
        sys.exit(0)

    verbose = code & 8
    # load data from input filename
    data = np.empty([0,3], dtype=float) # subject to change - may not be positions
    df = pd.read_csv(filename, usecols=[1,2,3], dtype=float) # Reading rows. 

    # Turn rows to points
    perc = 0.0
    buffer = []
    for i in range(len(df)):
        point = np.array(df.loc[i])
        if (code & 1):
            point = to_cylindrical(point)
        if (code & 4):
            point = equidistant_projection(repropagate_plane(recoordinate(point))) # this line is dangerous and needs review
        buffer.append(point)
        percp = float(i)/len(df) *100
        if (verbose):
            if (int(percp*100) > perc*100):
                perc = percp
                print("Reading data ...... %.2f %% ......" % perc)
    buffer = np.transpose(np.array(buffer))
    # Now extract every line of buffer, for cylindrical, it is z,r,phi
    x, y, z = buffer[:]

    if (code & 2):
        # histogram
        plt.hist2d(x, y, bins=50, cmap='gray', norm = mpl.colors.LogNorm())
        cb = plt.colorbar()
        plt.savefig(filename + '_xy_hist.png')
        plt.cla()
        cb.remove()
        plt.hist2d(x, z, bins=50, cmap='gray', norm = mpl.colors.LogNorm())
        cb = plt.colorbar()
        plt.savefig(filename + '_xz_hist.png')
        plt.cla()
        cb.remove()
        plt.hist2d(y, z, bins=50, cmap='gray', norm = mpl.colors.LogNorm())
        cb = plt.colorbar()
        plt.savefig(filename + '_yz_hist.png')
        plt.cla()
        cb.remove()
    else:
        # scatter point plot
        plt.scatter(x,y, alpha=0.01)
        plt.savefig(filename + '_xy_scatter.png')
        plt.cla()
        plt.scatter(x,z, alpha=0.01)
        plt.savefig(filename + '_xz_scatter.png')
        plt.cla()
        plt.scatter(y,z, alpha=0.01)
        plt.savefig(filename + '_yz_scatter.png')
        plt.cla()
        # 3D scatter - considered unimportant and aborted
        """
        fig=plt.figure()
        ax=Axes3D(fig)
        ax.scatter(x,y,z, alpha=0.01)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        plt.savefig(filename + '_xyz_scatter.png')
        plt.show()
        """

    tf = datetime.datetime.now()
    dt = tf - ti
    print("The total time cost: ")
    print(dt)