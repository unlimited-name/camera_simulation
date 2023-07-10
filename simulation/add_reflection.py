import numpy as np
import mathematics as m
illu_array = np.load('illumination_map.npy')

""" Add the LED positions into illumination map, trying to simulate direct reflection
Basic idea: manually add the light intensity in illumination map, at the space chunks with LED position
"""

def search_illumination(position):
# input position, and search the illumination map to see if it is 'visible'
# i.e. already illuminated. 
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
    return illu.astype(bool)

def add_illumination(position):
    x,y,z = (position*1000).astype(int)
    x += 200
    y += 200
    if (x>=400 or x<0):
        print('Addition failed!')
    elif (y>=400 or y<0):
        print('Addition failed!')
    elif (z>=400 or z<0):
        print('Addition failed!')
    else:
        illu_array[(x,y,z)] += 10000
        print('Addition Success!')
    return

ring = (0.06985+0.12065/2)/2
delta = np.pi/12
LED_position_list = []
for i in range(24):
    x = ring * np.cos(i*delta)
    y = ring * np.sin(i*delta)
    z = 0
    LED_position_list.append([x,y,z])
LED_position_list = np.array(LED_position_list)

dx, dy, dz = 0.03910, 0.06772, 0.34958
pos_measure = np.array([0, np.sqrt(dx*dx+dy*dy), dz])
l_deviation = 0.0005
pos_center = pos_measure - np.array([0,l_deviation*np.sin(22.5*np.pi/180),l_deviation*np.cos(22.5*np.pi/180)])
dir_center = np.array([0, -1*np.sin(22.5*np.pi/180), -1*np.cos(22.5*np.pi/180)])

theta, phi = m.get_angles(dir_center)
pos_led = np.dot(LED_position_list, m.rotation_matrix(theta, 0, - (phi-np.pi/2))) + pos_center # the final position of LEDs

if __name__ == '__main__':
    search = np.apply_along_axis(search_illumination, 1, pos_led)
    print('Search result:')
    print(search)
    np.apply_along_axis(add_illumination, 1, pos_led)
    np.save('illumination_map.npy', illu_array)