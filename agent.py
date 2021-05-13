import random_number_generator
import environment
import numpy as np


# creates the parent class agent. This class contains the time_slot_preference (and maybe more later).
# From this class children classes can be made a use different strategies

class Agent:

    def __init__(self, environment, n_agents, ID, bonus_type):
        self.__utility = 0  # The utility that is gained by having the time slots chosen by the environment
        self.__total_utility = 0 # the total utility of an agent 
        self._time_slot_preference = [] # the time slot preferences of an agent
        self._time_slots_chosen = []  # The index's of the time slots chosen
        self.environment = environment  # assign the environment class
        self._n_time_slots = environment.get_n_time_slots()
        self.create_time_slot_preference()
        self.__ID = ID  # assign an ID
        self._willingness = 0
        self._strategy = ""
        self._bonus_type = bonus_type # 0 = no social bonus, 1 = social bonus
        self._social_utility = 0 # This is the total utility that has been earned from social bonus  
        if self._bonus_type == 1: # type 1 is social bonus agent 
            self._social_bonus = 0.05 # the social bonus an agent gets for each extra timeslot it picks
            self._social_bonus_cap = round(self._n_time_slots/3) # the number of slots an agent can pick in order to get social bonus. Could also be in environment
        
    def __str__(self):
        return f"Basic agent {self.__ID}"

    def get_willingness(self):
        return self._willingness
    
    def set_willingness(self, mean, sd):
        self._willingness = random_number_generator.generate_random_number_normal_distribution(mean, sd, 0, 1)

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

        #TODO: find a better way to fix that the social bonus can make the utility go above 1
        if self.__utility > 1: 
            self.__utility = 1

        self.__total_utility += self.__utility

    def reset_total_utility(self):
        self.__total_utility = 0

    def increase_utility(self):
        self.__utility += self._social_bonus
        self._social_utility += self._social_bonus

        #TODO: find a better way to fix that the social bonus can make the utility go above 1
        if self.__utility > 1: 
            self.__utility = 1

    def get_utility(self):
        return self.__utility

    def get_total_utility(self):
        return self.__total_utility

    # Returns the preference for a specific slot
    def get_time_slot_preference(self, idx_slot):
        return self._time_slot_preference[idx_slot]

    def get_social_utility(self):
        return self._social_utility

    def reset_utility(self):
        self.__utility = 0
        self._social_utility = 0

    def reset_timeslots_chosen(self):
        self._time_slots_chosen.clear()

    def change_time_slot_preference(self):
        for i in range(self._n_time_slots):
            # creates random value between 0 and 1 and stores this in time_slot_preference
            self._time_slot_preference[i] = random_number_generator.generate_random_number_normal_distribution()

    def set_n_time_slots(self, n_time_slots):
        self._n_time_slots = n_time_slots

    def create_time_slot_preference(self):
        self._time_slot_preference.clear()
        for _ in range(self._n_time_slots):
            # creates normally distributed random value with mean 0 and sd 1 and stores this in time_slot_preference
            self._time_slot_preference.append(random_number_generator.generate_random_number_normal_distribution())

    def __debug(self):
        print(f"agent {self.__ID}: {self._time_slot_preference}")






