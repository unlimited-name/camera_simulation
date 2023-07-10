import numpy as np
import datetime

from chroma.sim import Simulation
from chroma.loader import load_bvh
import detector_construction
from source import camera_source

"""
Used to generate simple camera->ref sim results using detector_camera
"""
if __name__ == '__main__':

    ti = datetime.datetime.now()
    print("Initial tima stamp: ")
    print(ti)
    namestr = 'reflector'
    g = detector_construction.detector_camera()
    g.flatten()
    g.bvh = load_bvh(g)
    sim = Simulation(g)

    # define the positions of camera surface
    dx, dy, dz = 0.03910, 0.06772, 0.34958
    pos_measure = np.array([0, np.sqrt(dx*dx+dy*dy), dz])
    h_cone = 0.060325
    pos_sapphire = pos_measure + np.array([0,h_cone*np.sin(22.5*np.pi/180),h_cone*np.cos(22.5*np.pi/180)])
    dir_sapphire = np.array([0, -1*np.sin(22.5*np.pi/180), -1*np.cos(22.5*np.pi/180)])

    # use camera source
    position_list = []
    direction_list = []
    for j in range(10000):
        for ev in sim.simulate([camera_source(850, 10000, pos_sapphire, dir_sapphire)],
                    keep_photons_beg=False,keep_photons_end=True,
                    run_daq=False,max_steps=100):

            detected = (ev.photons_end.flags & (0x1 << 2)).astype(bool)
            detected_index = np.arange(10000)[detected]
            position_list.append(ev.photons_end.pos[detected])
            direction_list.append(ev.photons_end.dir[detected])
    
    pos_data = np.concatenate(position_list, axis=0)
    np.save(namestr + '_position', pos_data)
    dir_data = np.concatenate(direction_list, axis=0)
    np.save(namestr + '_direction', dir_data)

    tf = datetime.datetime.now()
    dt = tf - ti
    print("The total time cost: ")
    print(dt)
