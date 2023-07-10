import numpy as np
import datetime
from classify import recognize
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

# simple lines to print the ranges of position vec
ti = datetime.datetime.now()
pos = np.load('camera_position.npy')
data1y = []
data2y = []
data3y = []
data4y = []
data1x = []
data2x = []
data3x = []
data4x = []
for row in pos:
    if recognize(row)==0 or recognize(row)==1:
        z,r,phi = get_cylindrical(row)
        data1x.append(r) # ij, r-phi
        data1y.append(phi)
    elif recognize(row)==2:
        z,r,phi = get_cylindrical(row)
        data2x.append(z) # oj, z-phi
        data2y.append(phi)
    elif recognize(row)>2 and recognize(row)<11:
        z,r,phi = get_cylindrical(row)
        data3x.append(z) # head, z-phi
        data3y.append(phi)
    elif recognize(row)>10 and recognize(row)<14:
        z,r,phi = get_cylindrical(row)
        data4x.append(r) # dome, r-phi
        data4y.append(phi)

print('The minimum and maximum for data1:')
print('r')
print(min(data1x))
print(max(data1x))
print('phi')
print(min(data1y))
print(max(data1y))

print('The minimum and maximum for data2:')
print('z')
print(min(data2x))
print(max(data2x))
print('phi')
print(min(data2y))
print(max(data2y))

print('The minimum and maximum for data3:')
print('z')
print(min(data3x))
print(max(data3x))
print('phi')
print(min(data3y))
print(max(data3y))

print('The minimum and maximum for data4:')
print('r')
print(min(data4x))
print(max(data4x))
print('phi')
print(min(data4y))
print(max(data4y))

tf = datetime.datetime.now()
dt = tf - ti
print("The total time cost: ")
print(dt)