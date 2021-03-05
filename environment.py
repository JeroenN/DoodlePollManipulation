import quick_sort

# The class creates the time-slots and counts how often
# a certain time slot is chosen
class Environment:
    __n_time_slots = 0  # number of time-slots
    __time_slots = []  # How often each time slot is chosen
    initial_idx_time_slots = []  # The initial index of the time slots, when quick sort is used to find the most
                                 # popular time slots the original indexs should still be known
    __time_slots_chosen = []  # How often each time slot is chosen
    __idx_most_popular_time_slot = 0  # The idx of the most poular time slot
    __rank_popularity_time_slots = []
    __time_step = 0
    __willingness_agents = []
    __index_agents = []

    def __init__(self, number_of_slots=0):
        self.__n_time_slots = number_of_slots
        self.__create_time_slots()

    def __str__(self):
        return f"Environment with {self.__n_time_slots} time slots"

    # This function can be called by an agent to vote for that particular time slot
    # it also removes the first element from the willingness_agents list
    def vote_time_slot(self, index_time_slot):
        self.__time_slots[index_time_slot] += 1

    def remove_agent_from_voting_list(self):
        self.__willingness_agents.pop(0)
        self.__index_agents.pop(0)

    # This function can be called by an agent to see how often a time slot is voted for
    def get_time_slots(self):
        return self.__time_slots

    # Get the number of time slots
    def get_n_time_slots(self):
        return self.__n_time_slots

    # Determines the most popular time slot based on which time slots is most often chosen
    def determine_most_popular_time_slot(self):
        max = 0
        idx = 0
        for i in range(len(self.__time_slots)):
            if self.__time_slots[i] > max:
                max = self.__time_slots[i]
                idx = i
        self.__idx_most_popular_time_slot = idx

    # Using quick_sort to sort the time-slots based on popularity
    def rank_popularity_time_slots(self):
        n_elements = len(self.__time_slots)
        quick_sort.quick_sort(self.__time_slots, self.initial_idx_time_slots, 0, n_elements - 1)

    def get_most_popular_time_slot(self):
        return self.__idx_most_popular_time_slot

    # For each time slot the amount of times it is chosen is set to 0
    def __create_time_slots(self):
        for i in range(self.__n_time_slots):
            self.__time_slots.append(0)
            self.initial_idx_time_slots.append(i)

    def reset_enviroment(self, agents):
        for idx in range(len(self.__time_slots)):
            self.__time_slots[idx] = 0
        # TODO: make the willingness change each round
        self.determine_willingness(agents)
        self.rank_willingness()

    # Get the willingness from each agent and put it in a list
    def determine_willingness(self, agents):
        for idx in range(len(agents)):
            agent = agents[idx]
            self.__willingness_agents.append(agent.get_willingness())
            self.__index_agents.append(idx)

    # Quick-sort the willingness
    def rank_willingness(self):
        n_elements = len(self.__willingness_agents)
        quick_sort.quick_sort(self.__willingness_agents, self.__index_agents, 0, n_elements - 1)

    def get_index_agent_willingness(self):
        if self.__index_agents:
            return self.__index_agents[0]
        else:
            return None

    def increase_time(self):
        if self.__time_step >= 100: 
            return 0
        else: 
            self.__time_step += 1
            return 1

    def get_time(self):
        return self.__time_step
