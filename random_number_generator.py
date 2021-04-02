import numpy as np

# Generates a random number from a normal distribution with a certain mean and standard deviation. The number
# has to be between a certain range
def generate_random_number_normal_distribution(mean=0.5, standard_deviation=0.35, start_range=0, end_range=1):
    random_number = np.random.normal(mean, standard_deviation, 1)
    while random_number < start_range or random_number > end_range:
        random_number = np.random.normal(mean, standard_deviation, 1)
    return random_number[0]
