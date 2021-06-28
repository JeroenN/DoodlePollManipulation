import quick_sort
import random

# The class creates the time-slots and counts how often
# a certain time slot is chosen
class Environment:

    def __init__(self, number_of_slots=0):
        self.__n_time_slots = number_of_slots   # number of time slots
        self.__time_slots_votes = []  # how often each time slot is chosen
        self.__initial_idx_time_slots = [] # the initial index of the time slots, when quick sort is used to find the most
                                           # popular time slots the original indexes should still be known
        self.__idx_most_popular_time_slot = 0 # the idx of the most popular time slot
        self.__willingness_agents = []
        self.__index_agents = []
        self.__create_time_slots()
        self.__popular_idx = 0

    def __str__(self):
        return "Environment with {self.__n_time_slots} time slots"

    # This function can be called by an agent to vote for that particular time slot
    # it also removes the first element from the willingness_agents list
    def vote_time_slot(self, index_time_slot):
        for idx in range(self.__n_time_slots):
            if index_time_slot == self.__initial_idx_time_slots[idx]:
                self.__time_slots_votes[idx] += 1
                break

    def remove_agent_from_voting_list(self):
        self.__willingness_agents.pop(0)
        self.__index_agents.pop(0)

    # This function can be called by an agent to see how often a time slot is voted for
    def get_time_slots(self):
        return self.__time_slots_votes

    # Get the number of time slots
    def get_n_time_slots(self):
        return self.__n_time_slots

    #def popular_voted_for_idx(self, idx):

    # Determines the most popular time slot based on which time slots is most often chosen
    def determine_most_popular_time_slot(self):
        max = 0
        idx = 0
        for i in range(self.__n_time_slots):
            if self.__time_slots_votes[i] > max:
                max = self.__time_slots_votes[i]
                idx = self.__initial_idx_time_slots[i]

        self.__idx_most_popular_time_slot = idx

        #idx_top_slots = []
        #for i in range(self.__n_time_slots):
        #    if self.__time_slots_votes[i] == max:
        #            idx_top_slots.append(self.__initial_idx_time_slots[i])

        #self.__idx_most_popular_time_slot = random.choice(idx_top_slots)

    # Using quick_sort to sort the time-slots based on popularity
    def rank_popularity_time_slots(self):
        # TODO: make a boolean that keeps track of whether the time slots have already been ranked
        # in terms of popularity. If this is not the case then this function should rank them
        # if it is the case that the time slots have already been ranked in terms of popularity
        # then this function should do nothing. When the order in the list is changed in some
        # different function then the boolean should be set to false again.
        n_elements = len(self.__time_slots_votes)
        quick_sort.quick_sort(self.__time_slots_votes, self.__initial_idx_time_slots, 0, n_elements - 1)


    def get_most_popular_time_slot(self):
        #print("most popular time slot: ", self.__idx_most_popular_time_slot)
        return self.__idx_most_popular_time_slot

    # For each time slot the amount of times it is chosen is set to 0
    def __create_time_slots(self):
        for i in range(self.__n_time_slots):
            self.__time_slots_votes.append(0)
            self.__initial_idx_time_slots.append(i)

    # Changes the number of time slots in the agent slot game and then sets the votes to 0 again
    def change_time_slots(self, n_time_slots):
        self.__n_time_slots = n_time_slots
        self.__time_slots_votes.clear()
        self.__initial_idx_time_slots.clear()

        for i in range(self.__n_time_slots):
            self.__time_slots_votes.append(0)
            self.__initial_idx_time_slots.append(i)

    # Reset all the time slots to zero votes, set the willingness of the agents
    # rank the agents in terms of willingness and reset the utilities of the agents
    def reset(self, agents):
        for idx in range(self.__n_time_slots):
            self.__time_slots_votes[idx] = 0
            self.__initial_idx_time_slots[idx] = idx

        self.determine_willingness(agents)
        self.rank_willingness()
        self.reset_utilities(agents)
        self.reset_timeslots_chosen(agents)

    # clears the agent lists and resets environment
    def reset_agents(self, agents):
        self.__willingness_agents.clear()
        self.__index_agents.clear()
        self.reset(agents)

    # Get the willingness from each agent and put it in a list
    def determine_willingness(self, agents):
        for idx in range(len(agents)):
            agent = agents[idx]
            self.__willingness_agents.append(agent.get_willingness())
            self.__index_agents.append(idx)

    def reset_utilities(self, agents):
        for agent in agents:
            agent.reset_utility()

    def reset_timeslots_chosen(self, agents):
        for agent in agents:
            agent.reset_timeslots_chosen()

    # Quick-sort the willingness
    def rank_willingness(self):
        # Commenting the following two lines out makes the agents vote in the order that they are created
        #n_elements = len(self.__willingness_agents)
        #quick_sort.quick_sort(self.__willingness_agents, self.__index_agents, 0, n_elements - 1)
        pass


    # After this function is called another function removes the first element. Thus everytime this function is
    # is called a new element will be given until the list is empty in which case it returns none.
    def get_index_agent_willingness(self):
        if self.__index_agents:
            return self.__index_agents[0]
        else:
            return None

    def get_initial_idx_time_slots(self):
        return self.__initial_idx_time_slots

    # From index_agents every time when a vote is cast by an agent an element is removed
    def get_n_agents_waiting_to_vote(self):
        return len(self.__index_agents)

    def get_index_agents(self):
        return self.__index_agents

    def get_number_of_willingness_agents(self):
        return len(self.__willingness_agents)

    def get_time_slot_votes(self):
        return self.__time_slots_votes