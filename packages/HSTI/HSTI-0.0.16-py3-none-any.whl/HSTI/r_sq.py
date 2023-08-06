# Function returns coefficient of determination between values based on model
#(y_fit) and corresponding measured values (y_meas)

def r_sq(y_fit, y_meas):
    mean = sum(y_meas)/len(y_meas)
    #Sum of squared residuals
    SS_res = sum([(m - f)**2 for m, f in zip(y_meas, y_fit)])
    #Total sum of squares
    SS_tot = sum([(m - mean)**2 for m in y_meas])

    R_sq = 1 - SS_res/SS_tot

    return R_sq
