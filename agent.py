import random
import environment
import numpy as np


# creates the parent class agent. This class contains the time_slot_preference (and maybe more later).
# From this class children classes can be made a use different strategies

class Agent:
    environment = environment.Environment()  # the environment that the agent is in
    def __init__(self, environment, ID):
        self.__utility = 0  # The utility that is gained by having the time slots chosen by the environment
        self._time_slot_preference = [] # the time slot preferences of an agent
        self._time_slots_chosen = []  # The index's of the time slots chosen
        self.environment = environment  # assign the environment class
        self._n_time_slots = environment.get_n_time_slots()
        self.__create_time_slot_preference()
        self.__ID = ID  # assign an ID
        self._willingness = 0
        self._strategy = ""
        #self.__debug()
        
    def __str__(self):
        return f"Basic agent {self.__ID}"

    def get_willingness(self):
        return self._willingness

    def get_strategy(self):
        return self._strategy

    def print_voted_time_slots(self):
        for time_slot_chosen in self._time_slots_chosen:
            print(f"voted for time slot: {time_slot_chosen} ")

    def print_time_slot_preference(self):
        for i in range(len(self._time_slot_preference)):
            print(f"time slot {i} has a preference of {self._time_slot_preference[i]}")

    # Calculate and return the total utility
    def calculate_utility(self):
        self.__utility += self._time_slot_preference[self.environment.get_most_popular_time_slot()]

    def get_utility(self):
        return self.__utility

    def reset_utility(self):
        self.__utility = 0

    def change_time_slot_preference(self):
        for i in range(self._n_time_slots):
            # creates random value between 0 and 1 and stores this in time_slot_preference
            self._time_slot_preference[i] = random.uniform(0, 1)

    def __create_time_slot_preference(self):
        for _ in range(self._n_time_slots):
            # creates normally distributed random value with mean 0 and sd 1 and stores this in time_slot_preference
            self._time_slot_preference.append(random.uniform(0, 1))

    def __debug(self):
        print(f"agent {self.__ID}: {self._time_slot_preference}")






