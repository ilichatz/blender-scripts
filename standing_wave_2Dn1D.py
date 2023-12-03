import bpy
# easybpy is an add-on. Install it first or disable it. 
import easybpy as eb  

from mathutils import Euler
import math
pi = math.pi
import random

import time
then = time.time()


# set some functions for random coloring later
def random_color():
    "pick a random color"
    red = random.random()        
    green = random.random()        
    blue = random.random()        
    alpha = 1.0
    color = (red, green, blue, alpha)
    return color

def random_material(color):
    "pick a random material"
    material = bpy.data.materials.new("random_material")
    material.diffuse_color = color
    return material
    

# clean up the scene and memory from previous runs (eb is an add-on)
# comment the following three lines if you haven't install it 
eb.select_all_objects()
eb.delete_selected_objects()
eb.clear_unused_data()

# set up discretization of elastic medium
start_x = -1.5
end_x = 1.5
dx = end_x - start_x
start_y = -2
end_y = 2
dy = end_y - start_y
#keep z values equal to 0 because it is the axis of oscillation
#start_z = 0
#end_z = 0
#dz = end_z - start_z

length = math.sqrt(dx**2 + dy**2) 
x_points = 30
y_points = 30 # make this parameter(or previous) equal to 1 for 1-D standing wave
points = x_points * y_points

# turn all the x-y distribution of point "masses" by an angle theta (pivot around origin)
theta = 45      # in degrees
theta = math.radians(theta)     # converted in radians
rot_mat = Euler((0, 0, theta)).to_matrix().to_4x4()

# determine the offset (step size) in each axis
if (x_points != 1):
    x_offset = dx/(x_points-1)
else:
    x_offset = 0        
if (y_points != 1):
    y_offset = dy/(y_points-1)
else:
    y_offset = 0
# size of point "masses"
size = 0.05


bpy.context.scene.render.fps = 30
fps = bpy.context.scene.render.fps
# Set up parameters of traveling waves that created the standing wave
amplitude = 0.2   # in [m]
lambd = 4.     # in [m]

physical_period = 5     # in [s]
period = physical_period * fps # in [number of frames per period]
frequency = 1 / period  # in [Hz]/frame

kappa = 2 * pi / lambd  # in [rad/m]
omega = 2 * pi * frequency  # in [rad/s]/frame


# Main loop for creating point "masses" and setting drivers
for i in range(x_points):
    # create point "masses"
    x = start_x + i*x_offset    
    for j in range(y_points):
        y = start_y + j*y_offset

        bpy.ops.mesh.primitive_ico_sphere_add(radius=size, location=(x,y,0))
        
        # create and edit a driver for moving each point mass properly
        obj = eb.active_object()        
        my_driver = obj.driver_add('location', 2)
        # compute distance from origin
        dist = math.sqrt((x - start_x)**2 + (y - start_y)**2 )
        sf = f'2*{amplitude}*cos({kappa}*{dist}) * sin({omega}*frame)'
        my_driver.driver.expression = sf 
        
        
        # the code below is intended in a later version to change color dynamically...
        # for now it is a random choice
        color = random_color()
        mat = random_material(color)
        # add the material to the object
        obj.data.materials.append(mat)

        # don't forget to turn around z-axis!
        bpy.context.object.matrix_world = rot_mat @ bpy.context.object.matrix_world

# count running time of script
now = time.time()
dt = now - then
print(f'Runtime: {dt} seconds for \n N = {x_points}*{y_points} = {points} points totally')
