import numpy as np
def remove_stuck_px(data_cube):
    temp_data_cube = np.copy(data_cube)
    min_img = np.min(data_cube, axis=2)
    zero_idx = np.where(min_img == 0)
    zero_std_idx = np.where(np.std(data_cube, axis = 2) == 0)
    for i in range(len(zero_idx[0])):
        if zero_idx[0][i] == 0 and zero_idx[1][i] == 0:  # upper left
            temp_data_cube[zero_idx[0][i], zero_idx[1][i], :] = (data_cube[zero_idx[0][i] + 1, zero_idx[1][i] + 1, :] + \
                                                                 data_cube[zero_idx[0][i] + 1, zero_idx[1][i], :] + \
                                                                 data_cube[zero_idx[0][i], zero_idx[1][i] + 1, :]) / 3
        elif zero_idx[0][i] == 0 and zero_idx[1][i] == data_cube.shape[1]-1:  # upper right
            temp_data_cube[zero_idx[0][i], zero_idx[1][i], :] = (data_cube[zero_idx[0][i] + 1, zero_idx[1][i] - 1, :] + \
                                                                 data_cube[zero_idx[0][i] + 1, zero_idx[1][i], :] + \
                                                                 data_cube[zero_idx[0][i], zero_idx[1][i] - 1, :]) / 3
        elif zero_idx[0][i] == data_cube.shape[0]-1 and zero_idx[1][i] == 0:  # lower left
            temp_data_cube[zero_idx[0][i], zero_idx[1][i], :] = (data_cube[zero_idx[0][i] - 1, zero_idx[1][i] + 1, :] + \
                                                                 data_cube[zero_idx[0][i] - 1, zero_idx[1][i], :] + \
                                                                 data_cube[zero_idx[0][i], zero_idx[1][i] + 1, :]) / 3
        elif zero_idx[0][i] == data_cube.shape[0]-1 and zero_idx[1][i] == data_cube.shape[1]-1:  # lower right
            temp_data_cube[zero_idx[0][i], zero_idx[1][i], :] = (data_cube[zero_idx[0][i] - 1, zero_idx[1][i] - 1, :] + \
                                                                 data_cube[zero_idx[0][i] - 1, zero_idx[1][i], :] + \
                                                                 data_cube[zero_idx[0][i], zero_idx[1][i] - 1, :]) / 3
        elif zero_idx[0][i] == 0:  # upper row
            temp_data_cube[zero_idx[0][i], zero_idx[1][i], :] = (data_cube[zero_idx[0][i] + 1, zero_idx[1][i] + 1, :] + \
                                                                 data_cube[zero_idx[0][i] + 1, zero_idx[1][i] - 1, :] + \
                                                                 data_cube[zero_idx[0][i] + 1, zero_idx[1][i], :] + \
                                                                 data_cube[zero_idx[0][i], zero_idx[1][i] + 1, :] + \
                                                                 data_cube[zero_idx[0][i], zero_idx[1][i] - 1, :]) / 5
        elif zero_idx[0][i] == data_cube.shape[0]-1:  # lower row
            temp_data_cube[zero_idx[0][i], zero_idx[1][i], :] = (data_cube[zero_idx[0][i] - 1, zero_idx[1][i] - 1, :] + \
                                                                 data_cube[zero_idx[0][i] - 1, zero_idx[1][i] + 1, :] + \
                                                                 data_cube[zero_idx[0][i] - 1, zero_idx[1][i], :] + \
                                                                 data_cube[zero_idx[0][i], zero_idx[1][i] + 1, :] + \
                                                                 data_cube[zero_idx[0][i], zero_idx[1][i] - 1, :]) / 5
        elif zero_idx[1][i] == 0:  # leftmost column
            temp_data_cube[zero_idx[0][i], zero_idx[1][i], :] = (data_cube[zero_idx[0][i] + 1, zero_idx[1][i] + 1, :] + \
                                                                 data_cube[zero_idx[0][i] - 1, zero_idx[1][i] + 1, :] + \
                                                                 data_cube[zero_idx[0][i] + 1, zero_idx[1][i], :] + \
                                                                 data_cube[zero_idx[0][i] - 1, zero_idx[1][i], :] + \
                                                                 data_cube[zero_idx[0][i], zero_idx[1][i] + 1, :]) / 5
        elif zero_idx[1][i] == data_cube.shape[1]-1:  # rightmost column
            temp_data_cube[zero_idx[0][i], zero_idx[1][i], :] = (data_cube[zero_idx[0][i] - 1, zero_idx[1][i] - 1, :] + \
                                                                 data_cube[zero_idx[0][i] + 1, zero_idx[1][i] - 1, :] + \
                                                                 data_cube[zero_idx[0][i] + 1, zero_idx[1][i], :] + \
                                                                 data_cube[zero_idx[0][i] - 1, zero_idx[1][i], :] + \
                                                                 data_cube[zero_idx[0][i], zero_idx[1][i] - 1, :]) / 5
        else:
            temp_data_cube[zero_idx[0][i], zero_idx[1][i], :] = (data_cube[zero_idx[0][i] + 1, zero_idx[1][i] + 1, :] + \
                                                                 data_cube[zero_idx[0][i] - 1, zero_idx[1][i] - 1, :] + \
                                                                 data_cube[zero_idx[0][i] + 1, zero_idx[1][i] - 1, :] + \
                                                                 data_cube[zero_idx[0][i] - 1, zero_idx[1][i] + 1, :] + \
                                                                 data_cube[zero_idx[0][i] + 1, zero_idx[1][i], :] + \
                                                                 data_cube[zero_idx[0][i] - 1, zero_idx[1][i], :] + \
                                                                 data_cube[zero_idx[0][i], zero_idx[1][i] + 1, :] + \
                                                                 data_cube[zero_idx[0][i], zero_idx[1][i] - 1, :]) / 8

    for i in range(len(zero_std_idx[0])):
        if zero_std_idx[0][i] == 0 and zero_std_idx[1][i] == 0:  # upper left
            temp_data_cube[zero_std_idx[0][i], zero_std_idx[1][i], :] = (data_cube[zero_std_idx[0][i] + 1, zero_std_idx[1][i] + 1, :] + \
                                                                 data_cube[zero_std_idx[0][i] + 1, zero_std_idx[1][i], :] + \
                                                                 data_cube[zero_std_idx[0][i], zero_std_idx[1][i] + 1, :]) / 3
        elif zero_std_idx[0][i] == 0 and zero_std_idx[1][i] == data_cube.shape[1]-1:  # upper right
            temp_data_cube[zero_std_idx[0][i], zero_std_idx[1][i], :] = (data_cube[zero_std_idx[0][i] + 1, zero_std_idx[1][i] - 1, :] + \
                                                                 data_cube[zero_std_idx[0][i] + 1, zero_std_idx[1][i], :] + \
                                                                 data_cube[zero_std_idx[0][i], zero_std_idx[1][i] - 1, :]) / 3
        elif zero_std_idx[0][i] == data_cube.shape[0]-1 and zero_std_idx[1][i] == 0:  # lower left
            temp_data_cube[zero_std_idx[0][i], zero_std_idx[1][i], :] = (data_cube[zero_std_idx[0][i] - 1, zero_std_idx[1][i] + 1, :] + \
                                                                 data_cube[zero_std_idx[0][i] - 1, zero_std_idx[1][i], :] + \
                                                                 data_cube[zero_std_idx[0][i], zero_std_idx[1][i] + 1, :]) / 3
        elif zero_std_idx[0][i] == data_cube.shape[0]-1 and zero_std_idx[1][i] == data_cube.shape[1]-1:  # lower right
            temp_data_cube[zero_std_idx[0][i], zero_std_idx[1][i], :] = (data_cube[zero_std_idx[0][i] - 1, zero_std_idx[1][i] - 1, :] + \
                                                                 data_cube[zero_std_idx[0][i] - 1, zero_std_idx[1][i], :] + \
                                                                 data_cube[zero_std_idx[0][i], zero_std_idx[1][i] - 1, :]) / 3
        elif zero_std_idx[0][i] == 0:  # upper row
            temp_data_cube[zero_std_idx[0][i], zero_std_idx[1][i], :] = (data_cube[zero_std_idx[0][i] + 1, zero_std_idx[1][i] + 1, :] + \
                                                                 data_cube[zero_std_idx[0][i] + 1, zero_std_idx[1][i] - 1, :] + \
                                                                 data_cube[zero_std_idx[0][i] + 1, zero_std_idx[1][i], :] + \
                                                                 data_cube[zero_std_idx[0][i], zero_std_idx[1][i] + 1, :] + \
                                                                 data_cube[zero_std_idx[0][i], zero_std_idx[1][i] - 1, :]) / 5
        elif zero_std_idx[0][i] == data_cube.shape[0]-1:  # lower row
            temp_data_cube[zero_std_idx[0][i], zero_std_idx[1][i], :] = (data_cube[zero_std_idx[0][i] - 1, zero_std_idx[1][i] - 1, :] + \
                                                                 data_cube[zero_std_idx[0][i] - 1, zero_std_idx[1][i] + 1, :] + \
                                                                 data_cube[zero_std_idx[0][i] - 1, zero_std_idx[1][i], :] + \
                                                                 data_cube[zero_std_idx[0][i], zero_std_idx[1][i] + 1, :] + \
                                                                 data_cube[zero_std_idx[0][i], zero_std_idx[1][i] - 1, :]) / 5
        elif zero_std_idx[1][i] == 0:  # leftmost column
            temp_data_cube[zero_std_idx[0][i], zero_std_idx[1][i], :] = (data_cube[zero_std_idx[0][i] + 1, zero_std_idx[1][i] + 1, :] + \
                                                                 data_cube[zero_std_idx[0][i] - 1, zero_std_idx[1][i] + 1, :] + \
                                                                 data_cube[zero_std_idx[0][i] + 1, zero_std_idx[1][i], :] + \
                                                                 data_cube[zero_std_idx[0][i] - 1, zero_std_idx[1][i], :] + \
                                                                 data_cube[zero_std_idx[0][i], zero_std_idx[1][i] + 1, :]) / 5
        elif zero_std_idx[1][i] == data_cube.shape[1]-1:  # rightmost column
            temp_data_cube[zero_std_idx[0][i], zero_std_idx[1][i], :] = (data_cube[zero_std_idx[0][i] - 1, zero_std_idx[1][i] - 1, :] + \
                                                                 data_cube[zero_std_idx[0][i] + 1, zero_std_idx[1][i] - 1, :] + \
                                                                 data_cube[zero_std_idx[0][i] + 1, zero_std_idx[1][i], :] + \
                                                                 data_cube[zero_std_idx[0][i] - 1, zero_std_idx[1][i], :] + \
                                                                 data_cube[zero_std_idx[0][i], zero_std_idx[1][i] - 1, :]) / 5
        else:
            temp_data_cube[zero_std_idx[0][i], zero_std_idx[1][i], :] = (data_cube[zero_std_idx[0][i] + 1, zero_std_idx[1][i] + 1, :] + \
                                                                 data_cube[zero_std_idx[0][i] - 1, zero_std_idx[1][i] - 1, :] + \
                                                                 data_cube[zero_std_idx[0][i] + 1, zero_std_idx[1][i] - 1, :] + \
                                                                 data_cube[zero_std_idx[0][i] - 1, zero_std_idx[1][i] + 1, :] + \
                                                                 data_cube[zero_std_idx[0][i] + 1, zero_std_idx[1][i], :] + \
                                                                 data_cube[zero_std_idx[0][i] - 1, zero_std_idx[1][i], :] + \
                                                                 data_cube[zero_std_idx[0][i], zero_std_idx[1][i] + 1, :] + \
                                                                 data_cube[zero_std_idx[0][i], zero_std_idx[1][i] - 1, :]) / 8

    return temp_data_cube


def remove_outlying_px(data_cube, cut_off):
    temp_data_cube = np.copy(data_cube)
    gray_img = np.mean(temp_data_cube, axis=2)
    gray_img += abs(np.min(gray_img))
    gray_img = gray_img / np.max(gray_img)

    neighbour_img = np.zeros([gray_img.shape[0], gray_img.shape[1]])
    for i in range(gray_img.shape[0]):
        for j in range(gray_img.shape[1]):
            if i == 0 and j == 0:  # upper left
                neighbour_img[i, j] = gray_img[i, j] - (gray_img[i, j + 1] + gray_img[i + 1, j] + gray_img[i + 1, j + 1]) / 3
            elif i == 0 and j == gray_img.shape[1] - 1:  # upper right
                neighbour_img[i, j] = gray_img[i, j] - (gray_img[i, j - 1] + gray_img[i + 1, j] + gray_img[i + 1, j - 1]) / 3
            elif i == gray_img.shape[0] - 1 and j == 0:  # bottom left
                neighbour_img[i, j] = gray_img[i, j] - (gray_img[i - 1, j] + gray_img[i, j + 1] + gray_img[i - 1, j + 1]) / 3
            elif i == gray_img.shape[0] - 1 and j == gray_img.shape[1] - 1:  # bottom right
                neighbour_img[i, j] = gray_img[i, j] - (gray_img[i, j - 1] + gray_img[i - 1, j] + gray_img[i - 1, j - 1]) / 3
            elif i == 0:  # top row
                neighbour_img[i, j] = gray_img[i, j] - (gray_img[i, j - 1] + gray_img[i, j + 1] + gray_img[i + 1, j] + gray_img[i + 1, j - 1] + gray_img[i + 1, j + 1]) / 5
            elif i == gray_img.shape[0] - 1:  # bottom row
                neighbour_img[i, j] = gray_img[i, j] - (gray_img[i, j - 1] + gray_img[i, j + 1] + gray_img[i - 1, j] + gray_img[i - 1, j - 1] + gray_img[i - 1, j + 1]) / 5
            elif j == 0:  # leftmost column
                neighbour_img[i, j] = gray_img[i, j] - (gray_img[i + 1, j] + gray_img[i - 1, j] + gray_img[i, j + 1] + gray_img[i + 1, j + 1] + gray_img[i - 1, j + 1]) / 5
            elif j == gray_img.shape[1] - 1:  # rightmost column
                neighbour_img[i, j] = gray_img[i, j] - (gray_img[i + 1, j] + gray_img[i - 1, j] + gray_img[i, j - 1] + gray_img[i + 1, j - 1] + gray_img[i - 1, j - 1]) / 5
            else:
                neighbour_img[i, j] = gray_img[i, j] - (gray_img[i - 1, j - 1] + gray_img[i - 1, j] + gray_img[i - 1, j + 1] + gray_img[i, j + 1] + gray_img[i + 1, j + 1] + gray_img[i + 1, j] + gray_img[i + 1, j - 1] + gray_img[i, j - 1]) / 8

    outlier_idx = np.where(abs(neighbour_img) > cut_off)

    for i in range(len(outlier_idx[0])):
        if outlier_idx[0][i] == 0 and outlier_idx[1][i] == 0:  # upper left
            temp_data_cube[outlier_idx[0][i], outlier_idx[1][i], :] = (data_cube[outlier_idx[0][i] + 1, outlier_idx[1][i] + 1, :] + \
                                                                 data_cube[outlier_idx[0][i] + 1, outlier_idx[1][i], :] + \
                                                                 data_cube[outlier_idx[0][i], outlier_idx[1][i] + 1, :]) / 3
        elif outlier_idx[0][i] == 0 and outlier_idx[1][i] == data_cube.shape[1]-1:  # upper right
            temp_data_cube[outlier_idx[0][i], outlier_idx[1][i], :] = (data_cube[outlier_idx[0][i] + 1, outlier_idx[1][i] - 1, :] + \
                                                                 data_cube[outlier_idx[0][i] + 1, outlier_idx[1][i], :] + \
                                                                 data_cube[outlier_idx[0][i], outlier_idx[1][i] - 1, :]) / 3
        elif outlier_idx[0][i] == data_cube.shape[0]-1 and outlier_idx[1][i] == 0:  # lower left
            temp_data_cube[outlier_idx[0][i], outlier_idx[1][i], :] = (data_cube[outlier_idx[0][i] - 1, outlier_idx[1][i] + 1, :] + \
                                                                 data_cube[outlier_idx[0][i] - 1, outlier_idx[1][i], :] + \
                                                                 data_cube[outlier_idx[0][i], outlier_idx[1][i] + 1, :]) / 3
        elif outlier_idx[0][i] == data_cube.shape[0]-1 and outlier_idx[1][i] == data_cube.shape[1]-1:  # lower right
            temp_data_cube[outlier_idx[0][i], outlier_idx[1][i], :] = (data_cube[outlier_idx[0][i] - 1, outlier_idx[1][i] - 1, :] + \
                                                                 data_cube[outlier_idx[0][i] - 1, outlier_idx[1][i], :] + \
                                                                 data_cube[outlier_idx[0][i], outlier_idx[1][i] - 1, :]) / 3
        elif outlier_idx[0][i] == 0:  # upper row
            temp_data_cube[outlier_idx[0][i], outlier_idx[1][i], :] = (data_cube[outlier_idx[0][i] + 1, outlier_idx[1][i] + 1, :] + \
                                                                 data_cube[outlier_idx[0][i] + 1, outlier_idx[1][i] - 1, :] + \
                                                                 data_cube[outlier_idx[0][i] + 1, outlier_idx[1][i], :] + \
                                                                 data_cube[outlier_idx[0][i], outlier_idx[1][i] + 1, :] + \
                                                                 data_cube[outlier_idx[0][i], outlier_idx[1][i] - 1, :]) / 5
        elif outlier_idx[0][i] == data_cube.shape[0]-1:  # lower row
            temp_data_cube[outlier_idx[0][i], outlier_idx[1][i], :] = (data_cube[outlier_idx[0][i] - 1, outlier_idx[1][i] - 1, :] + \
                                                                 data_cube[outlier_idx[0][i] - 1, outlier_idx[1][i] + 1, :] + \
                                                                 data_cube[outlier_idx[0][i] - 1, outlier_idx[1][i], :] + \
                                                                 data_cube[outlier_idx[0][i], outlier_idx[1][i] + 1, :] + \
                                                                 data_cube[outlier_idx[0][i], outlier_idx[1][i] - 1, :]) / 5
        elif outlier_idx[1][i] == 0:  # leftmost column
            temp_data_cube[outlier_idx[0][i], outlier_idx[1][i], :] = (data_cube[outlier_idx[0][i] + 1, outlier_idx[1][i] + 1, :] + \
                                                                 data_cube[outlier_idx[0][i] - 1, outlier_idx[1][i] + 1, :] + \
                                                                 data_cube[outlier_idx[0][i] + 1, outlier_idx[1][i], :] + \
                                                                 data_cube[outlier_idx[0][i] - 1, outlier_idx[1][i], :] + \
                                                                 data_cube[outlier_idx[0][i], outlier_idx[1][i] + 1, :]) / 5
        elif outlier_idx[1][i] == data_cube.shape[1]-1:  # rightmost column
            temp_data_cube[outlier_idx[0][i], outlier_idx[1][i], :] = (data_cube[outlier_idx[0][i] - 1, outlier_idx[1][i] - 1, :] + \
                                                                 data_cube[outlier_idx[0][i] + 1, outlier_idx[1][i] - 1, :] + \
                                                                 data_cube[outlier_idx[0][i] + 1, outlier_idx[1][i], :] + \
                                                                 data_cube[outlier_idx[0][i] - 1, outlier_idx[1][i], :] + \
                                                                 data_cube[outlier_idx[0][i], outlier_idx[1][i] - 1, :]) / 5
        else:
            temp_data_cube[outlier_idx[0][i], outlier_idx[1][i], :] = (data_cube[outlier_idx[0][i] + 1, outlier_idx[1][i] + 1, :] + \
                                                                 data_cube[outlier_idx[0][i] - 1, outlier_idx[1][i] - 1, :] + \
                                                                 data_cube[outlier_idx[0][i] + 1, outlier_idx[1][i] - 1, :] + \
                                                                 data_cube[outlier_idx[0][i] - 1, outlier_idx[1][i] + 1, :] + \
                                                                 data_cube[outlier_idx[0][i] + 1, outlier_idx[1][i], :] + \
                                                                 data_cube[outlier_idx[0][i] - 1, outlier_idx[1][i], :] + \
                                                                 data_cube[outlier_idx[0][i], outlier_idx[1][i] + 1, :] + \
                                                                 data_cube[outlier_idx[0][i], outlier_idx[1][i] - 1, :]) / 8

    return temp_data_cube, outlier_idx
