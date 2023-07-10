import numpy as np
import random
import sys
from scipy.sparse import load_npz
import mathematics as m
import os

from chroma.event import Photons

"""
This file is a test file for self-made light sources. Also used as direct source for light source functions; 
be careful before editting.
The main function aims at interactively test any user-defined light source functions. 
Use mode number for interactive i/o: 
0 or none: print the current code list
1: point source
2: LED ring
3: Triple LED ring
4: Camera
5: Triple camera
"""

ring = (0.06985+0.12065/2)/2
delta = np.pi/12
LED_position_list = []
for i in range(24):
    x = ring * np.cos(i*delta)
    y = ring * np.sin(i*delta)
    z = 0
    LED_position_list.append([x,y,z])
LED_position_list = np.array(LED_position_list) # The LED positions

if (os.path.exists('Archived/led_list.npy')):
    led_list = np.load('Archived/led_list.npy').tolist()
else:
    led_list = 0
if (os.path.exists('mul_list.npy')):
    ind_list = np.load('mul_list.npy').tolist()
else:
    ind_list = 0
if (os.path.exists('mat_of_angle.npy')):
    ang_list = np.load('mat_of_angle.npy')
else:
    ang_list = 0
if (os.path.exists('pos_list.npy')):
    pos_list = np.load('pos_list.npy')
else:
    pos_list = 0
if (os.path.exists('plot.npz')):
    plot = load_npz('plot.npz').toarray()
    index_array = np.arange(np.shape(plot)[1])
else:
    plot = 0
# ===================================================================================

def generate_pol(row):
    # a quick function to generate polarization vector
    # should always be called by np.apply_along_axis()
    return np.cross(row, m.random_vector())

def photon_bomb(n,wavelength,pos):
    """
    chroma example light source. recieves an integer, float, and a tuple.
    Class Photon( n*3, normalized n*3, normalized n*3, n )
    For more details, refer to chroma.event
    """
    from chroma.sample import uniform_sphere
    pos = np.tile(pos,(n,1))
    dir = uniform_sphere(n)
    pol = np.cross(dir,uniform_sphere(n))
    wavelengths = np.repeat(wavelength,n)
    return Photons(pos,dir,pol,wavelengths)

def point_source(wavelength, n, pos, dir = (0,0,1)):
    """
    n photons in total emitting from points (pos), with angles restricted in a half
    accepts multiple points input, they will be evenly cycled.
    dir is the direction of source - the default is the direction of Z axis here
    thus, this function will generate photons with respect to a certain direction
    """
    n = int(n)
    pos = np.array(pos)
    dir = np.array(dir)
    if (dir.ndim != 1):
        raise Exception("dir input dimension larger than 1! Not supported now.")
    normal_theta, normal_phi = m.get_angles(dir)
    normal_rotation = m.rotation_matrix(normal_theta, 0, - (normal_phi-np.pi/2))

    pos_list = []
    if (pos.ndim == 1):
        pos_list.append(pos)
    elif (pos.ndim == 2):
        pos_list.append(pos[0])
    else: 
        raise Exception("Invalid photon position input!")
    dir_list = [np.dot(m.random_vector(), normal_rotation)]
    pol_list = [np.cross(dir_list[0], m.random_vector())]

    while len(pos_list)<n:
        if (pos.ndim == 1):
            pos_list.append(pos)
            dirvec = np.dot(m.random_vector(), normal_rotation)
            dir_list.append(dirvec)
            pol_list.append(np.cross(dirvec, m.random_vector()))
        else:
            for i in range(len(pos)): # run a loop to cycle around the Positions
                pos_list.append(pos[i])
                dirvec = np.dot(m.random_vector(), normal_rotation)
                dir_list.append(dirvec)
                pol_list.append(np.cross(dirvec, m.random_vector()))
                if (len(pos_list)==n): 
                    break

    pos_photon = np.array(pos_list)
    dir_photon = np.array(dir_list)
    pol_photon = np.array(pol_list)
    wavelengths = np.repeat(wavelength,n)
    return Photons(pos_photon, dir_photon, pol_photon, wavelengths)

def select_angle(row):
    #row = row.tolist()
    #row_real = row[row!=0]
    row_real = row[np.nonzero(row)]
    if len(row_real)==0:
        return 0
    return np.random.choice(row_real)

def reflector_emission(wavelength, n):
    """
    generate re-emitted photons by diffuse reflection.
    for each photon, pos is selected in the position list generated by 'multiplicity'; 
    dir is selected in the corresponding 'theta-phi plot'.
    Below is the illustrative code exposing the method....
    upgraded to the numpy-compatible version

    len_angle = np.shape(plot)[1]
    for i in range(n):
        # generate selected pos and dir
        ind_select = np.random.choice(ind_list)
        pos_select = pos_list[ind_select]
        plt = plot[ind_select].tolist()
        ang_select = int(random.random()*len_angle)
        while (plt[ang_select]!=True):
            ang_select = int(random.random()*len_angle)
        dir_select = -ang_list[ang_select]
        pos.append(pos_select)
        dir.append(dir_select)
        pol.append(np.cross(dir_select, m.random_vector()))
    """

    ind_select = np.random.choice(ind_list, n)
    pos = np.take(pos_list, ind_select, axis=0)

    plt = np.take(plot, ind_select, axis=0) *index_array
    ang_select = np.apply_along_axis(select_angle, 1, plt)
    mis = len(ang_select)-len(ang_select[np.nonzero(ang_select)])
    if mis:
        print('Alert: Photons mismatch: '+str(mis))
    dir = np.take(-ang_list, ang_select, axis=0)
    
    pol = np.apply_along_axis(generate_pol, 1, dir)
    wavelengths = np.repeat(wavelength, n)
    return Photons(pos, dir, pol, wavelengths)

def reflector_patch(wavelength, n):
    """
    A function follows reflector_emission with a fixed patch- used to test and 
    check the focus in analysis
    """
    dir = []
    pol = []

    # selected pos and dir, pos should be fixed
    ind_select = np.random.choice(ind_list)
    pos = np.take(pos_list, np.repeat(ind_select, n), axis=0)
    plt = np.take(plot, ind_select, axis=0) *index_array

    plt_real = plt[np.nonzero(plt)]
    ang_select = np.random.choice(plt_real, n)
    mis = len(ang_select)-len(ang_select[np.nonzero(ang_select)])
    if mis:
        print('Alert: Photons mismatch: '+str(mis))
    dir = np.take(-ang_list, ang_select, axis=0)

    pol = np.apply_along_axis(generate_pol, 1, dir)
    wavelengths = np.repeat(wavelength, n)
    return Photons(pos, dir, pol, wavelengths)

def generate_direction_led(normalvec):
    normal_theta, normal_phi = m.get_angles(normalvec)
    normal_rotation = m.rotation_matrix(normal_theta, 0, - (normal_phi-np.pi/2))
    dir_led = np.dot(m.random_vector_list(led_list), normal_rotation)
    return dir_led

def LED_point_source(n, pos, dir = (0,0,1)):
    """
    Same function with point_source() but with special angular distribution
    using random_vector_list(). Should not be called directly; 
    take in the position list and direction list of LEDs, return n evenly generated
    random photons. 
    """
    n = int(n)
    pos = np.array(pos).reshape(-1,3) # no matter the input, reshaped as n*3 array
    dir = np.array(dir).reshape(-1,3) # then use ndim to check shape
    # check the shape of both pos and dir
    if (pos.ndim == 1):
        pos_len = 1
    elif (pos.ndim == 2):
        pos_len = len(pos)
    else: 
        raise Exception("Invalid photon position input!")

    if (dir.ndim == 1):
        dir_len = 1
    elif (dir.ndim == 2):
        dir_len = len(dir)
    else: 
        raise Exception("Invalid photon direction input!")
    
    if (dir_len == pos_len):
        dir_led = dir
        pos_led = pos
        length = dir_len
    elif (dir_len % pos_len ==0):
        rep = dir_len // pos_len
        dir_led = dir
        pos_led = np.concatenate([pos]*rep)
        length = dir_len
    elif (pos_len % dir_len ==0):
        rep = pos_len // dir_len
        dir_led = np.concatenate([dir]*rep)
        pos_led = pos
        length = pos_len
    else: 
        raise Exception("Size of photon direction and position doesn't match!")

    if (n<length):
        pos_photon = np.take(pos_led, range(n), axis=0)
        dir_photon = np.take(dir_led, range(n), axis=0)
        dir_photon = np.apply_along_axis(generate_direction_led, 1, dir_photon)
        pol_photon = np.apply_along_axis(generate_pol, 1, dir_photon)
        return pos_photon, dir_photon, pol_photon
    num = n // length
    res = n % length

    pos_photon = np.concatenate([pos_led]*num)
    pos_photon = np.append(pos_photon, np.take(pos_led, range(res), axis=0), axis=0)
    dir_photon = np.concatenate([dir_led]*num)
    dir_photon = np.append(dir_photon, np.take(dir_led, range(res), axis=0), axis=0)
    dir_photon = np.apply_along_axis(generate_direction_led, 1, dir_photon)
    pol_photon = np.apply_along_axis(generate_pol, 1, dir_photon)

    return pos_photon, dir_photon, pol_photon

def LED_ring(wavelength, n, pos, dir):
    """
    n photons emitting photons evenly from 24 LEDs arranged in a ring
    use pos,dir as the position of center and the normal vector of the ring.
    """
    n = int(n)
    pos = np.array(pos) # a list of 3d vectors
    dir = np.array(dir) # (x,y,z) array
    if ((pos.ndim !=1) or (pos.size != 3)):
        raise Exception("Invalid input position for LED center!")
    if ((dir.ndim !=1) or (dir.size != 3)):
        raise Exception("Invalid direction for LED normal plane!")
    # obtain the angles of normal vector
    theta, phi = m.get_angles(dir)
    
    # position matrices for 24 LEDs
    pos_led = np.dot(LED_position_list, m.rotation_matrix(theta, 0, - (phi-np.pi/2))) + pos

    pos_photon, dir_photon, pol_photon = LED_point_source(n, pos_led, dir)
    wavelengths = np.repeat(wavelength, n)

    return Photons(pos_photon, dir_photon, pol_photon, wavelengths)

def triple_LED_ring(wavelength, n, pos, dir):
    """ Following the same logic with single LED ring.  """ 
    # the function used for 3 LEDs, the input parameters are the same with LED1
    # but with LED1 rotated 3/pi each time
    num = n // 3
    res = n % 3

    # obtain the angles of normal vector
    theta, phi = m.get_angles(dir)
    
    # position matrices for 24 LEDs
    pos_led1 = np.dot(LED_position_list, m.rotation_matrix(theta, 0, - (phi-np.pi/2))) + pos
    pos_led2 = np.dot(pos_led1, m.rotation_matrix(0,0,np.pi/3*2))
    dir2 = np.dot(dir, m.rotation_matrix(0,0,np.pi/3*2))
    pos_led3 = np.dot(pos_led2, m.rotation_matrix(0,0,np.pi/3*2))
    dir3 = np.dot(dir2, m.rotation_matrix(0,0,np.pi/3*2))

    pos_photon1, dir_photon1, pol_photon1 = LED_point_source(num +res, pos_led1, dir)
    pos_photon2, dir_photon2, pol_photon2 = LED_point_source(num, pos_led2, dir2)
    pos_photon3, dir_photon3, pol_photon3 = LED_point_source(num, pos_led3, dir3)

    pos_photon = np.concatenate([pos_photon1, pos_photon2, pos_photon3])
    dir_photon = np.concatenate([dir_photon1, dir_photon2, dir_photon3])
    pol_photon = np.concatenate([pol_photon1, pol_photon2, pol_photon3])
    wavelengths = np.repeat(wavelength, n)

    return Photons(pos_photon, dir_photon, pol_photon, wavelengths)

def camera_source(wavelength, n, pos, dir):
    """
    Generate n photons randomly on the camera surface.
    pos: the center of camera; dir: the normal vector
    random points in within a circle will be chosen. 
    """
    n = int(n)
    pos = np.array(pos) # a list of 3d vectors
    dir = np.array(dir) # (x,y,z) array
    if ((pos.ndim !=1) or (pos.size != 3)):
        raise Exception("Invalid input position for camera center!")
    if ((dir.ndim !=1) or (dir.size != 3)):
        raise Exception("Invalid direction for camera normal plane!")
    
    # obtain the angles of normal vector
    theta, phi = m.get_angles(dir)
    # radius of viewpoint
    r_camera = 0.03647 / 2
    # generate n random points on the viewpoint surface
    points = m.generate_circle(r_camera, n)
    pos_light = np.dot(points, m.rotation_matrix(theta, 0, - (phi-np.pi/2))) + pos

    return point_source(wavelength, n, pos_light, dir)

def triple_camera(wavelength, n):
    """ unfinished trial of triple camera source - may be updated with single cam source """
    rot_camera_1 = m.rotation_matrix(22.5*np.pi/180, 0, 0)
    pos_camera_1 = np.array([(0.03750+0.02913+0.04603)/2+0.060325, 0, (0.34097+0.38421)/2])
    rot_camera_2 = m.rotation_matrix(22.5*np.pi/180, 0, np.pi/3)
    pos_camera_2 = np.dot(pos_camera_1,m.rotation_matrix(0,0,np.pi/3))
    rot_camera_3 = m.rotation_matrix(22.5*np.pi/180, 0, 2*np.pi/3)
    pos_camera_3 = np.dot(pos_camera_1,m.rotation_matrix(0,0,2*np.pi/3))
    r_camera = 0.03647 / 2
    pos_light = []
    for i in range(n):
        rnd = random.random()*3
        if (rnd<1):
            vec = np.dot(np.array(r_camera * m.random_vector_2d()), rot_camera_1) + pos_camera_1
            pos_light.append(vec)
        elif (rnd<2):
            vec = np.dot(np.array(r_camera * m.random_vector_2d()), rot_camera_2) + pos_camera_2
            pos_light.append(vec)
        else:
            vec = np.dot(np.array(r_camera * m.random_vector_2d()), rot_camera_3) + pos_camera_3
            pos_light.append(vec)
    pos_light = np.array(pos_light)
    dir_light = np.array([0,0,-1])

    return point_source(wavelength, n, pos_light, dir_light)

def mode_to_source(batch_number, wavelength, position = (0,0,0), direction = (0,0,1), mode = 0):
    """ intended overload function for external use. aborted and needs updating. """
    batch_number = int(batch_number)

    if mode == 0:
        print("Zero mode: mode number information")
        print("1: point source")
        print("2: LED ring")
        print("3: Triple LED ring")
        print("4: Camera")
        print("5: Triple camera")
    elif mode == 1:
        return point_source(wavelength, batch_number, position, direction)
    elif mode == 2:
        return LED_ring(wavelength, batch_number, position, direction)
    elif mode == 3:
        return triple_LED_ring(wavelength, batch_number, position, direction)
    elif mode == 4:
        return camera_source(wavelength, batch_number, position, direction)
    elif mode == 5:
        return triple_camera(wavelength, batch_number)
    else:
        raise Exception("Invalid mode number! Try mode=0 for info.")

def traced_photon(pixel, n, wavelength):
    """ The final version of camera simulation source """
    # generate a set of photons determined by camera: 
    # pos: determined by pixel(i,j)
    # dir: calculated by "endpoint" and pos

    # Pixel total number: 800*1280. For each (i,j), generate n (supposedly 1000) photons.
    # The valid range should be i(0,800) j(0,1280)
    """ The math in analysis file:
    for i in range(len(pos_new)):
        p = pos_new[i] / R
        d = dir_new[i]
        ip = np.dot(p,d) #inner product
        l_value = ip + np.sqrt(ip*ip +1-sum(p*p))
        vec = - (p - l_value*d)
        theta,phi = get_angles(vec)
        #theta = np.arctan(np.sqrt(x*x+y*y)/abs(z))
        #phi = np.arctan(abs(y)/abs(x))
        i1 = i0 + int(f*theta / p_value *np.cos(phi))
        j1 = j0 + int(f*theta / p_value *np.sin(phi))
        i_list.append(i1)
        j_list.append(j1)
    """
    dx, dy, dz = 0.03910, 0.06772, 0.34958
    h_cone = 0.060325
    pos_measure = np.array([0, np.sqrt(dx*dx+dy*dy), dz])
    pos_sapphire = pos_measure + np.array([0,h_cone*np.sin(22.5*np.pi/180),h_cone*np.cos(22.5*np.pi/180)])
    rotation = m.rotation_matrix(22.5/180*np.pi,0,0)

    i0 = 200
    j0 = 320
    i,j = pixel
    i_generate = np.random.rand(n) + i -i0
    j_generate = np.random.rand(n) + j -j0
    p_value = 0.000006 # scale of a pixel, 3um
    f = 0.00165
    #d_value = 0.03647 # r of window
    #d_value = 0.0184 # the effective aperture
    d_value = 0.00165 / 2.8 /2 # the small iris using f-number (radius)

    r = np.sqrt(np.random.rand(n)) *d_value
    t = np.random.rand(n) *np.pi*2
    x = r * np.cos(t)
    y = r * np.sin(t)
    z = np.zeros(n)
    pos_relative = np.transpose([x,y,z])

    x_pixel = i_generate*p_value
    y_pixel = j_generate*p_value
    z_pixel = np.repeat(f, n)
    vector_image = np.transpose([x_pixel, y_pixel, z_pixel])
    #theta, phi = m.get_angles_array(vector_image)
    focus_distance = 0.3
    vector_focal = np.apply_along_axis(m.normalize, 1, vector_image) * focus_distance
    vector_dir = np.apply_along_axis(m.normalize, 1, vector_focal-pos_relative)

    pos_camera = np.dot(pos_relative, rotation) + pos_sapphire
    dir_camera = np.dot(-vector_dir, rotation)
    pol_camera = np.apply_along_axis(generate_pol, 1, dir_camera)
    wavelengths = np.repeat(wavelength,n)
    return Photons(pos_camera, dir_camera, pol_camera, wavelengths)


if __name__ == '__main__':
    """
    A quick sim to test the source functions.
    """
    import detector_construction
    from chroma.sim import Simulation
    from chroma.loader import load_bvh

    max_mode = 5
    if len(sys.argv)==1:
        mode = 0
    elif (int(sys.argv[1]) > max_mode):
        raise Exception("Invalid mode number! Try mode=0 for info.")
    else:
        mode = int(sys.argv[1])

    g = detector_construction.test_geometry() # the detector is not influenced by the mode
    g.flatten()
    g.bvh = load_bvh(g)
    sim = Simulation(g)

    namestr = 'source_'+str(mode)
    test_position = (0,0,0)
    test_direction = (0,0,1)
    position_list = []
    length_of_batch = 1000
    for i in range(1):
        for j in range(10):
            for ev in sim.simulate([mode_to_source(length_of_batch,400,test_position,test_direction, mode)],
                           keep_photons_beg=True,keep_photons_end=False,
                           run_daq=False,max_steps=20):
                position_list.append(ev.photons_beg.pos[:])
    # note here, we choose the beginning position to check the source
    pos_data = np.concatenate(position_list[:], axis=0)
    namestr = namestr + '_position'
    np.save(namestr, pos_data)