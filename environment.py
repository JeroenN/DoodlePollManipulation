def partition(arr, low, high):
    pass

def quick_sort(arr, low, high):
    if low < high:
        pi = partition()

# The class creates the time-slots and counts how often
# a certain time slot is chosen
class Environment:
    __n_time_slots = 0  # number of time-slots
    __time_slots_chosen = [] # How often each time slot is chosen
    __idx_most_popular_time_slot = 0 # The idx of the most poular time slot
    __rank_popularity_time_slots = []

    def __init__(self, number_of_slots=0):
        self.__n_time_slots = number_of_slots
        self.__create_time_slots()

    def __str__(self):
        return f"Environment with {self.__n_time_slots} time slots"

    # This function can be called by an agent to vote for that particular time slot
    def vote_time_slot(self, index_time_slot):
        self.__time_slots_chosen[index_time_slot] += 1

    # This function can be called by an agent to see how often a time slot is voted for
    def get_time_slots(self):
        return self.__time_slots_chosen

    # Get the number of time slots
    def get_n_time_slots(self):
        return self.__n_time_slots

    # Determines the most popular time slot based on which time slots is most often chosen
    def determine_most_popular_time_slot(self):
        max = 0
        idx = 0
        for i in range(len(self.__time_slots_chosen)):
            if self.__time_slots_chosen[i] > max:
                max = self.__time_slots_chosen[i]
                idx = i
        self.__idx_most_popular_time_slot = idx

    # Using quicksort to sort the time-slots based on popularity
    def rank_popularity_time_slots(self):
        quick_sort()

    def get_most_popular_time_slot(self):
        return self.__idx_most_popular_time_slot

    # For each time slot the amount of times it is chosen is set to 0
    def __create_time_slots(self):
        for _ in range(self.__n_time_slots):
            self.__time_slots_chosen.append(0)
