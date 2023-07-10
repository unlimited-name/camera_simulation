import numpy as np
import sys
import os
import datetime

from chroma.sim import Simulation
from chroma.loader import load_bvh
import detector_construction
from source import photon_bomb, LED_ring

""" The old simulation file. This simulation is run in standard geometry. """

def write_photon(photons, namestr=''):
    # write everything of a photon into a series of text files

    f = open(namestr+'pos.txt', 'a')
    print(photons.pos, file = f)
    f.close()
    f = open(namestr+'dir.txt', 'a')
    print(photons.dir, file = f)
    f.close()
    f = open(namestr+'pol.txt', 'a')
    print(photons.pol, file = f)
    f.close()
    f = open(namestr+'wavl.txt', 'a')
    print(photons.wavelengths, file = f)
    f.close()
    f = open(namestr+'t.txt', 'a')
    print(photons.t, file = f)
    f.close()
    f = open(namestr+'tri.txt', 'a')
    print(photons.last_hit_triangles, file = f)
    f.close()
    f = open(namestr+'flags.txt', 'a')
    print(photons.flags, file = f)
    f.close()
    f = open(namestr+'chanl.txt', 'a')
    print(photons.channel, file = f)
    f.close()
    return

def write_array(array, namestr='array'):
    # write a seiries of arrays into a file
    # The array to be written here, are expected to be a 1-d array - like the vertices in chroma
    # They will be written out in n*3 array.
    f = open(namestr + '.txt', 'a')
    a = np.array(array).reshape((-1,3))
    print(a, file = f)
    f.close()
    return

def write_event(event, namestr = 'event/'):
    """
    Write event(s) to certain output forms. Use mode number to direct the function
    Simulation.simulate() will return a set of events, use a for loop to locate each one of them

    Writing to a .txt file is used as an intuitive view of data structure
    For data analysis, write to .csv file with switches is a good choice.
    """
    #sys.stdout = open('event.txt','wt')
    #if os.access("/file/path/foo.txt", os.F_OK):
    # check folders
    if not os.path.exists(namestr):
        os.makedirs(namestr)
    
    if event.photons_beg is not None:
        if len(event.photons_beg.pos) > 0:
            write_photon(event.photons_beg, namestr + 'beg_')

    if event.photons_end is not None:
        if len(event.photons_end.pos) > 0:
            write_photon(event.photons_end, namestr + 'end_')
    
    if event.photon_tracks is not None:
        """
        photon_tracks is a list containning class Photon(s)...
        you need to list() it at first, otherwise it is NoType
        parent_trackid info is also commented below
        """
        for i in list(event.photon_tracks):
            write_photon(i, namestr + 'track_')
        #event.photon_parent_trackids.resize(len(event.photon_parent_trackids))
        #np.asarray(event.photon_parent_trackids)[:] = event.photon_parent_trackids

    
    if event.vertices is not None:
        write_array(event.vertices, namestr + 'vertices')
    
    if event.hits is not None:
        event.hits.clear()
        for hit in event.hits:
            photons = event.hits[hit]
            if len(photons.pos) > 0:
                write_photon(photons, namestr + 'hits_')
    else:
        event.hits.clear()
    
    if event.flat_hits is not None:
        photons = event.flat_hits
        if len(photons.pos) > 0:
            write_photon(photons, namestr + 'flathit_')
    
    if event.channels is not None:
        hit_channels = event.channels.hit.nonzero()[0].astype(np.uint32)
        if len(hit_channels) > 0:
            f = open(namestr + 'channel.txt','a')
            print('ch.t', file=f)
            print(event.channels.t.astype(np.float32), file=f)
            print('ch.q', file=f)
            print(event.channels.q.astype(np.float32), file=f)
            print('ch.flags', file=f)
            print(event.channels.flags.astype(np.float32), file=f)

    return

if __name__ == '__main__':
    ti = datetime.datetime.now()
    if len(sys.argv)==1:
        mode = 'point'
    else:
        mode = sys.argv[1]
    """
    if mode == 'test':
        g = detector_construction.test_geometry()
    else:
        g = detector_construction.detector_construction()
    """

    g = detector_construction.detector_construction()
    g.flatten()
    g.bvh = load_bvh(g)
    sim = Simulation(g)

    # sim.simulate() always returns an iterator even if we just pass
    namestr = str(datetime.date.today())

    position_list = []
    direction_list = []
    if mode=='led':
        for j in range(10000):
            for ev in sim.simulate([LED_ring(850, 10000, (0,0,0.1), (0,0,1))],
                        keep_photons_beg=False,keep_photons_end=True,
                        run_daq=False,max_steps=100):

                detected = (ev.photons_end.flags & (0x1 << 2)).astype(bool)
                detected_index = np.arange(1000)[detected]
                position_list.append(ev.photons_end.pos[detected], index = detected_index)
                position_list.append(ev.photons_end.dir[detected], index = detected_index)
    elif (mode=='point' or mode=='test'):
        for j in range(10000):
            for ev in sim.simulate([photon_bomb(10000, 850, (0,0,0.1))],
                        keep_photons_beg=False,keep_photons_end=True,
                        run_daq=False,max_steps=20):

                detected = (ev.photons_end.flags & (0x1 << 2)).astype(bool)
                detected_index = np.arange(1000)[detected]
                position_list.append(ev.photons_end.pos[detected], index = detected_index)
                position_list.append(ev.photons_end.dir[detected], index = detected_index)
    else:
        raise Exception('Please enter a valid mode: vim this file for details.')
    
    position_full = np.concatenate(position_list, axis=0)
    np.save(namestr + '_position', position_full)
    direction_full = np.concatenate(direction_list, axis=0)
    np.save(namestr + '_direction', direction_full)
    tf = datetime.datetime.now()
    dt = tf - ti


    print("The total time cost: ")
    print(dt)
