import numpy as np
from IPython.display import clear_output

#Function which distributes n_seeds (a numper of points) equally within a lists
#of points to obtain furthest point sampling.

#The function takes in a list of points. Every entry in the list contains both the
#x and y coordinate of a given point. It returns the coordinates of the selected
#sample points
def fps(points, n_seeds):
    """
    https://minibatchai.com/ai/2021/08/07/FPS.html
    points: [N, 3] array containing the whole point cloud
    n_seeds: samples you want in the sampled point cloud typically << N
    """
    points = np.array(points)

    # Represent the points by their indices in points
    points_left = np.arange(len(points)) # [P]

    # Initialise an array for the sampled indices
    sample_inds = np.zeros(n_seeds, dtype='int') # [S]

    # Initialise distances to inf
    dists = np.ones_like(points_left) * float('inf') # [P]

    # Select a point from points by its index, save it
    selected = 0
    sample_inds[0] = points_left[selected]

    # Delete selected
    points_left = np.delete(points_left, selected) # [P - 1]

    # Iteratively select points for a maximum of n_seeds
    for i in range(1, n_seeds):
        # Find the distance to the last added point in selected
        # and all the others
        last_added = sample_inds[i-1]

        dist_to_last_added_point = (
            (points[last_added] - points[points_left])**2).sum(-1) # [P - i]

        # If closer, updated distances
        dists[points_left] = np.minimum(dist_to_last_added_point,
                                        dists[points_left]) # [P - i]

        # We want to pick the one that has the largest nearest neighbour
        # distance to the sampled points
        selected = np.argmax(dists[points_left])
        sample_inds[i] = points_left[selected]

        # Update points_left
        points_left = np.delete(points_left, selected)

    return points[sample_inds]


def voronoi(array_2D, n_seeds):
    p_x = np.arange(0,array_2D.shape[1])
    p_y = np.arange(0,array_2D.shape[0])
    points = np.zeros([len(p_x)*len(p_y),2])
    c = 0
    for i in p_x:
        for j in p_y:
            points[c, 0] = i
            points[c, 1] = j
            c += 1
    domains = []
    for i in range(n_seeds):
        domains.append([])

    temp = fps(points, n_seeds)
    seeds = []
    for i in range(len(temp)):
        # The selected seed points are converted for faster calculations later
        seeds.append(temp[i,0] + temp[i,1]*1j)
    #The same is done for the rest of the points_left

    points = list(points[:,0] +  points[:,1]*1j)

    for i in range(len(points)):
        if i%1000 == 0:
            clear_output(wait=True)
            print('Partitioning array: ' + str(round(100*(i+1)/len(points), 1)) + '%')
        distance = []
        for j in range(n_seeds):
            distance.append(abs(points[i]-seeds[j]))
        shortest_dist = np.where(distance == np.min(distance))
        domains[shortest_dist[0][0]].append(points[i])

    clear_output(wait=True)
    print('Partitioning image: 100%')

    return domains, seeds
