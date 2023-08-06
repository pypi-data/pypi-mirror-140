import numpy as np

"""
This function is used along with resizing images from RGB and thermal camera
During the resizing, some gaps might appear, where some pixels are not given a new
value and therefore have a value of zero. This function finds these pixels and
replaces them with the average of their non-zero neighbors.
"""

def remove_zeros(matrix_2D):
    matrix_2D_copy = np.copy(matrix_2D)
    for i in range(matrix_2D.shape[0]):
        for j in range(matrix_2D.shape[1]):
            if matrix_2D_copy[i,j] == 0:
                matrix_2D_copy[i,j] = avg_neighbors(matrix_2D, i, j)
            else:
                matrix_2D_copy[i,j] = matrix_2D[i,j]
    return matrix_2D_copy

"""
Calculate the average of all non-zero neighbors
"""

def avg_neighbors(matrix_2D, row, col):
    avg = 0
    #Upper left
    if row == 0 and col == 0:
        temp_vals = np.array([matrix_2D[0, 1], matrix_2D[1, 1], matrix_2D[1, 0]])
        temp_vals = temp_vals[temp_vals > 0]
        avg = np.mean(temp_vals)
    #Upper right
    elif row == 0 and col == matrix_2D.shape[1]-1:
        temp_vals = np.array([matrix_2D[1, col], matrix_2D[1, col-1], matrix_2D[0, col-1]])
        temp_vals = temp_vals[temp_vals > 0]
        avg = np.mean(temp_vals)
    #Lower left
    elif row == matrix_2D.shape[0]-1 and col == 0:
        temp_vals = np.array([matrix_2D[row-1, 0], matrix_2D[row-1, 1], matrix_2D[row, 1]])
        temp_vals = temp_vals[temp_vals > 0]
        avg = np.mean(temp_vals)
    #Lower right
    elif row == matrix_2D.shape[0]-1 and col == matrix_2D.shape[1]-1:
        temp_vals = np.array([matrix_2D[row, col-1], matrix_2D[row-1, col-1], matrix_2D[row-1, col]])
        temp_vals = temp_vals[temp_vals > 0]
        avg = np.mean(temp_vals)
    #Leftmost column
    elif col == 0:
        temp_vals = np.array([matrix_2D[row-1, col], matrix_2D[row-1, col+1], matrix_2D[row, col+1], matrix_2D[row+1, col+1], matrix_2D[row+1, col]])
        temp_vals = temp_vals[temp_vals > 0]
        avg = np.mean(temp_vals)
    #Rightmost column
    elif col == matrix_2D.shape[1]-1:
        temp_vals = np.array([matrix_2D[row-1, col], matrix_2D[row-1, col-1], matrix_2D[row, col-1], matrix_2D[row+1, col-1], matrix_2D[row+1, col]])
        temp_vals = temp_vals[temp_vals > 0]
        avg = np.mean(temp_vals)
    #Upper row
    elif row == 0:
        temp_vals = np.array([matrix_2D[row, col+1], matrix_2D[row+1, col+1], matrix_2D[row+1, col], matrix_2D[row+1, col-1], matrix_2D[row, col-1]])
        temp_vals = temp_vals[temp_vals > 0]
        avg = np.mean(temp_vals)
    #Bottom row
    elif row == matrix_2D.shape[0]-1:
        temp_vals = np.array([matrix_2D[row, col+1], matrix_2D[row-1, col+1], matrix_2D[row-1, col], matrix_2D[row-1, col-1], matrix_2D[row, col-1]])
        temp_vals = temp_vals[temp_vals > 0]
        avg = np.mean(temp_vals)
    else:
        temp_vals = np.array([matrix_2D[row, col+1], matrix_2D[row-1, col+1], matrix_2D[row-1, col], matrix_2D[row-1, col-1], matrix_2D[row, col-1], matrix_2D[row+1, col-1], matrix_2D[row+1, col], matrix_2D[row+1, col+1]])
        temp_vals = temp_vals[temp_vals > 0]
        avg = np.mean(temp_vals)

    return avg
