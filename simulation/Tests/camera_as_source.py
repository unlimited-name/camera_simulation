import numpy as np
import datetime

from chroma.sim import Simulation
from chroma.loader import load_bvh
import detector_construction
from source import reflector_emission, reflector_patch


""" The simulation script for aborted simulation using reflector_emission as source. 
Attepted to use reflectors as light source and trace the photons at the camera, but failed.
only 1% of them reach the camera. 
"""

if __name__ == '__main__':
    ti = datetime.datetime.now()

    g = detector_construction.detector_construction()
    g.flatten()
    g.bvh = load_bvh(g)
    sim = Simulation(g)

    namestr = 'camera'

    position_list = []
    direction_list = []
    length_of_patch = 10000
    for j in range(1000):
        for ev in sim.simulate([reflector_emission(850, length_of_patch)],
                    keep_photons_beg=False,keep_photons_end=True,
                    run_daq=False,max_steps=100):

            detected = (ev.photons_end.flags & (0x1 << 2)).astype(bool)
            position_list.append(ev.photons_end.pos[detected])
            direction_list.append(ev.photons_end.dir[detected])

    
    position_full = np.concatenate(position_list, axis=0)
    np.save(namestr + '_position', position_full)
    direction_full = np.concatenate(direction_list, axis=0)
    np.save(namestr + '_direction', direction_full)

    tf = datetime.datetime.now()
    dt = tf - ti

    print("The total time cost: ")
    print(dt)
