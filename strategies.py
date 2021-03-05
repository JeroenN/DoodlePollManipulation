from agent import Agent
import quick_sort
import random
from datetime import datetime

# This is the standard strategy, agents with this strategy vote for all the time-slots for which the
# agent has a preference above or equal to the specified threshold
class Standard(Agent):
    __threshold = random.random() #TODO: change to normal distribution


    def __init__(self, environment, ID):
        Agent.__init__(self, environment, ID)
        self._willingness = random.randint(0,100) #TODO: change to normal distribution
        self._strategy = "standard"

    # vote for a time slot if the time slot preference for that time slot is above the threshold
    # Update also for the particular object that it voted on that specific time slot
    def vote(self):
        for i in range(self._n_time_slots):
            if self._time_slot_preference[i] >= self.__threshold:
                self.environment.vote_time_slot(i)
                self._time_slots_chosen.append(i)
                self._voted = True
        self.environment.remove_agent_from_voting_list()

# This is the popular strategy, agents with this strategy look at the most popular time slots and vote for
# the popular time slots that have the highest preference. For this strategy to work the agent has to wait
# for other agents to vote.
# This strategy could be expanded by looking at how many agents already voted and how many agents have yet to vote
# And based on this determine the number of slots that should be taken in to consideration. E.g. when not a lot of
# agents have voted it can be beneficial to take more slots into consideration since it is hard to determine
# right now what time slot will most likely win.
# To make it even more complex you could also take a look at the most popular time slot and then compare that
# to the second, third ect. popular time slot on how much they differ. Then the agent could determine itself
# which time slots it should take into consideration.
class Popular(Agent):
    __popular_time_slots_idx = []
    __popular_time_slots_preference = []
    __n_slots_consideration = 5 # The number of time slots that will be taken in consideration\
    __n_votes = 3  # How many votes the agent should cast, this has to be always equal or greater than n_slots_consideration

    def __init__(self, environment, ID):
        Agent.__init__(self, environment, ID)
        environment.rank_popularity_time_slots()
        self._willingness = 99
        self._strategy = "popular"

    def __create_list_popular_slots(self):
        self.environment.rank_popularity_time_slots()  # Ranks the time slots from least popular to most popular

        # Goes over the last n_slots_consideration and adds the index of those to the array idx_popular_time_slots
        for idx in range(self._n_time_slots - self.__n_slots_consideration, self._n_time_slots):
            self.__popular_time_slots_idx.append(idx)

    def __create_list_preference_popular_slots(self):
        # Makes a new list with the most popular time-slots
        for idx in self.__popular_time_slots_idx:
            preference = self._time_slot_preference[idx]
            self.__popular_time_slots_preference.append(preference)

    def __vote_for_slots_highest_preference(self):
        # Rank in terms of highest preference
        quick_sort.quick_sort(self.__popular_time_slots_preference, self.__popular_time_slots_idx, 0, self.__n_slots_consideration - 1)

        # Vote for n_votes time-slots with the highest preference from the n_slots_consideration most popular time slots
        for idx in range(self.__n_slots_consideration - self.__n_votes, self.__n_slots_consideration):
            self.environment.vote_time_slot(self.__popular_time_slots_idx[idx])
            self._time_slots_chosen.append(self.__popular_time_slots_idx[idx])

    def vote(self):
        self.__create_list_popular_slots()
        self.__create_list_preference_popular_slots()
        self.__vote_for_slots_highest_preference()
        self.environment.remove_agent_from_voting_list()





