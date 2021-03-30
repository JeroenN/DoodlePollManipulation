import math
# Calculates the mean of the elements in a list
def calculate_mean(arr):
    mean = 0
    print(f"length: ", len(arr))
    for element in arr:
        mean += element

    return mean / len(arr)

# Calculates the standard deviation in a list by first calculating the variance and then taking
# the square root of the variance
def calculate_standard_deviation(arr, mean):
    variance = 0
    for element in arr:
        variance += pow(element - mean, 2)

    variance /= len(arr)
    return math.sqrt(variance)
