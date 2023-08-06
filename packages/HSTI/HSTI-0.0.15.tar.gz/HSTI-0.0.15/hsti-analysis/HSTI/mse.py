# Function returns MSE between two lists of same length
def lst_mse(lst1, lst2):
    MSE = 0
    for i in range(len(lst1)):
        MSE += (lst1[i]-lst2[i])**2
    MSE = MSE/len(lst1)
    return MSE
