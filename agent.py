import random
import enviroment
# creates the parent class agent. This class contains the time_slot_preference (and maybe more later).
# From this class children classes can be made a use different strategies
class Agent:
    __time_slot_preference = []
    __environment = enviroment.Environment()
    __n_time_slots = 0

    def __init__(self, environment):
        self.__environment = environment #assign the enviroment class
        self.__n_time_slots = environment.get_n_time_slots()
        self.__create_time_slot_preference()

    def __create_time_slot_preference(self):
        for i in range(self.__n_time_slots):
            # creates random value between 0 and 1, a value of 1 can not be achieved.
            # if we would want this we would have to change it to random.randrange(0, 1.01, 0.01)
            random_value = random.randrange(0, 1, 0.01)
            self.__time_slot_preference.append(random_value)


class Standard(Agent):
    pass