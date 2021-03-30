from agent import Agent
import quick_sort
import random_number_generator
import normal_distribution

# This is the standard strategy, agents with this strategy vote for all the time-slots for which the
# agent has a preference above or equal to the specified threshold
class Standard(Agent):

    def __init__(self, environment, ID):
        Agent.__init__(self, environment, ID)
        self.__threshold = 0.55  # TODO: change to normal distribution
        self.__ID = ID
        self._willingness = random_number_generator.generate_random_number_normal_distribution(0.4, 0.2, 0, 1)
        self._strategy = "standard"

    # vote for a time slot if the time slot preference for that time slot is above the threshold
    # Update also for the particular object that it voted on that specific time slot
    def vote(self):
        for i in range(self._n_time_slots):
            if self._time_slot_preference[i] >= self.__threshold:
                self.environment.vote_time_slot(i)
                self._time_slots_chosen.append(i)
        self.environment.remove_agent_from_voting_list()

    def set_threshold(self, threshold):
        self.__threshold = threshold

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
    def __init__(self, environment, ID):
        Agent.__init__(self, environment, ID)
        self.__popular_time_slots_idx = []
        self.__popular_time_slots_preference = []
        self.__n_slots_consideration = 3  # The number of time slots that will be taken in consideration\
        self.__n_votes = 1  # How many votes the agent should cast, this has to be always equal or greater than n_slots_consideration
        environment.rank_popularity_time_slots()
        self._willingness = random_number_generator.generate_random_number_normal_distribution(0.8, 0.1, 0, 1)
        self._strategy = "popular"
        self.__ID = ID

    def __create_list_popular_slots(self):
        self.environment.rank_popularity_time_slots()  # Ranks the time slots from least popular to most popular

        # Goes over the last n_slots_consideration and adds the index of those to the array idx_popular_time_slots
        for idx in range(self._n_time_slots - self.__n_slots_consideration, self._n_time_slots):
            idx_time_slots = self.environment.get_initial_idx_time_slots()
            self.__popular_time_slots_idx.append(idx_time_slots[idx])
            #self.__popular_time_slots_idx.append(idx)

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

    def __debug(self):
        print(f"popular time slots preference: {self.__popular_time_slots_preference} \n")

    def set_k(self, k):
        self.__n_votes = k

    def set_m(self, m):
        self.__n_slots_consideration = m

    def vote(self):
        self.__create_list_popular_slots()
        self.__create_list_preference_popular_slots()
        self.__vote_for_slots_highest_preference()
        self.__popular_time_slots_preference.clear()
        self.__popular_time_slots_idx.clear()
        self.environment.remove_agent_from_voting_list()

class Popular_prediction(Agent):

    def __init__(self, environment, ID):
        Agent.__init__(self, environment, ID)
        self.__preference_per_slot = []
        self.__means_per_slot = []
        self.__standard_deviation_per_slot = []
        self._strategy = 'popular_prediction'
        self.__print_debug()


    def set_normal_distribution(self, means_per_slot, standard_deviation_per_slot):
        self.__means_per_slot = means_per_slot
        self.__standard_deviation_per_slot = standard_deviation_per_slot

    def __print_debug(self):
        print(f"means_per_slot: ", self.__means_per_slot)
        print(f"standard deviation per slot: ", self.__standard_deviation_per_slot)

    def vote(self):
        for i in range(self._n_time_slots):
            if self._time_slot_preference[i] >= 0.55:
                self.environment.vote_time_slot(i)
                self._time_slots_chosen.append(i)
        self.environment.remove_agent_from_voting_list()