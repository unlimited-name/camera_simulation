import numpy as np
import matplotlib.pyplot as plt
import time

from chroma.sim import Simulation
from chroma.loader import load_bvh
from source import traced_photon
import detector_construction
from add_reflection import pos_led

illu_array = np.load('illumination_map.npy')

def count_illumination(position):
    x,y,z = (position*1000).astype(int)
    x += 200
    y += 200
    if (x>=400 or x<0):
        illu = 0
    elif (y>=400 or y<0):
        illu = 0
    elif (z>=400 or z<0):
        illu = 0
    else:
        illu = illu_array[(x,y,z)]

    return illu

x_led, y_led, z_led = np.transpose(pos_led*1000).astype(int)
x_led += 200
y_led += 200
def check_reflection(position):
    # given position array, see if there is any photon causing reflection
    # works with apply_along_axis
    x,y,z = (position*1000).astype(int)
    x += 200
    y += 200
    x_delta = (x_led-x).astype(bool)
    y_delta = (y_led-y).astype(bool)
    z_delta = (z_led-z).astype(bool)
    judge = np.transpose([x_delta, y_delta, z_delta])
    zeros = judge[np.all(~judge, axis=1)]

    return len(zeros)

def sum_illumination(position, n=1000):
    pos = np.array(position)
    illu = np.apply_along_axis(count_illumination, 1, pos)
    effect = len(illu.nonzero()[0]) # record the number of effective photons
    
    reflect = np.apply_along_axis(check_reflection, 1, pos)
    if len(reflect.nonzero()[0])!=0:
        is_ref = 1
    else:
        is_ref = 0 
    return sum(illu)/n, effect, is_ref

if __name__ == '__main__':
    construction_code = 15
    g = detector_construction.detector_reflector(construction_code)
    g.flatten()
    g.bvh = load_bvh(g)
    sim = Simulation(g)

    namestr = 'camera'

    tinit = time.time()

    effect_total = 0
    length_of_patch = 1000
    hist_of_pixel = []
    list_of_pixel = [(i,j)
                    for i in range(0,400)
                    for j in range(0,640)]
    reflected_pixel = []
    for pixel in list_of_pixel:
        print(pixel)
        for ev in sim.simulate([traced_photon(pixel, length_of_patch, 850)],
                keep_photons_beg=False,keep_photons_end=True,
                run_daq=False,max_steps=20):

            #detected = (ev.photons_end.flags & (0x1 << 2)).astype(bool)
            #position_detected = ev.photons_end.pos[detected]
            position_end = ev.photons_end.pos
            if len(position_end):
                summed, effect, is_ref = sum_illumination(position_end, length_of_patch)
                hist_of_pixel.append(summed)
                effect_total += effect
                if is_ref:
                    reflected_pixel.append(pixel)
            else: 
                hist_of_pixel.append(0)

    #if len(position_list):
    #    position_full = np.concatenate(position_list, axis=0)
    #    np.save(namestr + '_position', position_full)
    hist_of_pixel = np.array(hist_of_pixel).reshape(400,640)
    np.save('hist_of_pixel', hist_of_pixel)
    if len(reflected_pixel):
        for pixel in reflected_pixel:
            add_value = hist_of_pixel[pixel] * 0.25
            qixel = np.array(pixel)
            hist_of_pixel[tuple(qixel+(0,1))] += add_value
            hist_of_pixel[tuple(qixel-(0,1))] += add_value
            hist_of_pixel[tuple(qixel+(1,0))] += add_value
            hist_of_pixel[tuple(qixel-(1,0))] += add_value
        print('Detected reflection...')
        print('Added reflection effect.')
        np.save('hist_of_pixel_add',hist_of_pixel)

    tf = time.time()
    dt = tf - tinit
    print('Total effective photons: ' + str(effect_total))
    print('out of ' +str(length_of_patch*len(hist_of_pixel.ravel())) + ' photons simulated.')
    print('Simulation time cost: ')
    print(str(round(dt/3600, 2)) + ' hour')

    """
    plt.imshow(hist_of_pixel, interpolation='none', cmap='gray')
    plt.colorbar()
    plt.savefig('hist_of_pixel.png')"""