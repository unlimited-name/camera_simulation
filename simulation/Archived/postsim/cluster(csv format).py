import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import datetime
import random
from recognize import recognize, angular_paint
from mathematics import get_angles, unit_vector, rotation_matrix

"""
A test file to check the effect of angular painting
"""

if __name__ == '__main__':
    # read pos and dir, plot dir(θφ) scatter and hist (5 sets.)
    ti = datetime.datetime.now()
    filename = "refnum"
    # load data from input filename
    df_pos = pd.read_csv('camera_position.csv', usecols=[1,2,3], dtype=float)
    length = int(df_pos.size/2)
    df_dir = pd.read_csv('camera_direction.csv', usecols=[1,2,3], dtype=float)
    
    # now pick a random point on particular part
    i = int(random.random()*length)
    refnum = 0
    filename += str(refnum)
    while recognize(df_pos.loc[i])!=refnum:
        i = int(random.random()*length)
    pos_i = np.array(df_pos.loc[i])
    print("The refnum is: ")
    print(recognize(pos_i))

    # find out the corresponding dir near the selected point. 
    theta = []
    phi = []
    for i in range(length):
        pos = np.array(df_pos.loc[i])
        dist = abs(pos-pos_i)
        if (dist[0]<0.001) and (dist[1]<0.001) and (dist[2]<0.001):
            t,f = get_angles(df_dir.loc[i])
            theta.append(t)
            phi.append(f)

    data = np.transpose(np.array(theta,phi))
    np.savetxt('data.txt',data)
    # scatter point plot
    fig = plt.figure()
    ax = plt.axes()
    ax.set_xlabel('θ')
    ax.set_xlim(0, np.pi)
    ax.set_ylabel('φ')
    ax.set_ylim(0, np.pi*2)
    ax.scatter(theta,phi, s=0.5, alpha=1)
    fig.savefig(filename + '_scatter.png')

    # test of angular painting
    dire = []
    for i in range(len(theta)):
        dire.append(unit_vector(theta[i],phi[i]))
    paint = angular_paint(dire)
    step = 0.001
    theta_m = np.arange(0+step/2, np.pi/2, step)
    phi_m = np.arange(0+step/2, 2*np.pi, step)
    t = []
    f = []
    for i in range(len(theta_m)):
        for j in range(len(phi_m)):
            if paint[i][j]:
                t.append(theta_m[i])
                f.append(phi_m[j])
    
    fig = plt.figure()
    ax = plt.axes()
    ax.set_xlabel('θ')
    ax.set_xlim(0, np.pi)
    ax.set_ylabel('φ')
    ax.set_ylim(0, np.pi*2)
    ax.scatter(t,f, s=0.5, alpha=1)
    fig.savefig(filename + '_paint.png')

    tf = datetime.datetime.now()
    dt = tf - ti
    print("The total time cost: ")
    print(dt)
    print("Total number of points: ")
    print(len(theta))
    print("Length of datasheet: ")
    print(length)