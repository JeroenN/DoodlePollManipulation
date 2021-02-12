# The class creates the time-slots and counts how often
# a certain time slot is chosen
class Environment:
    __time_slots = []
    __n_time_slots = 0  # number of time-slots
    __time_slots_chosen = []

    def __init__(self, number_of_slots=0):
        self.__n_time_slots = number_of_slots
        self.__create_time_slots()

    # Set how
    def __create_time_slots(self):
        for i in range(self.__n_time_slots):
            self.__time_slots_chosen.append(0)

    # This function can be called by an agent to vote for that particular time slot
    def vote_time_slot(self, index_time_slot):
        self.__time_slots_chosen[index_time_slot] += 1

    # This function can be called by an agent to see how often a time slot is voted for
    def get_time_slots(self):
        return self.__time_slots_chosen

    # Get the number of time slots
    def get_n_time_slots(self):
        return self.__n_time_slots
