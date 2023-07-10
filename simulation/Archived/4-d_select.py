import numpy as np
import time

from chroma.sim import Simulation
from chroma.loader import load_bvh
import detector_construction
from chroma.event import Photons

""" An aborted trial of applying cosine similarity in generating traced photons, 
given the information of LED->reflector photons, find out the relavant photons reflector->camera
"""


def cosine_similarity(array1, array2, threshold = 0.99):
    # return the result of cosine sim judge. posdir is the result of cam-ref simulation,
    # target is the generated photon pos-dir vector. 
    if (array1.shape != array2.shape):
        raise Exception('Different shape between arrays!')
    
    sim = np.sum(array1*array2, axis=1)/np.sqrt(np.sum(array1*array1, axis=1)*np.sum(array2*array2, axis=1))
    #print('Cosine value:')
    #print(sim)
    judge = np.piecewise(sim, [sim>=threshold, sim<threshold], [True, False])
    return judge.astype(bool)

def cosine_select():
    # select photons using cosine similarity. 1st sims are classified to poslist; pos are selected randomly from them.
    # 2rd sims are stored in .npy files; randomly select a dirvec, then add some deviation to it
    # lastly, test: if it passed cosine similarity, then true. 
    pos_light = np.load('led_illumination.npy')
    pos_cam = np.load('reflector_position.npy')
    dir_cam = np.load('reflector_direction.npy')
    length_cam = len(pos_cam)
    deviation = 0.01
    posdir = np.concatenate((pos_cam, dir_cam), axis=1)

    length_subset = 0
    iter = 0
    while (length_subset == 0):
        ind_select = np.random.choice(np.arange(len(pos_light)))
        pos_select = np.take(pos_light, ind_select, axis=0)
        ind_subset = np.arange(length_cam)[cosine_similarity(pos_cam, np.repeat([pos_select], length_cam, axis=0), threshold=0.995)]
        #print(ind_subset.shape)
        length_subset = len(ind_subset)
        iter += 1
        if (iter >= 100):
            raise Exception('Too many trials in pos selection!')

    posdir = np.take(posdir, ind_subset, axis=0)
    dir_subset = np.take(dir_cam, ind_subset, axis=0)
    del pos_cam, dir_cam

    t,f = m.get_angles_array(dir_subset)
    t += np.random.randn(len(t)) * deviation
    f += np.random.randn(len(t)) * deviation
    dir_choice = m.unit_vector(t,f) # an array of possible dirs
    ind_select = np.random.choice(np.arange(len(dir_choice)))
    dir_select = np.take(dir_choice, ind_select, axis=0)

    vec_select = np.concatenate([pos_select, dir_select])

    judge = cosine_similarity(posdir, np.repeat([vec_select], len(posdir), axis=0), threshold=0.9999)
    if (len(judge.nonzero()[0])==0):
        #print('Selection Failure!')
        return 0, 0
    else: 
        #print('Selection Success!')
        return pos_select, -dir_select

def four_dimentional_select(wavelength, n):
    poslis = []
    dirlis = []
    pollis = []
    for i in range(n):
        pos = 0
        dir = 0
        iter = 0
        while (isinstance(pos, int)):
            pos, dir = cosine_select()
            iter += 1
            if (iter>1000):
                #raise Exception('Repeated failure in cosine selection!')
                break
        
        poslis.append(pos)
        dirlis.append(dir)
        pollis.append(np.cross(dir, m.random_vector()))
    pos_photon = np.concatenate([poslis], axis=0)
    dir_photon = np.concatenate([dirlis], axis=0)
    pol_photon = np.concatenate([pollis], axis=0)
    n_actual = len(pol_photon)
    if (n != n_actual):
        print('Warning: '+str(n-n_actual)+' Photons lost during generation')

    wavelengths = np.repeat(wavelength,n_actual)
    return Photons(pos_photon, dir_photon, pol_photon, wavelengths)

if __name__ == '__main__':

    """
    The main func is used to generate simple camera->ref sim results
    """
    ti = time.time()
    print("Initial tima stamp: ")
    print(ti)
    namestr = 'test'
    g = detector_construction.detector_camera()
    g.flatten()
    g.bvh = load_bvh(g)
    sim = Simulation(g)

    position_list = []
    direction_list = []
    length_of_patch = 10000
    for j in range(1):
        for ev in sim.simulate([four_dimentional_select(850, length_of_patch)],
                    keep_photons_beg=False,keep_photons_end=True,
                    run_daq=False,max_steps=100):

            detected = (ev.photons_end.flags & (0x1 << 2)).astype(bool)
            position_list.append(ev.photons_end.pos[detected])
            direction_list.append(ev.photons_end.dir[detected])

    
    position_full = np.concatenate(position_list, axis=0)
    np.save(namestr + '_position', position_full)
    direction_full = np.concatenate(direction_list, axis=0)
    np.save(namestr + '_direction', direction_full)

    tf = time.time()
    dt = tf - ti
    print("The total time cost: ")
    print(dt)
