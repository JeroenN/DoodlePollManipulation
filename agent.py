import random
import environment


# creates the parent class agent. This class contains the time_slot_preference (and maybe more later).
# From this class children classes can be made a use different strategies

class Agent:
    _time_slot_preference = []  # the time slot preferences of an agent
    environment = environment.Environment()  # the environment that the agent is in
    _n_time_slots = 0  # number of time slots
    _time_slots_chosen = [] # The index's of the time slots chosen
    __utility = 0 # The utility that is gained by having the time slots chosen by the environment

    __ID = None  # unique identification


    def __init__(self, environment, ID):
        self.environment = environment  # assign the environment class
        self._n_time_slots = environment.get_n_time_slots()
        self.__create_time_slot_preference()
        self.__ID = ID  # assign an ID

    def __str__(self):
        return f"Basic agent {self.__ID}"

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

    def change_time_slot_preference(self):
        for i in range(self._n_time_slots):
            # creates random value between 0 and 1 and stores this in time_slot_preference
            self._time_slot_preference[i] = random.uniform(0, 1)

    # FIXME: right know for some reason the time slot preference for each agent is the same for the first round
    def __create_time_slot_preference(self):
        for i in range(self._n_time_slots):
            # creates random value between 0 and 1 and stores this in time_slot_preference
            self._time_slot_preference.append(random.uniform(0, 1))








