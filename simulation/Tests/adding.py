from chroma import make
from chroma.geometry import Solid, Geometry
from chroma.demo.optics import glass, vacuum
from chroma.demo.optics import black_surface, shiny_surface
from optics import detector_surface
from optics import cf4 as water
from chroma.sim import Simulation
from chroma.loader import load_bvh
import chroma.stl as stl
import numpy as np
import pandas as pd
import datetime
import sys
from light import LED_ring, photon_bomb
from math import rotation_matrix

"""
This file is used for geometry testing (in terms of correctly running the geometry construction codes.)
Tried to add a layer of geometry at a time, and run a simulation of certain photons
to find out where the geometry might be wrong - it can be a poor mesh, a miswritten bulk material, etc.
The basic idea is to copy the geometry construction lines here, 
and run simulations in a loop to see where is wrong. 

This file is no longer used and some of the lines are not reasonable any more.
"""

def build_detector(mode=0):
    """
    Returns a cubic detector made of cubic photodetectors. 
    used for testing, mode = 0,1,2,3,4....
    
    mode = 0: add nothing
    mode = 1: inner jar only
    mode = 2: outer jar
    mode = 3: IJ and OJ reflectors
    mode = 4: dome reflectors
    mode = 5: cone + detector
    mode = 6: head reflectors
    """
    size = 0.2
    nx, ny, nz = 2, 2, 2
    spacing = size*2
    g = Geometry(water)

    world = Solid(make.box(spacing*nx,spacing*ny,spacing*nz),water,vacuum,
                  color=0x33ffffff)
    g.add_solid(world)
    # a .4*.4*.4 world with water
    # adding layers with mode number

    pos0 = np.array([0,0,0])
    mode = int(mode)
    if (mode>0):
        Ijout_mesh = stl.mesh_from_stl('ij_out.stl')
        Ijin_mesh = stl.mesh_from_stl('ij_in.stl')
        Ijout_solid = Solid(Ijout_mesh, glass, water)
        pos_ijout = pos0 - np.array([0,0,0.0001])
        rot_ij = rotation_matrix(0,0,0)
        g.add_solid(Ijout_solid, rot_ij, pos_ijout)
        Ijin_solid = Solid(Ijin_mesh, water, glass)
        pos_ijin = pos0
        g.add_solid(Ijin_solid, rot_ij, pos_ijin)

    if (mode>1):
        Ojout_mesh = stl.mesh_from_stl('oj_out.stl')
        Ojin_mesh = stl.mesh_from_stl('oj_in.stl')
        Ojout_solid = Solid(Ojout_mesh, glass, water)
        pos_ojout = pos0 - np.array([0,0,0.0001])
     # make a bit room for distinction. moved outer part a bit lower
        rot_oj = rotation_matrix(0,0,0)
        g.add_solid(Ojout_solid, rot_oj, pos_ojout)
        Ojin_solid = Solid(Ojin_mesh, water, glass)
        pos_ojin = pos0
        g.add_solid(Ojin_solid, rot_oj, pos_ojin)

    if (mode>2):
        Oref_mesh = stl.mesh_from_stl('oj_ref.stl')
        Oref_solid = Solid(Oref_mesh, water, water, detector_surface)
        pos_oref = pos0
        g.add_solid(Oref_solid, rotation_matrix(0,0,0), pos_oref)
        Iref_mesh = stl.mesh_from_stl('ij_ref.stl')
        Iref_solid = Solid(Iref_mesh, water, water, detector_surface)
        pos_iref = pos0
        g.add_solid(Iref_solid, rotation_matrix(0,0,0), pos_iref)

    if (mode>3):
        # dome reflectors
        # 8 pieces, thus treated in a for loop
        Dref_mesh = stl.mesh_from_stl('dome_ref.stl')
        Dref_solid = Solid(Dref_mesh, water, water, detector_surface)
        dr_dref = np.sqrt(0.01776 ** 2 + (0.07264+0.060325) ** 2) # difference in x-y plane
        dz_dref = 0.28018 # measured position in z
        t_plate = - 90 + 14.82 # slope of plate, 14.82 degree
        for i in range(8):
            pos_dref = np.array([dr_dref*np.cos(i*np.pi/4), dr_dref*np.sin(i*np.pi/4), dz_dref]) + pos0
            rot_dref = rotation_matrix(t_plate*np.pi/180, 0, i*np.pi/4) 
            # every plate is originally in x-y plane, then rotated along 
            g.add_solid(Dref_solid, rot_dref, pos_dref)
            # g.add_solid(SiPM(), rot_dref, pos_dref)
            # adding a sipm at each plate's center
    
    if (mode>4):
        Sapphire_mesh = stl.mesh_from_stl('sapphire.stl')
        Sapphire_solid = Solid(Sapphire_mesh, glass, water)
        rot_sapphire = rotation_matrix(22.5*np.pi/180, 0, 0)
        h_cone = 0.060325
        pos_measure = np.array([(0.03750+0.02913+0.04603)/2+0.060325, 0, (0.34097+0.38421)/2])
        pos_sapphire = pos0 + pos_measure + np.array([h_cone*np.sin(22.5*np.pi/180),0,h_cone*np.cos(22.5*np.pi/180)])
        g.add_solid(Sapphire_solid, rot_sapphire, pos_sapphire)
        # head cones
        Head_mesh = stl.mesh_from_stl('head_cone.stl')
        Head_solid = Solid(Head_mesh, water, water, black_surface) 
        # normal vector / optical axis: 28.16 degree to z axis
        # measured data above. Use 22.5 the design data instead.
        rot_head1 = rotation_matrix(22.5*np.pi/180, 0, 0)
        pos_head1 = pos_measure + pos0
        g.add_solid(Head_solid, rot_head1, pos_head1)
        rot_head2 = rotation_matrix(22.5*np.pi/180, 0, np.pi/3)
        pos_head2 = np.dot(pos_head1, rotation_matrix(0,0,np.pi/3))
        g.add_solid(Head_solid, rot_head2, pos_head2)
        rot_head3 = rotation_matrix(22.5*np.pi/180, 0, 2*np.pi/3)
        pos_head3 = np.dot(pos_head1, rotation_matrix(0,0,2*np.pi/3))
        g.add_solid(Head_solid, rot_head3, pos_head3)

    if (mode >5):
        Href_mesh = stl.mesh_from_stl('head_ref.stl')
        Href_solid = Solid(Href_mesh, water, water, detector_surface)
        l_deviation = 0.0005
        pos_href1 = pos_head1 - np.array([l_deviation*np.sin(22.5*np.pi/180),0,l_deviation*np.cos(22.5*np.pi/180)])
        pos_href2 = np.dot(pos_href1, rotation_matrix(0,0,np.pi/3))
        pos_href3 = np.dot(pos_href1, rotation_matrix(0,0,2*np.pi/3))
        g.add_solid(Href_solid, rot_head1, pos_href1)
        g.add_solid(Href_solid, rot_head2, pos_href2)
        g.add_solid(Href_solid, rot_head3, pos_href3)
    
    return g

def simulate(mode = 0):
    g = build_detector(mode)
    g.flatten()
    g.bvh = load_bvh(g)
    sim = Simulation(g)
    pos_measure = np.array([(0.03750+0.02913+0.04603)/2+0.060325, 0, (0.34097+0.38421)/2])
    l_deviation = 0.001
    pos_center = pos_measure - np.array([l_deviation*np.sin(22.5*np.pi/180),0,l_deviation*np.cos(22.5*np.pi/180)])
    dir_center = np.array([-1*np.sin(22.5*np.pi/180), 0, -1*np.cos(22.5*np.pi/180)])
    namestr = 'mode'+str(mode)
    position_list = []
    length_of_batch = 1000
    for i in range(1):
        for j in range(1000):
            for ev in sim.simulate([LED_ring(850, length_of_batch, pos_center, dir_center)],
                           keep_photons_beg=False,keep_photons_end=True,
                           run_daq=False,max_steps=20):
                detected = (ev.photons_end.flags & (0x1 << 2)).astype(bool)
                detected_index = np.arange(length_of_batch)[detected]
                position_list.append(pd.DataFrame(ev.photons_end.pos[detected], index = detected_index))
    
    position_full = pd.concat(position_list)
    namestr = namestr + '_adding.csv'
    position_full.to_csv(namestr)


if __name__ == '__main__':

    ti = pd.to_datetime(datetime.datetime.now())
    if len(sys.argv)==1:
        mode = 6
    else:
        mode = int(sys.argv[1])
    
    simulate(mode)
    
    tf = datetime.datetime.now()
    dt = tf - ti

    print("The total time cost: ")
    print(dt)