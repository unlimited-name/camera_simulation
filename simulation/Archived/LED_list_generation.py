from numpy import polyfit
import numpy as np

"""
The file used to generate a "random number list" used in picking direction vector for photons.

As a random variable (cosine theta), the distribution is modified with the actual LED source - 
use a list of (0.001 precision) numbers within [0,1], but each repeated with a "frequency"

The actual method we take here: frequency = int(probability * 1000)
This may satisfy our need for precision -- afterall, we don't have a precise data from LED source.
"""

I=np.array([1.0,0.95,0.87,0.75,0.58,0.4,0.2,0.12,0.06,0.0])
# viewed 'data points' from product data sheet
deg=np.arange(0,100,10)
deg=deg/180*np.pi
p=polyfit(deg,I,3)
print(p)
x=np.arange(0,np.pi/2,0.01)
y=p[0]*x*x*x+p[1]*x*x+p[2]*x+p[3]
"""
plt.plot(x,y)
plt.scatter(deg,I)
fig=plt.figure()
ax=plt.axes(projection = 'polar')
ax.set_thetagrids(np.arange(0.0, 180.0, 10.0))
ax.set_thetamax(90.0)
ax.set_thetamin(0.0)
p = [0.581, -1.338,  0.043,  0.994]
x=np.arange(0,np.pi/2,0.01)
y=p[0]*x*x*x+p[1]*x*x+p[2]*x+p[3]
plt.plot(x,y)
plt.scatter(deg,I)
"""
# commented code for plotting them out
from scipy import integrate
p = [0.581, -1.338,  0.043,  0.994]
def pdf(x):
    return p[0]*x*x*x+p[1]*x*x+p[2]*x+p[3]
def pdfu(u):
    x=np.arccos(u)
    return pdf(x)#/np.sin(x)
s,err = integrate.quad(pdfu, 0, 1) # normalization
#print(s)

l = np.arange(0, 1, 0.001)
data = []
for i in l:
    data.append(np.repeat(i, int(pdfu(i)/s*1000)))
data = np.concatenate(data)
print(data.shape)
np.save('led_list.npy',data)