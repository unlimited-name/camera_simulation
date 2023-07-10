import pandas as pd
import sys
import datetime
import numpy as np
from array import array

"""
A speed test for algorithm in data processing.
Result: using a [] list as a buffer, and then convert it to a numpy array is the fastest way. 
Try to avoid unneccesary lines, especially when they are going to loop millions of times.
"""


# name dependent on the time of running
namestr = str(datetime.datetime.now())
if len(sys.argv)==1:
    raise Exception("Please enter a filename! ")
else:
    filename = sys.argv[1]

# load data from input filename
df = pd.read_csv(filename, usecols=[1,2,3], dtype=float) # Reading rows. 
ti = datetime.datetime.now()
""" approach one """
# Turn rows to points
"""data = np.empty([0,3], dtype=float) # subject to change - may not be positions
for i in range(len(df)):
    point = np.array(df.loc[i])
    data = np.append(data, [point], axis=0)

x, y, z = np.transpose(data)[:]"""
t1 = datetime.datetime.now()
dt = t1 - ti
print("Approach 1 time cost: ")
print(dt)

""" App 2"""
buffer = []
for i in range(len(df)):
    point = np.array(df.loc[i])
    buffer.append(point)
buffer = np.transpose(np.array(buffer))

# Now extract every line of buffer, for cylindrical, it is z,r,phi
x, y, z = buffer[:]
t2 = datetime.datetime.now()
dt = t2 - t1
print("Approach 2 time cost: ")
print(dt)

""" App 3"""
buff = array('d')
for i in range(len(df)):
    buff.append(df.loc[i][0])
    buff.append(df.loc[i][1])
    buff.append(df.loc[i][2])
data2 = np.frombuffer(buff,dtype=float).reshape(-1,3)

t3 = datetime.datetime.now()
dt = t3 - t2
print("Approach 3 time cost: ")
print(dt)