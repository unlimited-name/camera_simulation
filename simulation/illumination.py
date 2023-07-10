import numpy as np
import sys
import time

from chroma.sim import Simulation
from chroma.loader import load_bvh
from source import LED_ring, triple_LED_ring, point_source, photon_bomb
import detector_construction

def Hist_illu_write(position):
    # given the data (position) of illumination map, generate a 3d array 'histogram'
    # consider cartesian coordinates, xyz in range x,y(-0.2, +0.2); z(0, 0.4)
    # suppose precision as 0.001 (1mm) per bin
    pos = np.array(position)
    t1 = time.time()
    succ = 0
    fail = 0
    illu_array = np.zeros((400,400,400), dtype=int)
    for line in pos:
        x,y,z = (line*1000).astype(int)
        x += 200
        y += 200
        #print('x, y, z:')
        #print(str(x)+'\t'+str(y)+'\t'+str(z))
        if (x>=400 or x<0):
            fail += 1
            continue
        elif (y>=400 or y<0):
            fail += 1
            continue
        elif (z>=400 or z<0):
            fail += 1
            continue
        else:
            illu_array[(x,y,z)] += 1
            succ += 1
    np.save('illumination_map', illu_array)
    t2 = time.time()
    dt = t2-t1
    print('Time cost for illumination writing:')
    print(dt)
    print('Total success: '+str(succ))
    print('Total failure: '+str(fail))
    rate = len((illu_array.ravel()).nonzero()[0]) / len(illu_array.ravel())
    print('Illumination map fill rate: '+str(round(rate*100, 2)) +'%')
    return

if __name__ == '__main__':
    construction_code = 15
    ti = time.time()
    print("Initial time stamp: ")
    print(ti)
    #namestr = str(datetime.date.today())
    namestr = 'illumination'
    if len(sys.argv)==1:
        mode = 'test'
    else:
        mode = sys.argv[1]
    namestr = namestr + '_' + mode
    g = detector_construction.detector_reflector(construction_code)
    g.flatten()
    g.bvh = load_bvh(g)
    sim = Simulation(g)

    dx, dy, dz = 0.03910, 0.06772, 0.34958
    pos_measure = np.array([0, np.sqrt(dx*dx+dy*dy), dz])
    l_deviation = 0.0005
    pos_center = pos_measure - np.array([0,l_deviation*np.sin(22.5*np.pi/180),l_deviation*np.cos(22.5*np.pi/180)])
    dir_center = np.array([0, -1*np.sin(22.5*np.pi/180), -1*np.cos(22.5*np.pi/180)])

    position_list = []
    length_of_batch = 10000
    if (mode=='led'):
        for j in range(1000):
            for ev in sim.simulate([LED_ring(850, length_of_batch, pos_center, dir_center)],
                        keep_photons_beg=False,keep_photons_end=True,
                        run_daq=False,max_steps=100):

                detected = (ev.photons_end.flags & (0x1 << 2)).astype(bool)
                detected_index = np.arange(length_of_batch)[detected]
                position_list.append(ev.photons_end.pos[detected])
    elif (mode == '3led'):
        for j in range(1000):
            for ev in sim.simulate([triple_LED_ring(850, length_of_batch, pos_center, dir_center)],
                        keep_photons_beg=False,keep_photons_end=True,
                        run_daq=False,max_steps=100):

                detected = (ev.photons_end.flags & (0x1 << 2)).astype(bool)
                detected_index = np.arange(length_of_batch)[detected]
                position_list.append(ev.photons_end.pos[detected])
    elif (mode=='point'):
        for j in range(1000):
            for ev in sim.simulate([point_source(850, length_of_batch, pos_center, dir_center)],
                        keep_photons_beg=False,keep_photons_end=True,
                        run_daq=False,max_steps=100):

                detected = (ev.photons_end.flags & (0x1 << 2)).astype(bool)
                detected_index = np.arange(length_of_batch)[detected]
                position_list.append(ev.photons_end.pos[detected])
    elif (mode=='test'):
        for j in range(1000):
            for ev in sim.simulate([photon_bomb(length_of_batch, 850, (0,0,0.04))],
                        keep_photons_beg=False,keep_photons_end=True,
                        run_daq=False,max_steps=100):

                detected = (ev.photons_end.flags & (0x1 << 2)).astype(bool)
                detected_index = np.arange(length_of_batch)[detected]
                position_list.append(ev.photons_end.pos[detected])
    else:
        raise Exception('Please enter a valid mode: test, point, led1 or led3')
    
    pos_data = np.concatenate(position_list, axis=0)
    np.save(namestr + '_position', pos_data)

    tf = time.time()
    dt = tf - ti
    print("The total time cost: ")
    print(dt)

    Hist_illu_write(pos_data)