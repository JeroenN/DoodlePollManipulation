from agent import Agent
import quick_sort
import random_number_generator
import normal_distribution

# This is the standard strategy, agents with this strategy vote for all the time-slots for which the
# agent has a preference above or equal to the specified threshold
class Standard(Agent):

    def __init__(self, environment, n_agents, ID, bonus_type):
        Agent.__init__(self, environment, n_agents, ID, bonus_type)
        self.__threshold = 0.55  
        self.__ID = ID
        self._willingness = random_number_generator.generate_random_number_normal_distribution(0.4, 0.2, 0, 1)
        self._strategy = "standard"
        self.__n_agents = n_agents

    # vote for a time slot if the time slot preference for that time slot is above the threshold
    # Update also for the particular object that it voted on that specific time slot
    def vote(self):
        for i in range(self._n_time_slots):
            if self._time_slot_preference[i] >= self.__threshold:
                # only add social bonus when this agent is used for a social bonus game and when the cap hasn't been reached 
                if self._bonus_type == 1 and len(self._time_slots_chosen) < self._social_bonus_cap:
                    self.increase_utility()

                self.environment.vote_time_slot(i)
                self._time_slots_chosen.append(i)
             
        self.environment.remove_agent_from_voting_list()

    def set_threshold(self, threshold):
        self.__threshold = threshold

# sincere strategy adapted to use social bonus 
class Standard_social(Agent): 
    # this agent will vote for the k most unpopular slots as well as the p slots with the highest utility, which together are exactly the social bonus cap. 
    def __init__(self, environment, n_agents, ID, bonus_type):
        Agent.__init__(self, environment, n_agents, ID, bonus_type)
        self.__unpopular_time_slots_idx = []
        self.__available_time_slots_idx = []
        self.__available_time_slots_preference = []
        self.__ID = ID
        self._willingness = random_number_generator.generate_random_number_normal_distribution(0.4, 0.2, 0, 1)
        self._strategy = "standard_social"
        self.__n_agents = n_agents
        self.__n_unpopular = 2 # the number of unpopular slots that this agent will vote for 
        self.__p = self._social_bonus_cap - self.__n_unpopular# the number of high utility slots that this agent will vote for, might need to be changed to only include timeslots above threshold. d 

    # Goes over the first n_slots_consideration and adds the index of those to the array idx_unpopular_time_slots
    # also goes over the other slots and adds them to available time_slots 
    def __create_list_slots(self):
        self.environment.rank_popularity_time_slots()  # Ranks the time slots from least popular to most popular

        # Takes the indexes from the first n_slots_consideration time slots (they are ranked from least to most popular,
        # thus the n_slots_consideration most unpopular time slots) and puts to indexes in the list unpopular_time_slots_idx
        for idx in range(0, self.__n_unpopular):
            idx_time_slots = self.environment.get_initial_idx_time_slots()
            self.__unpopular_time_slots_idx.append(idx_time_slots[idx])

        for idx in range(self.__n_unpopular, self._n_time_slots):
            idx_time_slots = self.environment.get_initial_idx_time_slots()
            self.__available_time_slots_idx.append(idx_time_slots[idx])

    # Makes a new list with the preference for each available time slot, starting from the least popular to the most
    # popular. This is realized by taking the list __available_time_slot_idx which contains the indexes of the slots
    # starting with the idx of the least popular and moving up idx of the time slot which is the most popular
    def __create_list_preference_available_slots(self):
        for idx in self.__available_time_slots_idx:
            preference = self._time_slot_preference[idx]
            self.__available_time_slots_preference.append(preference)

    # vote for a time slot if the time slot preference for that time slot is above the threshold
    # Update also for the particular object that it voted on that specific time slot
    def vote(self):
        self.__create_list_slots()

        # sort the available timeslots based on preference 
        quick_sort.quick_sort(self.__available_time_slots_preference, self.__available_time_slots_idx, 0, len(self.__available_time_slots_preference)-1)

        # vote for all of the k most unpopular time slots
        for idx in range(0, self.__n_unpopular): 
            if (self._bonus_type == 1 and len(self._time_slots_chosen) < self._social_bonus_cap):
                self.increase_utility()
            self.environment.vote_time_slot(self.__unpopular_time_slots_idx[idx])
            self._time_slots_chosen.append(self.__unpopular_time_slots_idx[idx])

        # vote for p timeslots with the highest preference that aren't the most unpopular
        for idx in range(len(self.__available_time_slots_idx) - self.__p, len(self.__available_time_slots_idx)):
            if (self._bonus_type == 1 and len(self._time_slots_chosen) < self._social_bonus_cap):
                self.increase_utility()
            self.environment.vote_time_slot(self.__available_time_slots_idx[idx])
            self._time_slots_chosen.append(self.__available_time_slots_idx[idx])
        
        self.__available_time_slots_idx.clear()
        self.__available_time_slots_preference.clear()
        self.__unpopular_time_slots_idx.clear()
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
    def __init__(self, environment, n_agents, ID, bonus_type):
        Agent.__init__(self, environment, n_agents, ID, bonus_type)
        self.__popular_time_slots_idx = []
        self.__popular_time_slots_preference = []
        self.__n_slots_consideration = 3  # The number of time slots that will be taken in consideration\
        self.__n_votes = 1  # How many votes the agent should cast, this has to be always equal or greater than n_slots_consideration
        self._willingness = random_number_generator.generate_random_number_normal_distribution(0.8, 0.1, 0, 1)
        self._strategy = "popular"
        self.__ID = ID
        self.__n_agents = n_agents
        #self.__set_n_considerations_to_n_slots()
        #self.__set_n_votes_to_n_slots()


    # Makes sure that if there are less time slots available than the amount of slots the agent wants to take into
    # consideration, then the amount of time slots taken into consideration is set to the amount of time slots there
    # are
    def __set_n_considerations_to_n_slots(self):
        print("dskljfsdlk", self.environment.get_time_slots())
        if self.environment.get_n_time_slots() < self.__n_slots_consideration:
            self.__n_slots_consideration = self.environment.get_n_time_slots()

    # Makes sure that if there are less time slots available than the amount of slots the agent wants to vote on
    # , then the amount of time slots voted on is set to the amount of time slots there
    # are
    def __set_n_votes_to_n_slots(self):
        if self.environment.get_n_time_slots() < self.__n_votes:
            self.__n_votes = self.environment.get_n_time_slots()

    # Goes over the last n_slots_consideration and adds the index of those to the array idx_popular_time_slots
    def __create_list_popular_slots(self):
        self.environment.rank_popularity_time_slots()  # Ranks the time slots from least popular to most popular

        # Takes the indexes from the last n_slots_consideration time slots (they are ranked from least to most popular,
        # thus the n_slots_consideration most popular time slots) and puts to indexes in the list popular_time_slots_idx
        starting_idx_most_popular_slots = self._n_time_slots - self.__n_slots_consideration
        if starting_idx_most_popular_slots < 0:
            starting_idx_most_popular_slots = 0

        for idx in range(starting_idx_most_popular_slots, self._n_time_slots):
            idx_time_slots = self.environment.get_initial_idx_time_slots()
            self.__popular_time_slots_idx.append(idx_time_slots[idx])


    # Makes a new list with the preference for each popular time slot, starting from the least popular to the most
    # popular. This is realized by taking the list __popular_time_slot_idx which contains the indexes of the slots
    # starting with the idx of the least popular and moving up idx of the time slot which is the most popular
    def __create_list_preference_popular_slots(self):
        for idx in self.__popular_time_slots_idx:
            preference = self._time_slot_preference[idx]
            self.__popular_time_slots_preference.append(preference)

    def __debug(self):
        votes = self.environment.get_time_slots()
        initial_idx = self.environment

    # Rank in terms of highest preference
    def __vote_for_slots_highest_preference(self):
        # Quick sorts the n_slots_consideration most popular time slots in terms of the agents their preference, then
        # the list popular_time_slots_idx can be used to vote for the right time slots.
        quick_sort.quick_sort(self.__popular_time_slots_preference, self.__popular_time_slots_idx, 0,
                              self.__n_slots_consideration - 1)

        # Vote for n_votes time-slots with the highest preference from the n_slots_consideration most popular time slots
        for idx in range(self.__n_slots_consideration - self.__n_votes, self.__n_slots_consideration):
             # only add social bonus when this agent is used for a social bonus game and when the cap hasn't been reached 
            if (self._bonus_type == 1 and len(self._time_slots_chosen) < self._social_bonus_cap):
                self.increase_utility()
            self.environment.vote_time_slot(self.__popular_time_slots_idx[idx])
            self._time_slots_chosen.append(self.__popular_time_slots_idx[idx])

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

# popular strategy adapted to work with social bonus 
class Popular_social(Agent):
        #the social bonus variant of the popular agent doesn't just vote for the x most popular slots, it also votes for the y least popular songs 
    def __init__(self, environment, n_agents, ID, bonus_type):
        Agent.__init__(self, environment, n_agents, ID, bonus_type)
        self.__popular_time_slots_idx = []
        self.__unpopular_time_slots_idx = []
        self.__popular_time_slots_preference = []
        self.__n_slots_consideration = 5 # The number of time slots that will be taken in consideration\
        self.__n_votes = 3  # How many votes the agent should cast, this has to be always equal or greater than n_slots_consideration
        self._willingness = random_number_generator.generate_random_number_normal_distribution(0.8, 0.1, 0, 1)
        self._strategy = "popular_social"
        self.__ID = ID
        self.__n_agents = n_agents
        self.__n_unpopular = 1

    
    #creates a list of popular and unpopular slots 
    def __create_lists(self):
        self.environment.rank_popularity_time_slots()  # Ranks the time slots from least popular to most popular

        # Takes the indexes from the last n_slots_consideration time slots (they are ranked from least to most popular,
        # thus the n_slots_consideration most popular time slots) and puts to indexes in the list popular_time_slots_idx
        for idx in range(self._n_time_slots - self.__n_slots_consideration, self._n_time_slots):
            idx_time_slots = self.environment.get_initial_idx_time_slots()
            self.__popular_time_slots_idx.append(idx_time_slots[idx])

        # Takes the indexes from the first n_slots_consideration time slots (they are ranked from least to most popular,
        # thus the n_slots_consideration most unpopular time slots) and puts to indexes in the list unpopular_time_slots_idx
        for idx in range(0, self.__n_unpopular):
            idx_time_slots = self.environment.get_initial_idx_time_slots()
            self.__unpopular_time_slots_idx.append(idx_time_slots[idx])

    # Makes a new list with the preference for each popular time slot, starting from the least popular to the most
    # popular. This is realized by taking the list __popular_time_slot_idx which contains the indexes of the slots
    # starting with the idx of the least popular and moving up idx of the time slot which is the most popular
    def __create_list_preference_popular_slots(self):
        for idx in self.__popular_time_slots_idx:
            preference = self._time_slot_preference[idx]
            self.__popular_time_slots_preference.append(preference)

    def __debug(self):
        votes = self.environment.get_time_slots()
        initial_idx = self.environment

    # Rank in terms of highest preference
    def __vote_for_slots_highest_preference(self):
        # Quick sorts the n_slots_consideration most popular time slots in terms of the agents their preference, then
        # the list popular_time_slots_idx can be used to vote for the right time slots.
        quick_sort.quick_sort(self.__popular_time_slots_preference, self.__popular_time_slots_idx, 0, self.__n_slots_consideration - 1)

        # Vote for n_votes time-slots with the highest preference from the n_slots_consideration most popular time slots
        for idx in range(self.__n_slots_consideration - self.__n_votes, self.__n_slots_consideration):
             # only add social bonus when this agent is used for a social bonus game and when the cap hasn't been reached 
            if (self._bonus_type == 1 and len(self._time_slots_chosen) < self._social_bonus_cap):
                self.increase_utility()
            self.environment.vote_time_slot(self.__popular_time_slots_idx[idx])
            self._time_slots_chosen.append(self.__popular_time_slots_idx[idx])

    def __vote_for_slots_unpopular(self): 
        #vote for unpopular slots 
        for idx in range(0, self.__n_unpopular): 
            if (self._bonus_type == 1 and len(self._time_slots_chosen) < self._social_bonus_cap):
                self.increase_utility()
            self.environment.vote_time_slot(self.__unpopular_time_slots_idx[idx])
            self._time_slots_chosen.append(self.__unpopular_time_slots_idx[idx])

    def set_k(self, k):
        self.__n_votes = k

    def set_m(self, m):
        self.__n_slots_consideration = m

    def vote(self):
        self.__create_lists()
        self.__create_list_preference_popular_slots()
        self.__vote_for_slots_highest_preference()
        self.__vote_for_slots_unpopular()
        self.__popular_time_slots_preference.clear()
        self.__popular_time_slots_idx.clear()
        self.environment.remove_agent_from_voting_list()

# popular prediction strategy: attemps to predict the votes of other agents, and votes on predicted to be most popular time slots 
class Popular_prediction(Agent):

    def __init__(self, environment, n_agents, ID, bonus_type):
        Agent.__init__(self, environment, n_agents, ID, bonus_type)
        self.__preference_per_slot = []
        self.__means_per_slot = []
        self.__standard_deviation_per_slot = []
        self._strategy = 'popular_prediction'
        self._willingness = random_number_generator.generate_random_number_normal_distribution(0.2, 0.1, 0, 1)
        self.__n_slots_consideration = 5  # The number of time slots that will be taken in consideration\
        self.__n_votes = 2  # How many votes the agent should cast, this has to be always equal or greater than n_slots_consideration
        self.__popular_time_slots_idx = []
        self.__popular_time_slots_preference = []
        self.__slots_preference_prediction = []
        self.__slots_preference_prediction_idx = []
        # A parameter between 0 and around 3 ish. The lower this number, the less important the standard deviation is when
        # computing how each slot should be ranked in terms of how likely agents are expected to vote for a
        # certain time slot. The higher this number, the more important the standard deviation gets in this calculation
        self.__importance_standard_deviation = 0.5
        self.__n_agents = n_agents

    def set_normal_distribution(self, means_per_slot, standard_deviation_per_slot):
        self.__means_per_slot = means_per_slot
        self.__standard_deviation_per_slot = standard_deviation_per_slot


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
            # How popular each time slot is, preference_prediction, is calculated by taking the mean of the preferences
            # from the time slot minus the standard_deviation times a parameter that determines how important the
            # standard deviation. To account for how often a slot is voted on the times that the slots is voted
            # on is divided by the number of agents (minus the agent their selfs). If their are no votes
            # this last part doesn't matter, however when this strategy is used later in the game and thus many
            # agents have already voted then this becomes more important than the prediction of the mean minus
            # the standard deviation
            preference_prediction = self.__means_per_slot[idx]\
                                    #- self.__standard_deviation_per_slot[idx] * \
                                    #self.__importance_standard_deviation + self.environment.get_time_slots()[idx] \
                                    #/ (self.__n_agents - 1)

            self.__slots_preference_prediction.append(preference_prediction)
            self.__slots_preference_prediction_idx.append(idx)

        # The list is quick sorted from least likely to be voted on to most likely
        quick_sort.quick_sort(self.__slots_preference_prediction, self.__slots_preference_prediction_idx, 0,
                              len(self.__slots_preference_prediction) - 1)

        # Only the last n_slot_considerations are left, the other are removed
        del self.__slots_preference_prediction[:(self._n_time_slots - self.__n_slots_consideration)] # DEBUG, should be removed later

        del self.__slots_preference_prediction_idx[:(self._n_time_slots - self.__n_slots_consideration)]
        #print(self.__slots_preference_prediction)

    # Takes at the slots that are most likely to get voted and makes a new list with the preference the agent
    # has for those particular time slots
    def __create_list_preference_popular_slots(self):
        for idx in self.__slots_preference_prediction_idx:
            preference = self._time_slot_preference[idx]
            self.__popular_time_slots_preference.append(preference)

    # Rank in terms of highest preference
    def __vote_for_slots_highest_preference(self):
        #print(f"len(popular_time_slot_pref: ", len(self.__popular_time_slots_preference), "len(self.__popular_time_slots_idx): ", len(self.__popular_time_slots_idx), "n_slot_considerations: ", self.__n_slots_consideration)
        # Quick sorts the n_slots_consideration most popular time slots in terms of the agents their preference, then
        # the list popular_time_slots_idx can be used to vote for the right time slots.
        quick_sort.quick_sort(self.__popular_time_slots_preference, self.__slots_preference_prediction_idx, 0,
                              self.__n_slots_consideration - 1)
        # Vote for n_votes time-slots with the highest preference from the n_slots_consideration most popular time slots
        for idx in range(self.__n_slots_consideration - self.__n_votes, self.__n_slots_consideration):
            # only add social bonus when this agent is used for a social bonus game and when the cap hasn't been reached 
            if self._bonus_type == 1 and len(self._time_slots_chosen) < self._social_bonus_cap:
                self.increase_utility()

            self.environment.vote_time_slot(self.__slots_preference_prediction_idx[idx])
            self._time_slots_chosen.append(self.__slots_preference_prediction_idx[idx])

    # Debug duh
    def __print_debug(self):
        print(f"means_per_slot: ", self.__means_per_slot)
        print(f"standard deviation per slot: ", self.__standard_deviation_per_slot)
        for idx in range(self._n_time_slots):
            preference_prediction = self.__means_per_slot[idx] - self.__standard_deviation_per_slot[idx] * \
                                    self.__importance_standard_deviation + self.environment.get_time_slots()[idx] \
                                    / (self.__n_agents - 1)
            print(f"environment.get_time_slots()[", idx, "] /  _n_agents: ", self.environment.get_time_slots()[idx], "/"
              , self.__n_agents, " = ", self.environment.get_time_slots()[idx] / self.__n_agents)
            print(f"preference prediction: ", preference_prediction)

    def vote(self):
        self.__create_slots_preference_prediction()
        self.__create_list_preference_popular_slots()
        self.__vote_for_slots_highest_preference()
        self.__popular_time_slots_preference.clear()
        self.__popular_time_slots_idx.clear()
        self.__slots_preference_prediction_idx.clear()
        self.__slots_preference_prediction.clear() # DEBUG, should be removed later
        self.environment.remove_agent_from_voting_list()

    



# popular prediction strategy adapted to work with social bonus 
class Popular_prediction_social(Agent):

    def __init__(self, environment, n_agents, ID, bonus_type):
        Agent.__init__(self, environment, n_agents, ID, bonus_type)
        self.__preference_per_slot = []
        self.__means_per_slot = []
        self.__standard_deviation_per_slot = []
        self._strategy = 'popular_prediction_social'
        self._willingness = random_number_generator.generate_random_number_normal_distribution(0.1, 0.2, 0, 1)
        self.__n_slots_consideration = 5  # The number of time slots that will be taken in consideration\
        self.__n_votes = 2  # How many votes the agent should cast, this has to be always equal or greater than n_slots_consideration
        self.__popular_time_slots_idx = []
        self.__popular_time_slots_preference = []
        self.__slots_preference_prediction = []
        self.__slots_preference_prediction_idx = []
        # A parameter between 0 and around 3 ish. The lower this number, the less important the standard deviation is when
        # computing how each slot should be ranked in terms of how likely agents are expected to vote for a
        # certain time slot. The higher this number, the more important the standard deviation gets in this calculation
        self.__importance_standard_deviation = 0.5
        self.__n_agents = n_agents
        self.__n_unpopular = 1 # the number of unpopular slots an agent should vote for in order to reach the social bonus cap
        self.__unpopular_time_slots_idx = [] #stores the indexes of unpopular time slots for which the agent should vote 

    def set_normal_distribution(self, means_per_slot, standard_deviation_per_slot):
        self.__means_per_slot = means_per_slot
        self.__standard_deviation_per_slot = standard_deviation_per_slot


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
            # How popular each time slot is, preference_prediction, is calculated by taking the mean of the preferences
            # from the time slot minus the standard_deviation times a parameter that determines how important the
            # standard deviation. To account for how often a slot is voted on the times that the slots is voted
            # on is divided by the number of agents (minus the agent their selfs). If their are no votes
            # this last part doesn't matter, however when this strategy is used later in the game and thus many
            # agents have already voted then this becomes more important than the prediction of the mean minus
            # the standard deviation
            preference_prediction = self.__means_per_slot[idx]

            self.__slots_preference_prediction.append(preference_prediction)
            self.__slots_preference_prediction_idx.append(idx)

        # The list is quick sorted from least likely to be voted on to most likely
        quick_sort.quick_sort(self.__slots_preference_prediction, self.__slots_preference_prediction_idx, 0,
                              len(self.__slots_preference_prediction) - 1)

        # Only the last n_slot_considerations are left, the other are removed
        del self.__slots_preference_prediction[:(self._n_time_slots - self.__n_slots_consideration)] # DEBUG, should be removed later

        del self.__slots_preference_prediction_idx[:(self._n_time_slots - self.__n_slots_consideration)]
        #print(self.__slots_preference_prediction)

    # created list of unpopular slots by ranking the time slots from least popular to most popular and taking the 
    # first x slots 
    def __create_list_unpopular(self):
        self.environment.rank_popularity_time_slots()  # Ranks the time slots from least popular to most popular

        # Takes the indexes from the first n_slots_consideration time slots (they are ranked from least to most popular,
        # thus the n_slots_consideration most unpopular time slots) and puts to indexes in the list unpopular_time_slots_idx
        for idx in range(0, self.__n_unpopular):
            idx_time_slots = self.environment.get_initial_idx_time_slots()
            self.__unpopular_time_slots_idx.append(idx_time_slots[idx])

    # Takes at the slots that are most likely to get voted and makes a new list with the preference the agent
    # has for those particular time slots
    def __create_list_preference_popular_slots(self):
        for idx in self.__slots_preference_prediction_idx:
            preference = self._time_slot_preference[idx]
            self.__popular_time_slots_preference.append(preference)

    # Rank in terms of highest preference
    def __vote_for_slots_highest_preference(self):
        #print(f"len(popular_time_slot_pref: ", len(self.__popular_time_slots_preference), "len(self.__popular_time_slots_idx): ", len(self.__popular_time_slots_idx), "n_slot_considerations: ", self.__n_slots_consideration)
        # Quick sorts the n_slots_consideration most popular time slots in terms of the agents their preference, then
        # the list popular_time_slots_idx can be used to vote for the right time slots.
        quick_sort.quick_sort(self.__popular_time_slots_preference, self.__slots_preference_prediction_idx, 0,
                              self.__n_slots_consideration - 1)
        # Vote for n_votes time-slots with the highest preference from the n_slots_consideration most popular time slots
        for idx in range(self.__n_slots_consideration - self.__n_votes, self.__n_slots_consideration):
            # only add social bonus when this agent is used for a social bonus game and when the cap hasn't been reached 
            if self._bonus_type == 1 and len(self._time_slots_chosen) < self._social_bonus_cap:
                self.increase_utility()

            self.environment.vote_time_slot(self.__slots_preference_prediction_idx[idx])
            self._time_slots_chosen.append(self.__slots_preference_prediction_idx[idx])

    def __vote_for_slots_unpopular(self): 
    #vote for unpopular slots 
        for idx in range(0, self.__n_unpopular): 
            if (self._bonus_type == 1 and len(self._time_slots_chosen) < self._social_bonus_cap):
                self.increase_utility()
            self.environment.vote_time_slot(self.__unpopular_time_slots_idx[idx])
            self._time_slots_chosen.append(self.__unpopular_time_slots_idx[idx])

    # Debug duh
    def __print_debug(self):
        print(f"means_per_slot: ", self.__means_per_slot)
        print(f"standard deviation per slot: ", self.__standard_deviation_per_slot)
        for idx in range(self._n_time_slots):
            preference_prediction = self.__means_per_slot[idx] - self.__standard_deviation_per_slot[idx] * \
                                    self.__importance_standard_deviation + self.environment.get_time_slots()[idx] \
                                    / (self.__n_agents - 1)
            print(f"environment.get_time_slots()[", idx, "] /  _n_agents: ", self.environment.get_time_slots()[idx], "/"
              , self.__n_agents, " = ", self.environment.get_time_slots()[idx] / self.__n_agents)
            print(f"preference prediction: ", preference_prediction)

    def vote(self):
        self.__create_slots_preference_prediction()
        self.__create_list_unpopular()
        self.__create_list_preference_popular_slots()
        self.__vote_for_slots_highest_preference()
        self.__vote_for_slots_unpopular()
        self.__popular_time_slots_preference.clear()
        self.__popular_time_slots_idx.clear()
        self.__slots_preference_prediction_idx.clear()
        self.__slots_preference_prediction.clear() # DEBUG, should be removed later
        self.environment.remove_agent_from_voting_list()
