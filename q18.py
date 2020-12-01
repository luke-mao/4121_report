import numpy as np 
import math


def get_sphere_volume(radius, dimension):
    return math.pi**(dimension/2) / math.gamma(dimension/2 + 1)


def get_cube_volume(edge_length, dimension):
    return pow(edge_length, dimension)


def is_in_sphere(coordinate, radius):
    return np.sum(np.square(coordinate)) <= radius 


def is_in_cube(coordinate, cube_edge):
    return np.max(np.absolute(coordinate)) <= cube_edge / 2


def is_in_both_cube_and_sphere(coordinate, radius, cube_edge):
    return is_in_cube(coordinate, cube_edge) and is_in_sphere(coordinate, radius)


def random_coordinate_in_cube_and_sphere(dimension, choice, radius):
    # return a numpy array of randomly chosen coordinate from choice
    # choice is a list of possible coordinate
    # the coordinate must be inside both S_i and R
    index = None 
    coordinate = None 

    # coordinate is chosen from S_i, so only need to check if it is in R
    while (index is None) or (not is_in_sphere(coordinate, radius)):
        index = np.random.randint(low=0, high=len(choice), size=(dimension,))
        coordinate = choice[index]

    return index, coordinate


def random_walk_get_ratio(dimension, choice, sphere_radius, prev_edge, cur_edge, cycles):
    # randomly chose a point inside both cube(edge_i2) and the sphere 
    index, coordinate = random_coordinate_in_cube_and_sphere(dimension, choice, sphere_radius)

    # count the number of points in cube(edge_i) and the sphere
    count = 0

    # random walk
    for i in range(cycles):
        # check if the point is also in the inner cube and the sphere
        if is_in_both_cube_and_sphere(coordinate, sphere_radius, prev_edge):
            count += 1
        
        # random walk
        new_index, new_coordinate = random_walk(dimension, choice, index, coordinate)
        # if not in the set, stay put and repeat
        while ((new_coordinate is None) or (not is_in_sphere(new_coordinate, sphere_radius))) and i < cycles:
            i += 1
            new_index, new_coordinate = random_walk(dimension, choice, index, coordinate)
        
        # if in the set, move to the neighbour and continue
        if i == cycles:
            break 

        index, coordinate = new_index, new_coordinate   

    ratio = count / cycles 
    return ratio 


def random_walk(dimension, choice, current_index, current_coordinate):
    # random walk through all dimension, 2 direction
    # total 2*dimension neighbours
    # notice potential IndexError
    # return the new numpy array of coordinate, or None indicating the index error

    walk = np.random.randint(low=-1, high=1+1, size=np.shape(current_index))
    new_index = current_index + walk 

    try:
        new_coordinate = choice[new_index]
        return new_index, new_coordinate
    except IndexError:
        return new_index, None 


# constant for test environment
tests = 20
cycles = 10000

# define some constants
dimension = 20
spacing = 0.1 
sphere_radius = 1
sphere_volume = get_sphere_volume(sphere_radius, dimension) 

# find the a list of cube edges
# so the smallest cube is contained by R
# and the largest cube contains R
# for a cube with edge length L, check the most distant coordinate with (L/2, L/2 ....)
edge_min = 0.1
edge_max = edge_min + spacing 

while True:
    coordinate = np.array([edge_max/2] * dimension)
    if not is_in_sphere(coordinate, sphere_radius):
        break
    else:
        edge_max += spacing 


# cube(edge_min) is contained by R
# cube(edge_max) is the minimum cube that contains R
# enlarge a bit for the edge_max by doubling it
edge_max *= 2

edge = np.arange(edge_min, edge_max+spacing/2, spacing)
num_cubes = len(edge)


# variable to record the mininum percentage error, and the volume
final_volume = None 
final_percentage_error = None 


for ii in range(tests):    
    # so need to find all ratio, find ratio in ascending order of edge length
    volume = get_cube_volume(edge[0], dimension)

    for i in range(1, num_cubes):
        cur_edge = edge[i]
        prev_edge = edge[i-1]

        # coordinate range, reduce the space here to increase the hit
        choice = np.arange(-cur_edge/2, cur_edge/2+spacing/20, spacing/10)
        ratio = random_walk_get_ratio(dimension, choice, sphere_radius, prev_edge, cur_edge, cycles)

        while ratio == 0:
            ratio = random_walk_get_ratio(dimension, choice, sphere_radius, prev_edge, cur_edge, cycles)

        volume /= ratio 


    # compare the percentage error
    percentage_error = abs(volume - sphere_volume) / sphere_volume * 100   
    if final_percentage_error is None or final_percentage_error > percentage_error:
        final_percentage_error = percentage_error
        final_volume = volume 

    # print current test result
    print("Test {}: volume = {:.3f}, percentage error = {:.2f}%".format(ii, volume, percentage_error))


print("------Test Summary------")
print("Dimension = {}".format(dimension))
print("Volume of sphere is estimated as {:.3f}".format(final_volume))
print("Exact volume is {:.3f}".format(sphere_volume))
print("Percentage of error = {:.2f}%".format(final_percentage_error))

