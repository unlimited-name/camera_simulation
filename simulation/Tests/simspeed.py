import numpy as np
import sys
import datetime
import pandas as pd

""" A test for the algorithm used in simulation
Result: Approach 1 is the best - use a list[] as a buffer to store the data, 
and use numpy.concatenate() to merge into a large one -
Lastly, turn to pandas for output.
"""

def mat_gene(n):
    """ generate a dummy data matrix """
    n = int(n)
    mat = np.arange(n*3, dtype=float).reshape(-1, 3)
    return mat

if __name__ == '__main__':
    batch = 1000
    gene = 1000
    t1 = datetime.datetime.now()
    """ App 1 """
    buff = []
    for i in range(batch):
        buff.append(mat_gene(gene))
    data = pd.DataFrame(np.concatenate(buff[:], axis=0))

    """ App 2 - the first version """
    t2 = datetime.datetime.now()
    buff = []
    for i in range(batch):
        buff.append(pd.DataFrame(mat_gene(gene)))
    data = pd.concat(buff)

    """ App 3 - adding a iterator """
    t3 = datetime.datetime.now()
    buff = []
    for i in range(100):
        for j in range(100):
            buff.append(mat_gene(100))
    data = pd.DataFrame(np.concatenate(buff[:], axis=0))

    """ App 4 - dumb way """
    t4 = datetime.datetime.now()
    buff = np.empty([0,3], dtype=float)
    for i in range(batch):
        buff = np.append(buff, mat_gene(gene), axis=0)
    data = pd.DataFrame(buff)

    tf = datetime.datetime.now()
    print("Approach 1 time cost: ")
    print(t2-t1)
    print("Approach 2 time cost: ")
    print(t3-t2)
    print("Approach 3 time cost: ")
    print(t4-t3)
    print("Approach 4 time cost: ")
    print(tf-t4)