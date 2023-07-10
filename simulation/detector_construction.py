import numpy as np
import sys

from chroma.geometry import Geometry,Solid
from chroma.make import linear_extrude
from chroma.transform import make_rotation_matrix
from chroma.demo.optics import glass, water, vacuum, r7081hqe_photocathode
import chroma.stl as stl
import chroma.make as make

from optics import teflon_surface, detector_surface, black_surface
from optics import argon, cf4, quartz, sapphire, bubblegas
from mathematics import rotation_matrix


"""
Construction of a geometry. To use it in a simulation, call detector_construction().

Tactics:
separate the construction into steps: the meshes of geometry objects used are either imported from
Solidworks model, or constructed externally using python packages (or any other reliable software)
chroma integrates a pack called 'PyMesh', which is also used in its GDML interface.
PyMesh is a good choice but will add (unnecessary) complexity to chroma installation. One may skip 
all the PyMesh stuff and still can run the simulations.
Notice the chroma GDML interface is not properly using Pymesh for geometry import, so one should 
avoid using GDML as a interface between Geant4 and chroma. 

here we import the needed meshes in .stl format, and make fine adjustments to them. 
for meshes used multiple times and needs adjustion after import, distinct functions are written 
but they can simply be ignored. 

The properties of Materials and Surfaces are moved to optics.py....
"""

def SiPM():
    # create a simple square with length a at x-y plane
    # used as black sipm
    a = 0.0141
    a = a/2
    #vertice = np.array([[a,a,0],[-a,a,0],[-a,-a,0],[a,-a,0]])
    #triangle = np.array([[1,2,3],[3,4,1]])
    #mesh = Mesh(vertice, triangle)
    mesh = linear_extrude([-a,a,a,-a],[-a,-a,a,a], height=0.0001, center=(0,0,0))
    solid = Solid(mesh, cf4,cf4, black_surface)
    return solid

def add_bubble():
    mesh = stl.mesh_from_stl('Meshes/bubble_2.stl')
    solid = Solid(mesh, bubblegas, argon)
    return solid

def detector_construction():
    g = Geometry(cf4)
    pos0 = np.array([0,0,0])
    # this is the position of inner jar center relative to [0,0,0]
    # in my construction, I actually considered all the position relative to inner jar center
    pos1 = np.array([0,0,0.2225])
    # the distance between outer jar center and inner jar.

    # World
    #World_mesh = make.cube(1)
    #World_solid = Solid(World_mesh, cf4, cf4, black_surface)
    World_solid = Solid(make.box(1,1,1),cf4,cf4,
                  color=0x33ffffff)
    g.add_solid(World_solid)
    # treat the PV as the world, a 2*2*2 cube centered at (0,0,0)

    # Inner jar
    Ijout_mesh = stl.mesh_from_stl('Meshes/ij_out.stl')
    Ijin_mesh = stl.mesh_from_stl('Meshes/ij_in.stl')
    Ijout_solid = Solid(Ijout_mesh, quartz, argon)
    pos_ijout = pos0 - np.array([0,0,0.0001])
    rot_ij = rotation_matrix(0,0,0)
    g.add_solid(Ijout_solid, rot_ij, pos_ijout)
    Ijin_solid = Solid(Ijin_mesh, cf4, quartz)
    pos_ijin = pos0
    g.add_solid(Ijin_solid, rot_ij, pos_ijin)

    # Outer jar
    Ojout_mesh = stl.mesh_from_stl('Meshes/oj_out.stl')
    Ojin_mesh = stl.mesh_from_stl('Meshes/oj_in.stl')
    Ojout_solid = Solid(Ojout_mesh, quartz, cf4)
    pos_ojout = pos0 - np.array([0,0,0.0001])
    # make a bit room for distinction. moved outer part a bit lower
    rot_oj = rotation_matrix(0,0,0)
    g.add_solid(Ojout_solid, rot_oj, pos_ojout)
    Ojin_solid = Solid(Ojin_mesh, argon, quartz)
    pos_ojin = pos0
    g.add_solid(Ojin_solid, rot_oj, pos_ojin)
    
    # Outer Jar reflector
    Oref_mesh = stl.mesh_from_stl('Meshes/oj_ref.stl')
    Oref_solid = Solid(Oref_mesh, cf4, cf4, teflon_surface)
    pos_oref = pos0
    g.add_solid(Oref_solid, rotation_matrix(0,0,0), pos_oref)

    # Inner jar reflector
    Iref_mesh = stl.mesh_from_stl('Meshes/ij_ref.stl')
    Iref_solid = Solid(Iref_mesh, cf4, cf4, teflon_surface)
    pos_iref = pos0
    g.add_solid(Iref_solid, rotation_matrix(0,0,0), pos_iref)

    # dome reflectors
    # 8 pieces, thus treated in a for loop
    Dref_mesh = stl.mesh_from_stl('Meshes/dome_ref.stl')
    Dref_solid = Solid(Dref_mesh, cf4, cf4, teflon_surface)
    dr_dref = np.sqrt(0.01776 ** 2 + (0.07264+0.060325) ** 2) # difference in x-y plane
    dz_dref = 0.28018 # measured position in z
    t_plate = (-90 + 14.82) *np.pi/180 # slope of plate, 14.82 degree
    for i in range(8):
        pos_dref = np.array([dr_dref*np.cos(i*np.pi/4 + np.pi/2), dr_dref*np.sin(i*np.pi/4 + np.pi/2), dz_dref]) + pos0
        # the first plate must be placed at (0, dr, dz).
        rot_dref = rotation_matrix(t_plate, 0, -i*np.pi/4) 
        # every plate is originally in x-y plane, then rotated along z axis; 
        # to ensure coordination with position, let the rotation be counter-clockwise.
        g.add_solid(Dref_solid, rot_dref, pos_dref)
        #g.add_solid(SiPM(), rot_dref, pos_dref)
        # adding a sipm at each plate's center

    # sapphire viewpoint
    Sapphire_mesh = stl.mesh_from_stl('Meshes/sapphire.stl')
    Sapphire_solid = Solid(Sapphire_mesh, cf4, cf4, detector_surface)
    h_cone = 0.060325
    # pos_measure = np.array([0, (0.03750+0.02913+0.04603)/2+0.060325, (0.34097+0.38421)/2])
    # The measured position of head cone center(bottom), to zero point
    rot_sapphire1 = rotation_matrix(22.5*np.pi/180, 0, 0)
    dx, dy, dz = 0.03910, 0.06772, 0.34958
    pos_measure = np.array([0, np.sqrt(dx*dx+dy*dy), dz])
    pos_sapphire1 = pos0 + pos_measure + np.array([0,h_cone*np.sin(22.5*np.pi/180),h_cone*np.cos(22.5*np.pi/180)])
    g.add_solid(Sapphire_solid, rot_sapphire1, pos_sapphire1)
    """
    rot_sapphire2 = rotation_matrix(22.5*np.pi/180, 0, 2*np.pi/3)
    pos_sapphire2 = np.dot(pos_sapphire1, rotation_matrix(0,0,2*np.pi/3))
    g.add_solid(Sapphire_solid, rot_sapphire2, pos_sapphire2)
    rot_sapphire3 = rotation_matrix(22.5*np.pi/180, 0, 4*np.pi/3)
    pos_sapphire3 = np.dot(pos_sapphire1, rotation_matrix(0,0,4*np.pi/3))
    g.add_solid(Sapphire_solid, rot_sapphire3, pos_sapphire3)"""

    # head cones
    Head_mesh = stl.mesh_from_stl('Meshes/head_cone.stl')
    Head_solid = Solid(Head_mesh, cf4, cf4, black_surface) 
    # normal vector / optical axis: 28.16 degree to z axis
    # measured data above. Use 22.5 the design data instead.
    rot_head1 = rotation_matrix(22.5*np.pi/180, 0, 0)
    pos_head1 = pos_measure + pos0
    g.add_solid(Head_solid, rot_head1, pos_head1)
    rot_head2 = rotation_matrix(22.5*np.pi/180, 0, 2*np.pi/3)
    pos_head2 = np.dot(pos_head1, rotation_matrix(0,0,2*np.pi/3))
    g.add_solid(Head_solid, rot_head2, pos_head2)
    rot_head3 = rotation_matrix(22.5*np.pi/180, 0, 4*np.pi/3)
    pos_head3 = np.dot(pos_head1, rotation_matrix(0,0,4*np.pi/3))
    g.add_solid(Head_solid, rot_head3, pos_head3)

    # head reflectors
    Href_mesh = stl.mesh_from_stl('Meshes/head_ref.stl')
    Href_solid = Solid(Href_mesh, cf4, cf4, teflon_surface)
    l_deviation = 0.00025
    pos_href1 = pos_head1 - np.array([0, l_deviation*np.sin(22.5*np.pi/180),l_deviation*np.cos(22.5*np.pi/180)])
    pos_href2 = np.dot(pos_href1, rotation_matrix(0,0,2*np.pi/3))
    pos_href3 = np.dot(pos_href1, rotation_matrix(0,0,4*np.pi/3))
    g.add_solid(Href_solid, rot_head1, pos_href1)
    g.add_solid(Href_solid, rot_head2, pos_href2)
    g.add_solid(Href_solid, rot_head3, pos_href3)

    """
    # adding sipms onto reflectors
    # oj reflector
    dz_ojsipm = 0.2225 /4
    oj_r = 0.12235
    for i in range(8):
        pos_ojsipm = np.array([oj_r, 0, 0]) + pos0
        rot_ojsipm = rotation_matrix(0, 0, np.pi/4*i)
        g.add_solid(SiPM(), rot_ojsipm, pos_ojsipm)
        pos_ojsipm = pos_ojsipm + np.array([0,0,dz_ojsipm])
        g.add_solid(SiPM(), rot_ojsipm, pos_ojsipm)
        pos_ojsipm = pos_ojsipm + np.array([0,0,dz_ojsipm])
        g.add_solid(SiPM(), rot_ojsipm, pos_ojsipm)
        pos_ojsipm = pos_ojsipm + np.array([0,0,dz_ojsipm])
        g.add_solid(SiPM(), rot_ojsipm, pos_ojsipm)
    # ij reflector"""

    return g

def detector_reflector(id_number = 0):
    """
    A detector used for illumination.py
    Use ID number for distinction for detectors. Same as the coding used in data processing, 
    a hexodecimal number representing the construction options for reflectors:
    teflon_surface: 90% reflecting, 10% absorbing; detector_surface: 90% reflecting, 10% detecting.
    - Head reflector: teflon / detector 
    - Dome reflector: teflon / detector 
    - OJ reflector: teflon / detector 
    - IJ reflector: teflon / detector 
    For example, if we want OJ and IJ reflector to be detecting, the ID number is hex(0011)=3
    Note we only check the last 4 digits of the ID number, so some invalid numbers will 
    still let the code run.
    """

    # check ID number first
    try:
        int(id_number)
    except ValueError:
        print("Please use an integer for reflector construction!")
    else:
        id_number = int(id_number)
    if (id_number<0):
        print("================Information mode=================")
        print("Please enter a valid hexadecimal number as process code. ")
        print("Each digit represents meaning as such:")
        print("Head reflector: detector (True) / teflon (False)")
        print("Dome reflector: detector (True) / teflon (False)") 
        print("OJ reflector: detector (True) / teflon (False)")
        print("IJ reflector: detector (True) / teflon (False)")
        print("For detailed information, view comments of this file.")
        sys.exit(0)

    g = Geometry(cf4)
    pos0 = np.array([0,0,0])
    # this is the position of inner jar center relative to [0,0,0]
    # in my construction, I actually considered all the position relative to inner jar center
    pos1 = np.array([0,0,0.2225])
    # the distance between outer jar center and inner jar.

    # World
    World_solid = Solid(make.box(1,1,1),cf4,cf4,
                  color=0x33ffffff)
    g.add_solid(World_solid)
    # treat the PV as the world, a 1*1*1 cube centered at (0,0,0)

    # Inner Jar
    Ijout_mesh = stl.mesh_from_stl('Meshes/ij_out.stl')
    Ijin_mesh = stl.mesh_from_stl('Meshes/ij_in.stl')
    Ijout_solid = Solid(Ijout_mesh, quartz, argon)
    pos_ijout = pos0 - np.array([0,0,0.0001])
    rot_ij = rotation_matrix(0,0,0)
    g.add_solid(Ijout_solid, rot_ij, pos_ijout)
    Ijin_solid = Solid(Ijin_mesh, cf4, quartz)
    pos_ijin = pos0
    g.add_solid(Ijin_solid, rot_ij, pos_ijin)

    # Outer Jar
    # includes 2 layers: inside and outside.
    Ojout_mesh = stl.mesh_from_stl('Meshes/oj_out.stl')
    Ojin_mesh = stl.mesh_from_stl('Meshes/oj_in.stl')
    Ojout_solid = Solid(Ojout_mesh, quartz, cf4)
    pos_ojout = pos0 - np.array([0,0,0.0001])
    # make a bit room for distinction. moved outer part a bit lower
    rot_oj = rotation_matrix(0,0,0)
    g.add_solid(Ojout_solid, rot_oj, pos_ojout)
    Ojin_solid = Solid(Ojin_mesh, argon, quartz)
    pos_ojin = pos0
    g.add_solid(Ojin_solid, rot_oj, pos_ojin)

    # sapphire viewpoint
    """ currently only 1 viewpoint is set, needs improvement
    """
    Sapphire_mesh = stl.mesh_from_stl('Meshes/sapphire.stl')
    Sapphire_solid = Solid(Sapphire_mesh, sapphire, cf4, black_surface)
    rot_sapphire = rotation_matrix(22.5*np.pi/180, 0, 0)
    h_cone = 0.060325
    # pos_measure = np.array([0, (0.03750+0.02913+0.04603)/2+0.060325, (0.34097+0.38421)/2])
    # The measured position of head cone center(bottom), to zero point
    dx, dy, dz = 0.03910, 0.06772, 0.34958
    pos_measure = np.array([0, np.sqrt(dx*dx+dy*dy), dz])
    pos_sapphire = pos0 + pos_measure + np.array([0,h_cone*np.sin(22.5*np.pi/180),h_cone*np.cos(22.5*np.pi/180)])
    g.add_solid(Sapphire_solid, rot_sapphire, pos_sapphire)

    # head cones
    Head_mesh = stl.mesh_from_stl('Meshes/head_cone.stl')
    Head_solid = Solid(Head_mesh, cf4, cf4, black_surface) 
    # normal vector / optical axis: 28.16 degree to z axis
    # measured data above. Use 22.5 the design data instead.
    rot_head1 = rotation_matrix(22.5*np.pi/180, 0, 0)
    pos_head1 = pos_measure + pos0
    g.add_solid(Head_solid, rot_head1, pos_head1)
    rot_head2 = rotation_matrix(22.5*np.pi/180, 0, 2*np.pi/3)
    pos_head2 = np.dot(pos_head1, rotation_matrix(0,0,2*np.pi/3))
    g.add_solid(Head_solid, rot_head2, pos_head2)
    rot_head3 = rotation_matrix(22.5*np.pi/180, 0, 4*np.pi/3)
    pos_head3 = np.dot(pos_head1, rotation_matrix(0,0,4*np.pi/3))
    g.add_solid(Head_solid, rot_head3, pos_head3)

    # head reflectors
    Href_mesh = stl.mesh_from_stl('Meshes/head_ref.stl')
    if (id_number & 8):
        Href_solid = Solid(Href_mesh, cf4, cf4, detector_surface)
    else:
        Href_solid = Solid(Href_mesh, cf4, cf4, teflon_surface)
    l_deviation = 0.00025
    pos_href1 = pos_head1 - np.array([0, l_deviation*np.sin(22.5*np.pi/180),l_deviation*np.cos(22.5*np.pi/180)])
    pos_href2 = np.dot(pos_href1, rotation_matrix(0,0,2*np.pi/3))
    pos_href3 = np.dot(pos_href1, rotation_matrix(0,0,4*np.pi/3))
    g.add_solid(Href_solid, rot_head1, pos_href1)
    g.add_solid(Href_solid, rot_head2, pos_href2)
    g.add_solid(Href_solid, rot_head3, pos_href3)

    # dome reflectors
    # 8 pieces, thus treated in a for loop
    Dref_mesh = stl.mesh_from_stl('Meshes/dome_ref.stl')
    if (id_number & 4):
        Dref_solid = Solid(Dref_mesh, cf4, cf4, detector_surface)
    else:
        Dref_solid = Solid(Dref_mesh, cf4, cf4, teflon_surface)
    dr_dref = np.sqrt(0.01776 ** 2 + (0.07264+0.060325) ** 2) # difference in x-y plane
    dz_dref = 0.28018 # measured position in z
    t_plate = (-90 + 14.82) *np.pi/180 # slope of plate, 14.82 degree
    for i in range(8):
        pos_dref = np.array([dr_dref*np.cos(i*np.pi/4 + np.pi/2), dr_dref*np.sin(i*np.pi/4 + np.pi/2), dz_dref]) + pos0
        # the first plate must be placed at (0, dr, dz).
        rot_dref = rotation_matrix(t_plate, 0, -i*np.pi/4) 
        # every plate is originally in x-y plane, then rotated along z axis; 
        # to ensure coordination with position, let the rotation be counter-clockwise.
        g.add_solid(Dref_solid, rot_dref, pos_dref)
        #g.add_solid(SiPM(), rot_dref, pos_dref)
        # adding a sipm at each plate's center

    # Outer Jar reflector
    Oref_mesh = stl.mesh_from_stl('Meshes/oj_ref.stl')
    if (id_number & 2):
        Oref_solid = Solid(Oref_mesh, cf4, cf4, detector_surface)
    else:
        Oref_solid = Solid(Oref_mesh, cf4, cf4, teflon_surface)
    pos_oref = pos0
    g.add_solid(Oref_solid, rotation_matrix(0,0,0), pos_oref)

    # Inner jar reflector
    Iref_mesh = stl.mesh_from_stl('Meshes/ij_ref.stl')
    if (id_number & 1):
        Iref_solid = Solid(Iref_mesh, cf4, cf4, detector_surface)
    else:
        Iref_solid = Solid(Iref_mesh, cf4, cf4, teflon_surface)
    pos_iref = pos0
    g.add_solid(Iref_solid, rotation_matrix(0,0,0), pos_iref)

    # Add some bubbles
    bubble_solid = add_bubble()
    # note, the outer jar reflector r=0.12235; h=0.22225
    pos_bubble1 = np.array([0.12235/2, 0.12235/2, 0.22225/4])
    pos_bubble2 = np.array([0.12235/2, 0.12235/2, 0.22225/4*3])
    g.add_solid(bubble_solid, rotation_matrix(0,0,0), pos_bubble1)
    g.add_solid(bubble_solid, rotation_matrix(0,0,0), pos_bubble2)

    # ring of LED for reflection effect
    led_band_mesh = stl.mesh_from_stl('Meshes/led_band.stl')
    l_deviation = 0.0005
    pos_band = pos_measure - np.array([0,l_deviation*np.sin(22.5*np.pi/180),l_deviation*np.cos(22.5*np.pi/180)])
    #dir_band = np.array([0, -1*np.sin(22.5*np.pi/180), -1*np.cos(22.5*np.pi/180)])
    Led_band_solid = Solid(led_band_mesh, cf4, cf4, detector_surface)
    g.add_solid(Led_band_solid, rot_sapphire, pos_band)

    # adding sipms onto reflectors
    # oj reflector
    """
    dz_ojsipm = 0.2225 /4
    oj_r = 0.12235
    for i in range(8):
        pos_ojsipm = np.array([oj_r, 0, 0]) + pos0
        rot_ojsipm = rotation_matrix(0, 0, np.pi/4*i)
        g.add_solid(SiPM(), rot_ojsipm, pos_ojsipm)
        pos_ojsipm = pos_ojsipm + np.array([0,0,dz_ojsipm])
        g.add_solid(SiPM(), rot_ojsipm, pos_ojsipm)
        pos_ojsipm = pos_ojsipm + np.array([0,0,dz_ojsipm])
        g.add_solid(SiPM(), rot_ojsipm, pos_ojsipm)
        pos_ojsipm = pos_ojsipm + np.array([0,0,dz_ojsipm])
        g.add_solid(SiPM(), rot_ojsipm, pos_ojsipm)
    # ij reflector
    """
    return g

def detector_camera():
    g = Geometry(cf4)
    pos0 = np.array([0,0,0])
    # this is the position of inner jar center relative to [0,0,0]
    # in my construction, I actually considered all the position relative to inner jar center
    pos1 = np.array([0,0,0.2225])
    # the distance between outer jar center and inner jar.

    # World
    #World_mesh = make.cube(1)
    #World_solid = Solid(World_mesh, cf4, cf4, black_surface)
    World_solid = Solid(make.box(1,1,1),cf4,cf4,
                  color=0x33ffffff)
    g.add_solid(World_solid)
    # treat the PV as the world, a 2*2*2 cube centered at (0,0,0)

    # Inner jar
    Ijout_mesh = stl.mesh_from_stl('Meshes/ij_out.stl')
    Ijin_mesh = stl.mesh_from_stl('Meshes/ij_in.stl')
    Ijout_solid = Solid(Ijout_mesh, quartz, argon)
    pos_ijout = pos0 - np.array([0,0,0.0001])
    rot_ij = rotation_matrix(0,0,0)
    g.add_solid(Ijout_solid, rot_ij, pos_ijout)
    Ijin_solid = Solid(Ijin_mesh, cf4, quartz)
    pos_ijin = pos0
    g.add_solid(Ijin_solid, rot_ij, pos_ijin)

    # Outer jar
    Ojout_mesh = stl.mesh_from_stl('Meshes/oj_out.stl')
    Ojin_mesh = stl.mesh_from_stl('Meshes/oj_in.stl')
    Ojout_solid = Solid(Ojout_mesh, quartz, cf4)
    pos_ojout = pos0 - np.array([0,0,0.0001])
    # make a bit room for distinction. moved outer part a bit lower
    rot_oj = rotation_matrix(0,0,0)
    g.add_solid(Ojout_solid, rot_oj, pos_ojout)
    Ojin_solid = Solid(Ojin_mesh, argon, quartz)
    pos_ojin = pos0
    g.add_solid(Ojin_solid, rot_oj, pos_ojin)
    
    # Outer Jar reflector
    Oref_mesh = stl.mesh_from_stl('Meshes/oj_ref.stl')
    Oref_solid = Solid(Oref_mesh, cf4, cf4, detector_surface)
    pos_oref = pos0
    g.add_solid(Oref_solid, rotation_matrix(0,0,0), pos_oref)

    # Inner jar reflector
    Iref_mesh = stl.mesh_from_stl('Meshes/ij_ref.stl')
    Iref_solid = Solid(Iref_mesh, cf4, cf4, detector_surface)
    pos_iref = pos0
    g.add_solid(Iref_solid, rotation_matrix(0,0,0), pos_iref)

    # dome reflectors
    # 8 pieces, thus treated in a for loop
    Dref_mesh = stl.mesh_from_stl('Meshes/dome_ref.stl')
    Dref_solid = Solid(Dref_mesh, cf4, cf4, detector_surface)
    dr_dref = np.sqrt(0.01776 ** 2 + (0.07264+0.060325) ** 2) # difference in x-y plane
    dz_dref = 0.28018 # measured position in z
    t_plate = (-90 + 14.82) *np.pi/180 # slope of plate, 14.82 degree
    for i in range(8):
        pos_dref = np.array([dr_dref*np.cos(i*np.pi/4 + np.pi/2), dr_dref*np.sin(i*np.pi/4 + np.pi/2), dz_dref]) + pos0
        # the first plate must be placed at (0, dr, dz).
        rot_dref = rotation_matrix(t_plate, 0, -i*np.pi/4) 
        # every plate is originally in x-y plane, then rotated along z axis; 
        # to ensure coordination with position, let the rotation be counter-clockwise.
        g.add_solid(Dref_solid, rot_dref, pos_dref)
        #g.add_solid(SiPM(), rot_dref, pos_dref)
        # adding a sipm at each plate's center

    # sapphire viewpoint
    Sapphire_mesh = stl.mesh_from_stl('Meshes/sapphire.stl')
    Sapphire_solid = Solid(Sapphire_mesh, cf4, cf4, black_surface)
    h_cone = 0.060325
    # pos_measure = np.array([0, (0.03750+0.02913+0.04603)/2+0.060325, (0.34097+0.38421)/2])
    # The measured position of head cone center(bottom), to zero point
    rot_sapphire1 = rotation_matrix(22.5*np.pi/180, 0, 0)
    dx, dy, dz = 0.03910, 0.06772, 0.34958
    pos_measure = np.array([0, np.sqrt(dx*dx+dy*dy), dz])
    pos_sapphire1 = pos0 + pos_measure + np.array([0,h_cone*np.sin(22.5*np.pi/180),h_cone*np.cos(22.5*np.pi/180)])
    g.add_solid(Sapphire_solid, rot_sapphire1, pos_sapphire1)
    rot_sapphire2 = rotation_matrix(22.5*np.pi/180, 0, 2*np.pi/3)
    pos_sapphire2 = np.dot(pos_sapphire1, rotation_matrix(0,0,2*np.pi/3))
    g.add_solid(Sapphire_solid, rot_sapphire2, pos_sapphire2)
    rot_sapphire3 = rotation_matrix(22.5*np.pi/180, 0, 4*np.pi/3)
    pos_sapphire3 = np.dot(pos_sapphire1, rotation_matrix(0,0,4*np.pi/3))
    g.add_solid(Sapphire_solid, rot_sapphire3, pos_sapphire3)

    # head cones
    Head_mesh = stl.mesh_from_stl('Meshes/head_cone.stl')
    Head_solid = Solid(Head_mesh, cf4, cf4, black_surface) 
    # normal vector / optical axis: 28.16 degree to z axis
    # measured data above. Use 22.5 the design data instead.
    rot_head1 = rotation_matrix(22.5*np.pi/180, 0, 0)
    pos_head1 = pos_measure + pos0
    g.add_solid(Head_solid, rot_head1, pos_head1)
    rot_head2 = rotation_matrix(22.5*np.pi/180, 0, 2*np.pi/3)
    pos_head2 = np.dot(pos_head1, rotation_matrix(0,0,2*np.pi/3))
    g.add_solid(Head_solid, rot_head2, pos_head2)
    rot_head3 = rotation_matrix(22.5*np.pi/180, 0, 4*np.pi/3)
    pos_head3 = np.dot(pos_head1, rotation_matrix(0,0,4*np.pi/3))
    g.add_solid(Head_solid, rot_head3, pos_head3)

    # head reflectors
    Href_mesh = stl.mesh_from_stl('Meshes/head_ref.stl')
    Href_solid = Solid(Href_mesh, cf4, cf4, detector_surface)
    l_deviation = 0.00025
    pos_href1 = pos_head1 - np.array([0, l_deviation*np.sin(22.5*np.pi/180),l_deviation*np.cos(22.5*np.pi/180)])
    pos_href2 = np.dot(pos_href1, rotation_matrix(0,0,2*np.pi/3))
    pos_href3 = np.dot(pos_href1, rotation_matrix(0,0,4*np.pi/3))
    g.add_solid(Href_solid, rot_head1, pos_href1)
    g.add_solid(Href_solid, rot_head2, pos_href2)
    g.add_solid(Href_solid, rot_head3, pos_href3)

    """
    # adding sipms onto reflectors
    # oj reflector
    dz_ojsipm = 0.2225 /4
    oj_r = 0.12235
    for i in range(8):
        pos_ojsipm = np.array([oj_r, 0, 0]) + pos0
        rot_ojsipm = rotation_matrix(0, 0, np.pi/4*i)
        g.add_solid(SiPM(), rot_ojsipm, pos_ojsipm)
        pos_ojsipm = pos_ojsipm + np.array([0,0,dz_ojsipm])
        g.add_solid(SiPM(), rot_ojsipm, pos_ojsipm)
        pos_ojsipm = pos_ojsipm + np.array([0,0,dz_ojsipm])
        g.add_solid(SiPM(), rot_ojsipm, pos_ojsipm)
        pos_ojsipm = pos_ojsipm + np.array([0,0,dz_ojsipm])
        g.add_solid(SiPM(), rot_ojsipm, pos_ojsipm)
    # ij reflector"""

    return g

# Test geometry copied from chroma.doc
# this geometry is definite to function properly, which may be used in tests.
# it can also be a demo for geometry building.
def build_pd(size, glass_thickness):
    """Returns a simple photodetector Solid. The photodetector is a cube of
    size `size` constructed out of a glass envelope with a photosensitive
    face on the inside of the glass envelope facing up."""
    # outside of the glass envelope
    outside_mesh = make.cube(size)
    # inside of the glass envelope
    inside_mesh = make.cube(size-glass_thickness*2)

    # outside solid with water on the outside, and glass on the inside
    outside_solid = Solid(outside_mesh,glass,water)    

    # now we need to determine the triangles which make up
    # the top face of the inside mesh, because we are going to place
    # the photosensitive surface on these triangles
    # do this by seeing which triangle centers are at the maximum z
    # coordinate
    z = inside_mesh.get_triangle_centers()[:,2]
    top = z == max(z)

    # see np.where() documentation
    # Here we make the photosensitive surface along the top face of the inside
    # mesh. The rest of the inside mesh is perfectly absorbing.
    inside_surface = np.where(top,r7081hqe_photocathode,black_surface)
    inside_color = np.where(top,0x00ff00,0x33ffffff)

    # construct the inside solid
    inside_solid = Solid(inside_mesh,vacuum,glass,surface=inside_surface,
                         color=inside_color)

    # you can add solids and meshes!
    return outside_solid + inside_solid

def iter_box(nx,ny,nz,spacing):
    """Yields (position, direction) tuple for a series of points along the
    boundary of a box. Will yield nx points along the x axis, ny along the y
    axis, and nz along the z axis. `spacing` is the spacing between the points.
    """
    dx, dy, dz = spacing*(np.array([nx,ny,nz])-1)

    # sides
    for z in np.linspace(-dz/2,dz/2,nz):
        for x in np.linspace(-dx/2,dx/2,nx):
            yield (x,-dy/2,z), (0,1,0)
        for y in np.linspace(-dy/2,dy/2,ny):
            yield (dx/2,y,z), (-1,0,0)
        for x in np.linspace(dx/2,-dx/2,nx):
            yield (x,dy/2,z), (0,-1,0)
        for y in np.linspace(dy/2,-dy/2,ny):
            yield (-dx/2,y,z), (1,0,0)

    # bottom and top
    for x in np.linspace(-dx/2,dx/2,nx)[1:-1]:
        for y in np.linspace(-dy/2,dy/2,ny)[1:-1]:
            # bottom
            yield (x,y,-dz/2), (0,0,1)
            # top
            yield (x,y,dz/2), (0,0,-1)

def test_geometry():
    size = 1
    glass_thickness = 0.1
    nx, ny, nz = 10, 10, 10
    spacing = size*2
    """Returns a cubic detector made of cubic photodetectors."""
    g = Geometry(water)
    for pos, dir in iter_box(nx,ny,nz,spacing):
        # convert to arrays
        pos, dir = np.array(pos), np.array(dir)

        # we need to figure out what rotation matrix to apply to each
        # photodetector so that the photosensitive surface will be facing
        # `dir`.
        if tuple(dir) == (0,0,1):
            rotation = None
        elif tuple(dir) == (0,0,-1):
            rotation = make_rotation_matrix(np.pi,(1,0,0))
        else:
            rotation = make_rotation_matrix(np.arccos(dir.dot((0,0,1))),
                                            np.cross(dir,(0,0,1)))
        # add the photodetector
        g.add_solid(build_pd(size,glass_thickness),rotation=rotation,
                    displacement=pos)

    world = Solid(make.box(spacing*nx,spacing*ny,spacing*nz),water,vacuum,
                  color=0x33ffffff)
    g.add_solid(world)

    return g