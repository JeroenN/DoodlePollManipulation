import random
import environment


# creates the parent class agent. This class contains the time_slot_preference (and maybe more later).
# From this class children classes can be made a use different strategies

class Agent:
    time_slot_preference = []  # the time slot preferences of an agent
    environment = environment.Environment()  # the environment that the agent is in
    n_time_slots = 0  # number of time slots
    time_slots_chosen = []
    __ID = None  # unique identification


    def __init__(self, environment, ID):
        self.environment = environment  # assign the environment class
        self.n_time_slots = environment.get_n_time_slots()
        self.__create_time_slot_preference()
        self.__ID = ID  # assign an ID


    def __str__(self):
        return f"Basic agent {self.__ID}"

    def print_voted_time_slots(self):
        for time_slot_chosen in self.time_slots_chosen:
            print(f"voted for time slot: {time_slot_chosen} ")

    def print_time_slot_preference(self):
        for i in range(len(self.time_slot_preference)):
            print(f"time slot {i} has a preference of {self.time_slot_preference[i]}")

    def __create_time_slot_preference(self):
        for i in range(self.n_time_slots):
            # creates random value between 0 and 1 and stores this in time_slot_preference
            self.time_slot_preference.append(random.uniform(0, 1))


class Standard(Agent):
    __threshold = 0.7

    def __init__(self, environment, ID):
        Agent.__init__(self, environment, ID)
        self.vote()

    # vote for a time slot if the time slot preference for that time slot is above the threshold
    # Update also for the particular object that it voted on that specific time slot
    def vote(self):
        for i in range(self.n_time_slots):
            if self.time_slot_preference[i] >= self.__threshold:
                self.environment.vote_time_slot(i)
                self.time_slots_chosen.append(i)




