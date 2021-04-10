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
        self._willingness = random_number_generator.generate_random_number_normal_distribution(0.8, 0.1, 0, 1)
        self._strategy = "popular"
        self.__ID = ID


    # Goes over the last n_slots_consideration and adds the index of those to the array idx_popular_time_slots
    def __create_list_popular_slots(self):
        self.environment.rank_popularity_time_slots()  # Ranks the time slots from least popular to most popular

        # Takes the indexes from the last n_slots_consideration time slots (they are ranked from least to most popular,
        # thus the n_slots_consideration most popular time slots) and puts to indexes in the list popular_time_slots_idx
        for idx in range(self._n_time_slots - self.__n_slots_consideration, self._n_time_slots):
            idx_time_slots = self.environment.get_initial_idx_time_slots()
            self.__popular_time_slots_idx.append(idx_time_slots[idx])


    # Makes a new list with the preference for each popular time slot, starting from the least popular to the most
    # popular. This is realized by taking the list __popular_time_slot_idx which contains the indexes of the slots
    # starting with the idx of the least popular and moving up idx of the time slot which is the most popular
    def __create_list_preference_popular_slots(self):
        for idx in self.__popular_time_slots_idx:
            preference = self._time_slot_preference[idx]
            self.__popular_time_slots_preference.append(preference)

    # Rank in terms of highest preference
    def __vote_for_slots_highest_preference(self):
        # Quick sorts the n_slots_consideration most popular time slots in terms of the agents their preference, then
        # the list popular_time_slots_idx can be used to vote for the right time slots.
        quick_sort.quick_sort(self.__popular_time_slots_preference, self.__popular_time_slots_idx, 0,
                              self.__n_slots_consideration - 1)

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
        self._willingness = random_number_generator.generate_random_number_normal_distribution(0.1, 0.2, 0, 1)
        self.__n_slots_consideration = 3  # The number of time slots that will be taken in consideration\
        self.__n_votes = 1  # How many votes the agent should cast, this has to be always equal or greater than n_slots_consideration
        self.__popular_time_slots_idx = []
        self.__popular_time_slots_preference = []
        self.__slots_preference_prediction = []
        self.__slots_preference_prediction_idx = []
        # A parameter between 0 and around 3 ish. The lower this number, the less important the standard deviation is when
        # computing how each slot should be ranked in terms of how likely agents are expected to vote for a
        # certain time slot. The higher this number, the more important the standard deviation gets in this calculation
        self.__importance_standard_deviation = 0.5


    def set_normal_distribution(self, means_per_slot, standard_deviation_per_slot):
        self.__means_per_slot = means_per_slot
        self.__standard_deviation_per_slot = standard_deviation_per_slot

    # Goes over the last n_slots_consideration and adds the index of those to the array idx_popular_time_slots
    def __create_list_popular_slots(self):
        self.environment.rank_popularity_time_slots()  # Ranks the time slots from least popular to most popular
        for idx in range(self._n_time_slots - self.__n_slots_consideration, self._n_time_slots):
            idx_time_slots = self.environment.get_initial_idx_time_slots()
            self.__popular_time_slots_idx.append(idx_time_slots[idx])


    # TODO: make a function that takes the standard deviation and the mean and uses this to calculate a certainty
    # this could for example be done by standard_deviation / mean. The lower this number, the higher the certainty
    # This number should then be used when evaluating what voters are going to vote on. You could for example
    # break it down into three groups, high certainty (certainty < 0.25), normal certainty (certainty ranging 0.25, 0.5)
    # low certainty (certainty >0.5). These numbers should be parameters that can be changed. This would be rather
    # complicated because you would then need to take this certainty level into account when ranking the predictions
    # in terms of highest to lowest. Additionally it would lead to a lot more parameters

    # We could also use the certainty as a multiplier. For example you could preference_prediction = mean * (1-certainty). The
    # less certain you are, the higher the certainty thus the lower the preference level is.
    # Or you could use preference_prediction = mean - standard_deviation * parameter_x. Where x describes how much
    # the standard_devation matters (a number between 0 and 1)
    # Another idea would be preference_prediction = mean - (standard_deviation * certainty * parameter_x). This would make
    # the agent give a higher preference_prediction of slot, to slots that are more certain to be around that mean.
    def __calculate_certainty_normal_distribution(self, mean, standard_deviation):
        return mean / standard_deviation

    # creates the list slots_preference_prediction. Here the function calculates how likely it is that agents
    # are going to vote for the time slots based on the normal distribution of the preferences
    def __create_slots_preference_prediction(self):
        # creates the list slots_preference_prediction
        for idx in range(self._n_time_slots):
            preference_prediction = self.__means_per_slot[idx] - self.__standard_deviation_per_slot[idx] * \
                                    self.__importance_standard_deviation
            self.__slots_preference_prediction.append(preference_prediction)
            self.__slots_preference_prediction_idx.append(idx)

        # The list is quick sorted from least likely to be voted on to most likely
        quick_sort.quick_sort(self.__slots_preference_prediction, self.__slots_preference_prediction_idx, 0,
                              len(self.__slots_preference_prediction) - 1)

        # Only the last n_slot_considerations are left, the other are removed
        del self.__slots_preference_prediction[:(self._n_time_slots - self.__n_slots_consideration)] # DEBUG, should be removed later

        del self.__slots_preference_prediction_idx[:(self._n_time_slots - self.__n_slots_consideration)]
        print(self.__slots_preference_prediction)

    # Takes at the slots that are most likely to get voted and makes a new list with the preference the agent
    # has for those particular time slots
    def __create_list_preference_popular_slots(self):
        for idx in self.__slots_preference_prediction_idx:
            preference = self._time_slot_preference[idx]
            self.__popular_time_slots_preference.append(preference)

    # Rank in terms of highest preference
    def __vote_for_slots_highest_preference(self):
        quick_sort.quick_sort(self.__popular_time_slots_preference, self.__popular_time_slots_idx, 0, self.__n_slots_consideration - 1)
        # Vote for n_votes time-slots with the highest preference from the n_slots_consideration most popular time slots
        for idx in range(self.__n_slots_consideration - self.__n_votes, self.__n_slots_consideration):
            self.environment.vote_time_slot(self.__popular_time_slots_idx[idx])
            self._time_slots_chosen.append(self.__popular_time_slots_idx[idx])

        # Quick sorts the n_slots_consideration most popular time slots in terms of the agents their preference, then
        # the list popular_time_slots_idx can be used to vote for the right time slots.
        quick_sort.quick_sort(self.__popular_time_slots_preference, self.__slots_preference_prediction_idx, 0,
                              self.__n_slots_consideration - 1)
        # Vote for n_votes time-slots with the highest preference from the n_slots_consideration most popular time slots
        for idx in range(self.__n_slots_consideration - self.__n_votes, self.__n_slots_consideration):
            self.environment.vote_time_slot(self.__slots_preference_prediction_idx[idx])
            self._time_slots_chosen.append(self.__slots_preference_prediction_idx[idx])

    # Debug duh
    def __print_debug(self):
        print(f"means_per_slot: ", self.__means_per_slot)
        print(f"standard deviation per slot: ", self.__standard_deviation_per_slot)

    def vote(self):
        self.__create_slots_preference_prediction()
        self.__create_list_preference_popular_slots()
        self.__vote_for_slots_highest_preference()
        self.__popular_time_slots_preference.clear()
        self.__popular_time_slots_idx.clear()
        self.__slots_preference_prediction_idx.clear()
        self.__slots_preference_prediction.clear() # DEBUG, should be removed later
        self.environment.remove_agent_from_voting_list()

        # TODO: make it so that preference for the slots changes per round
        # TODO: take into account how many votes each slot already has

