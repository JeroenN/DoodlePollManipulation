from numpy.core.fromnumeric import mean
import quick_sort
import plots
import normal_distribution
from progress.bar import IncrementalBar
import numpy as np
import strategies
from environment import Environment
import csv


class Games:
    def __init__(self, agents, environment):
        self._agents = agents
        self._environment = environment

        self._social_welfare = 0
        self._social_bonus_utility = 0 # keeps track of the total utility that is gained from social bonus 
        self._min_utility = 0 # the utility of the agent with the lowest utility
        self._max_utility = 0 # the utility of the agent with the highest utility
        self._rounds = 10000 # number of rounds 
        self._social_welfare_scores = [] # keeps track of social welfare scores across rounds 
        self._min_utility_scores = [] # keeps track of minimum utility scores across rounds 
        self._max_utility_scores = [] # keeps track of maximum utility scores across rounds 
        self._n_agents = 0 # the total number of agents 
        self._n_standard_agents = 0 # the number of sincere agents 
        self._n_popular_agents = 0 # the number of popular agents 
        self._n_popular_prediction_agents = 0 # the number of popular prediction agents 
        self._mean_utility_popular_agents = [] # the mean utility of all popular agents 
        self._file = None

        self._calculate_number_of_agents()  # Determine how many agents there are of each type

    # Go through all the actions that have to be taken each round
    # 1. let the agents vote, 2. let the agents calculate the utility
    # 3. calculate social welfare and egalitarian welfare, 4. reset all the agents
    # their utility to 0 and set all the time slot votes to zero
    def _go_through_rounds(self, bonus_type=0):
        for _ in range(self._rounds):
            self._show_popular_prediction_agents_preferences()
            self._agents_vote()
            self._agents_calculate_utility()
            self.__calculate_social_welfare()
            self.__calculate_egalitarian_welfare()
            if bonus_type == 1:
                self.__calculate_social_bonus_utility()
            self._environment.reset(self._agents)

    # same as the previous except it can be used to store values for statistical analysis 
    # separated from the previous for less clutter in games that do not need/want statistics 
    def _go_through_rounds_statistics(self, parameter, bonus_type=0): 
        for _ in range(self._rounds):
            self._show_popular_prediction_agents_preferences()
            self._agents_vote()
            self._agents_calculate_utility()
            self.__save_utilities(parameter)
            if bonus_type == 1:
                self.__calculate_social_bonus_utility()
            self._environment.reset(self._agents)

    # Creates a list of all the preference from all the agents per time slot
    def __create_lists_preference_per_slot(self):
        n_slots = self._environment.get_n_time_slots()
        preferences_per_slot = []
        preferences = []
        for idx_slot in range(n_slots):
            for agent in self._agents:
                time_slot_preference_agent = agent.get_time_slot_preference(idx_slot)
                preferences.append(time_slot_preference_agent)
            preferences_per_slot.append(preferences[:])
            preferences.clear()

        return preferences_per_slot

    # Calculates the mean and the standard deviation with the functions from the file normal_distribution.py
    def __calculate_normal_distribution(self, arr):
        mean = normal_distribution.calculate_mean(arr)
        standard_deviation = normal_distribution.calculate_standard_deviation(arr, mean)
        return mean, standard_deviation

    # When this function is called, if there are agents with the 'popular prediction' strategy, then these
    # agents are given the normal distribution (the mean and the standard deviation) of the preference
    # per slot
    def _show_popular_prediction_agents_preferences(self):
        means_per_slot = []
        standard_deviations_per_slot = []
        # check if there is at least one agents with the 'popular prediction' strategy
        if self._n_popular_prediction_agents > 0:
            preferences_per_slot = self.__create_lists_preference_per_slot()
            for preferences in preferences_per_slot:
                mean, standard_deviation = self.__calculate_normal_distribution(preferences)
                means_per_slot.append(mean)
                standard_deviations_per_slot.append(standard_deviation)

            for agent in self._agents:
                if agent.get_strategy() == 'popular_prediction' or agent.get_strategy() == 'popular_prediction_social':
                    agent.set_normal_distribution(means_per_slot, standard_deviations_per_slot)

    # append the egalitarian and social welfare scores in lists, this is too keep track
    # of them over multiple runs
    def _append_scores_per_run(self):
        self._social_welfare_scores.append(self._social_welfare)
        self._min_utility_scores.append(self._min_utility)
        self._max_utility_scores.append(self._max_utility)

    # Set the social welfare and egalitarian welfare back to 0
    def _reset_scores(self):
        self._social_welfare = 0
        self._min_utility = 0
        self._max_utility = 0

    # Calculate how much agents there are of each type, also caclulate the total number of agents
    def _calculate_number_of_agents(self):
        # If this function is called multiple times then first the counts have to be reset
        self._n_standard_agents = 0
        self._n_popular_agents = 0
        self._n_popular_prediction_agents = 0
        for agent in self._agents:
            if agent.get_strategy() == "standard" or agent.get_strategy() == "strategy_social":
                self._n_standard_agents += 1
            if agent.get_strategy() == "popular" or agent.get_strategy() == "popular_social":
                self._n_popular_agents += 1
            if agent.get_strategy() == "popular_prediction" or agent.get_strategy() == "popular_prediction_social":
                self._n_popular_prediction_agents += 1

        self._n_agents = len(self._agents)

    # Make the agents vote for their desired time slots
    def _agents_vote(self):
        idx = self._environment.get_index_agent_willingness()
        while idx is not None:
            agent = self._agents[idx]
            agent.vote()  # Agents vote for their preferred time slots
            idx = self._environment.get_index_agent_willingness()

    # Make the agents calculate their utility
    def _agents_calculate_utility(self):
        # The agents calculate their utility based on the time slot picked. The most popular time slot is picked
        self._environment.determine_most_popular_time_slot()
        for agent in self._agents:
            agent.calculate_utility()
            agent.change_time_slot_preference()

    # Calculates the social welfare, duh
    def __calculate_social_welfare(self):
        for agent in self._agents:
            self._social_welfare += agent.get_utility()

    # calculates the total utility that has been earned from social bonus 
    def __calculate_social_bonus_utility(self):
        for agent in self._agents:
            self._social_bonus_utility += agent.get_social_utility()

    # finding min and max
    def __calculate_egalitarian_welfare(self):
        welfares = []
        welfare_idx = []

        for idx, agent in enumerate(self._agents):
            welfares.append(agent.get_utility())
            welfare_idx.append(idx)

        quick_sort.quick_sort(welfares, welfare_idx, 0, self._n_agents - 1)

        self._min_utility += welfares[0]
        self._max_utility += welfares[self._n_agents - 1]
    
    # calculates the mean utility of the current rounds and stores it in a csv file
    def __save_utilities(self, parameter):
        mean_utility = 0 
        welfares = []
        welfare_idx = []
        min_utility = 0 
        max_utility = 0

        for idx, agent in enumerate(self._agents):
            agent_utility = agent.get_utility()
            mean_utility += agent_utility
            welfares.append(agent_utility)
            welfare_idx.append(idx)
            self._social_welfare += agent_utility

        # prepare data 
        quick_sort.quick_sort(welfares, welfare_idx, 0, self._n_agents - 1)
        mean_utility = mean_utility / self._n_agents
        level = round(parameter, 1)

        # store for graph 
        self._min_utility += welfares[0]
        self._max_utility += welfares[self._n_agents - 1]

        # store for CSV
        min_utility = welfares[0]
        max_utility = welfares[self._n_agents - 1]

        # write to CSV 
        self._file.writerow([f'{level}', f'{mean_utility}', f'{min_utility}', f'{max_utility}'])

    # calculates the mean utility of the popular agents and then adds it to list mean_utility_popular_agents
    def _create_list_mean_utility(self, utility_agents, n_agents, n_runs):
        mean_utility = []
        for idx in range(n_runs):
            mean_utility.append(utility_agents[idx] / n_agents / self._rounds)

        return mean_utility

    def _print_strategies(self):
        for agent in self._agents:
            print(agent,
                  f", Strategy: {agent.get_strategy()}, Total utility: {agent.get_total_utility() / self._rounds}")

    def _print_social_welfare(self):
        print('\nSocial welfare: ', self._social_welfare / self._rounds)
        print('\nMean utility; ', (self._social_welfare / len(self._agents)) / self._rounds)

    def _print_social_utility(self):
        print(f'\nSocial welfare without social bonus:', (self._social_welfare- self._social_bonus_utility) / self._rounds)
        print(f'\nMean social bonus:', self._social_bonus_utility / self._rounds)

    def _print_egalitarian_welfare(self):
        print("\nMinimum utility ", self._min_utility / self._rounds)  # agent with smallest utility
        print("\nMaximum utility: ", self._max_utility / self._rounds)  # agent with largest utility

        # create new agents and reset the game to work with these new agents 
    def _create_agents(self, n_agents, n_pop_agents, n_pop_predic_agents, bonus_type):
        self._agents.clear()
        tot_agents = n_agents + n_pop_agents + n_pop_predic_agents

        for i in range(n_agents):
            agent = strategies.Standard(self._environment, tot_agents, i, bonus_type)
            self._agents.append(agent)
        for i in range(n_pop_agents):
            self._agents.append(strategies.Popular(self._environment, tot_agents, i+n_agents, bonus_type))
        
        self._n_agents = 0
        self._n_standard_agents = 0
        self._n_popular_agents = 0
        self._calculate_number_of_agents()
        self._environment.reset(self._agents)

    # converts the social welfare to mean utility and gets a mean across rounds of all values that can directly be plotted 
    def _prepare_for_plotting(self, runs):
        for idx in range(0, runs):
            self._social_welfare_scores[idx] = (self._social_welfare_scores[idx] / self._rounds) / self._n_agents
            self._min_utility_scores[idx] = self._min_utility_scores[idx] / self._rounds
            self._max_utility_scores[idx] = self._max_utility_scores[idx] / self._rounds

# the "standard" game 
class Normal(Games):
    def __init__(self, agents, environment, bonus_type):
        Games.__init__(self, agents, environment)
        self.__bonus_type = bonus_type 
        self.__play_game()

    def __print_results(self):
        print("Game ended! \n")
        self._print_strategies()
        self._print_social_welfare()
        self._print_egalitarian_welfare()
        
        # if the bonus type is 1, also print the utility without social bonus 
        if self.__bonus_type == 1: 
            self._print_social_utility()

    # If this is chosen the program is only run once, thus no parameters are changed
    def __play_game(self):
        self._go_through_rounds(self.__bonus_type)
        self._environment.rank_popularity_time_slots()
        self.__print_results()

# game used to test the effect of K and M (popular strategy) on welfare 
class KM(Games):
    def __init__(self, agents, environment, max_k, max_m):
        Games.__init__(self, agents, environment)
        self.__max_k = max_k
        self.__max_m = max_m
        self.__popular_agent_utility = []
        self.__list_k = []
        self.__list_m = []
        self.__n_runs = 0

        self.__calculate_number_of_runs()
        self.__play_game()

    # The program loops through k and m both starting at 1, each loop is one run. This functions calculates
    # in how many runs this results and stores it in __n_runs
    def __calculate_number_of_runs(self):
        self.__n_runs = (self.__max_k - 1) * (self.__max_m - 1)

    # Set the number of slots the agents are going to vote on (k) and the number of slots taken into
    # consideration (m). k always has to be equal or smaller than m. m is the number of most
    # popular slots that the popular agent looks at.
    def __set_km_popular_agents(self, k, m):
        for agent in self._agents:
            if agent.get_strategy() == "popular":
                agent.set_k(k)
                agent.set_m(m)

    # Prints all the different results that we have calculated
    def __print_results(self):
        print("Game ended! \n")
        # prints the strategy used by each agent and the average utility of each agent
        for agent in self._agents:
            print(agent,
                  ", Strategy: {agent.get_strategy()}, Total utility: {agent.get_total_utility() / self._rounds}")

        for idx in range(self.__n_runs):
            print("n_votes: ", self.__list_k[idx])
            print("n_considerations: ", self.__list_m[idx])
            print('Social welfare: ', self._social_welfare_scores[idx] / self._rounds)
            print('Mean utility; ', self._social_welfare_scores[idx] / self._n_agents / self._rounds)

            print('Minimum utility ', self._min_utility_scores[idx] / self._rounds)  # agent with smallest utility
            print("Maximum utility: ", self._max_utility_scores[idx] / self._rounds)  # agent with largest utility

            print("popular agent utility: ", self.__popular_agent_utility[idx] / self._rounds, "\n")

    # Each run this functions appends the utility of the popular agents to the list
    def __append_list_popular_agent_utility(self):
        for agent in self._agents:
            if agent.get_strategy() == "popular":
                self.__popular_agent_utility.append(agent.get_total_utility())
                agent.reset_total_utility()

    # keeps track what k and m were each run
    def __append_list_km(self, k, m):
        self.__list_k.append(k)
        self.__list_m.append(m)

    # The function that goes through all the steps for a successful game, storing the results and then
    # displaying the results in the form of text and a nice graph.
    #
    # The number of slots the agents are going to vote on (k) and the number of slots taken into
    # consideration (m) are changed each run. This results in a nice graph that show how k and m
    # affect the mean utility of agents using the popular strategy
    def __play_game(self):
        for k in range(1, self.__max_k):
            for m in range(1, self.__max_m):
                if not k > m:
                    self.__set_km_popular_agents(k, m)
                    self._go_through_rounds()

                self._append_scores_per_run()
                self.__append_list_popular_agent_utility()
                self.__append_list_km(k, m)
                self._reset_scores()

        self._environment.rank_popularity_time_slots()
        self.__print_results()
        mean_utility_popular_agents = self._create_list_mean_utility(self.__popular_agent_utility,
                                                                     self._n_popular_agents, self.__n_runs)
        plots.plot_3d_graph_cutoff(self.__list_k, self.__list_m, mean_utility_popular_agents, self.__max_k - 1,
                                   self.__max_m - 1,
                                   'votes per agent', 'slots taken into consideration per agent', 'mean utility',
                                   'mean utility with popular strategy')

# used to test the effect of number of agents and number of time slots on welfare 
class Agent_slot(Games):
    def __init__(self, agents, environment, max_agents, max_slots, percentage_strategic_agents, bonus_type):
        Games.__init__(self, agents, environment)
        self.__percentage_strategic_agents = percentage_strategic_agents
        self.__n_sincere_voters = 0
        self.__n_strategic_voters = 0
        # Set to four since if you have 25% strategic voters, the first game you can play with this is with 1
        # strategic voter and 3 sincere voters. If for each condition they are set to four the graphs can be more
        # easily compared
        self.__starting_n_agents = 4
        self.__starting_n_slots = 3
        self.__max_agents = max_agents
        self.__max_slots = max_slots
        self.__popular_agent_utility = []
        self.__list_slots = []
        self.__list_agents = []
        self.__n_runs = 0
        self.__bonus_type = bonus_type

        #self.__calculate_n_agent_per_type()
        self.__play_game()

    # The program loops through max_agents and max_slots both starting at 1, each loop is one run. This functions
    # calculates in how many runs this results and stores it in __n_runs
    def __calculate_number_of_runs(self):
        self.__n_runs = (self.__max_agents - self.__starting_n_agents + 1) * (self.__max_slots - self.__starting_n_slots + 1)

    # calculates how many sincere and strategic voters should be created
    def __calculate_n_agent_per_type(self, n_agents):
        self.__n_sincere_voters = round(n_agents * (1 - self.__percentage_strategic_agents / 100))
        self.__n_strategic_voters = n_agents - self.__n_sincere_voters
        self.__calculate_number_of_runs()

    # Changes the number of agents to fit with how many should be used in a particular run
    def __set_number_of_agents(self, n_agents):
        current_n_agents = len(self._agents)
        self._n_agents = n_agents
        # When the new number of agents that there are supposed to be is smaller than the current number of agents then
        # the agents are cleared and the new agents
        # are created. Otherwise, one agent is added to the number of agents
        if n_agents < current_n_agents:
            self._agents.clear()
            for i in range(n_agents):
                agent = strategies.Standard(self._environment, n_agents, i, self.__bonus_type)
                self._agents.append(agent)
        else:
            while n_agents != current_n_agents:
                agent = strategies.Standard(self._environment, n_agents, n_agents - 1, self.__bonus_type)
                self._agents.append(agent)
                current_n_agents += 1
        # DEBUG
        if n_agents != len(self._agents):
            print("ERROR: not enough agents were created in the agent_slot_game")


    def __set_number_of_agents_different_types(self, n_agents):
        self._n_agents = n_agents
        # Clears all the agents, then it create the number of sincere voters that have to created and next
        # The popular agents are created
        self.__calculate_n_agent_per_type(n_agents)
        self._agents.clear()
        for i in range(self.__n_sincere_voters):
            agent = strategies.Standard(self._environment, n_agents, i, self.__bonus_type)
            self._agents.append(agent)
        for i in range(self.__n_strategic_voters):
            agent = strategies.Popular(self._environment, n_agents, i + self.__n_sincere_voters, self.__bonus_type)
            self._agents.append(agent)

        #print("n_agents:", n_agents)
        #for agent in self._agents:
        #    print("strategy: ", agent.get_strategy())

        #print("")
        if n_agents != len(self._agents):
            print("ERROR: not enough agents were created in the agent_slot_game")

    # Tell the agents how many time slots there are and change for how many slots the agent has a certain preference
    def __inform_agents_n_slots(self, n_slots):
        for agent in self._agents:
            agent.set_n_time_slots(n_slots)
            agent.create_time_slot_preference()

    # Prints all the different results that we have calculated
    def __print_results(self):
        print("Game ended! \n")
        # prints the strategy used by each agent and the average utility of each agent
        for agent in self._agents:
            print(agent,
                  ", Strategy: {agent.get_strategy()}, Total utility: {agent.get_total_utility() / self._rounds}")

        for idx in range(self.__n_runs):
            print("n_slots: ", self.__list_slots[idx])
            print("n_agents: ", self.__list_agents[idx])
            print('Social welfare: ', self._social_welfare_scores[idx] / self._rounds)
            n_agents = self.__list_agents[idx]
            print('Mean utility; ', (self._social_welfare_scores[idx] / n_agents / self._rounds))

            print('Minimum utility ', self._min_utility_scores[idx] / self._rounds)  # agent with smallest utility
            print("Maximum utility: ", self._max_utility_scores[idx] / self._rounds)  # agent with largest utility
            print("\n")
    # Keep track of the number of agents and time slots each run
    def __append_parameters(self, n_slots, n_agents):
        self.__list_slots.append(n_slots)
        self.__list_agents.append(n_agents)

    def __create_list_mean_utility_varying_agents_per_run(self):
        mean_utility = []
        for idx in range(len(self._social_welfare_scores)):
            n_agents = self.__list_agents[idx]
            mean_utility.append(self._social_welfare_scores[idx] / n_agents / self._rounds)
        return mean_utility

    def determine_starting_n_agents_slots(self):
        pass

    def __play_game(self):
        for n_agents in range(self.__starting_n_agents, self.__max_agents + 1):
            if self.__percentage_strategic_agents == 0:
                self.__set_number_of_agents(n_agents)
            else:
                self.__set_number_of_agents_different_types(n_agents)
            for n_slots in range(self.__starting_n_slots, self.__max_slots + 1):
                self._environment.change_time_slots(n_slots)
                self.__inform_agents_n_slots(n_slots)
                self._calculate_number_of_agents()
                self._go_through_rounds()
                print("n_sincere_agents: ", self.__n_sincere_voters)
                print("n_pop_agents: ", self.__n_strategic_voters)

                self._append_scores_per_run()
                self.__append_parameters(n_slots, n_agents)
                self._reset_scores()
                self._environment.reset(self._agents)


        self._environment.rank_popularity_time_slots()
        self.__print_results()
        mean_utility = self.__create_list_mean_utility_varying_agents_per_run()
        plots.plot_3d_graph(self.__list_agents, self.__list_slots, mean_utility, self.__max_agents
                            - self.__starting_n_agents + 1, self.__max_slots - self.__starting_n_slots + 1,
                            'agents', 'time slots', 'mean utility', 'mean utility based on agents and time slots')

# used to test the effect of threshold on welfare 
class Threshold(Games):
    def __init__(self, agents, environment, bonus_type):
        Games.__init__(self, agents, environment)
        self.__game_type = int(input("What type of game do you want to play?\n1 = social welfare, 2 = price of anarchy\n")) # 1 = social welfare, 2 = price of anarchy
        self.__bonus_type = bonus_type #keeps track of the bonus type for when new agents have to be created

        self.__play_game()
        
    # creates the correct progress bar depending on game type 
    def __create_progress_bar(self):
        if self.__game_type == 1:
            bar = IncrementalBar('Progress', max=11)
        elif self.__game_type == 2:
            bar = IncrementalBar('Progress', max=22)

        return bar

    # changes the agents' thresholds
    def __set_threshold_normal_agents(self, threshold):
        for agent in self._agents:
            if agent.get_strategy() == "standard" or agent.get_strategy() == "standard_social":
                agent.set_threshold(threshold)

    # clear welfare scores
    def __clear_scores(self):
        self._social_welfare_scores.clear()
        self._min_utility_scores.clear()
        self._max_utility_scores.clear()
    
    # opens CSV file 
    def __open_file(self): 
        self._file = open('threshold_utilities.csv', mode='w')
        self._file = csv.writer(self._file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        self._file.writerow(['threshold', 'mean_utility', 'min_utility', 'max_utility'])

    # plays the game 
    def __play_game(self):
        self.__open_file()
        bar = self.__create_progress_bar()

        for threshold in np.arange(0, 1.1, 0.1):
            self.__set_threshold_normal_agents(threshold)
            self._go_through_rounds_statistics(parameter=threshold)
            self._append_scores_per_run()  # this is not divided by rounds yet
            self._reset_scores()
            bar.next()

        self._prepare_for_plotting(11)

        social_welfare_normal = self._social_welfare_scores.copy()
        min_normal = self._min_utility_scores.copy()
        max_normal = self._max_utility_scores.copy()

        # in case the price of anarchy needs to be found, new agents are created 
        if self.__game_type == 2:
            self._create_agents(0, self._n_standard_agents, 0, self.__bonus_type) # reverse the number of agents 
            self.__clear_scores()

            for threshold in np.arange(0, 1.1, 0.1):
                self._go_through_rounds_statistics(parameter=threshold)
                self._append_scores_per_run()
                self._reset_scores()
                bar.next()
            self._prepare_for_plotting(11)

        bar.finish()
        plots.plot_threshold_results(social_welfare_normal, self._social_welfare_scores, min_normal,
                                     self._min_utility_scores, max_normal, self._max_utility_scores, self.__game_type)

# used to test the effect of agent type / ratio on welfare 
class agent_type(Games):
    def __init__(self, agents, environment, bonus_type):
        Games.__init__(self, agents, environment)
        self.__bonus_type = bonus_type #keeps track of bonus type for when agents need to be created 
        self.__play_game()

    def __play_game(self):
        bar = IncrementalBar('Progress', max=self._n_agents + 1)

        for i in range(0, self._n_agents + 1):
            self._create_agents(self._n_agents - i, i, 0, self.__bonus_type)
            self._go_through_rounds()
            self._append_scores_per_run()
            self._reset_scores()
            bar.next()
        self._prepare_for_plotting(self._n_agents + 1)
        bar.finish()

        plots.plot_agent_results(self._social_welfare_scores, self._min_utility_scores, self._max_utility_scores,
                                 self._n_agents)

# used to test the effect of willingness on welfare  
class willingness(Games):
    def __init__(self, agents, environment, bonus_type):
        Games.__init__(self, agents, environment)
        self.__bonus_type = bonus_type #keeps track of the bonus type for when new agents have to be created
        self.__strategies = set()
        self.__pareto_agents = []
        self.__play_game()
    
    # creates pareto agents 
    def __create_willingness_agents(self, n_agents, n_pop_agents, n_pop_predic_agents):
        agents = []
        tot_agents = n_agents + n_pop_agents + n_pop_predic_agents

        for i in range(n_agents):
            agent = strategies.Standard(self._environment, tot_agents, i, self.__bonus_type)
            self._agents.append(agent)
            self.__pareto_agents.append(agent)
        for i in range(n_pop_agents):
            agent = (strategies.Popular(self._environment, tot_agents, i +n_agents, self.__bonus_type))
            self._agents.append(agent)
            self.__pareto_agents.append(agent)
        for i in range(n_pop_predic_agents):
            agent = (strategies.Popular_prediction(self._environment, tot_agents, i + n_agents + n_pop_agents, self.__bonus_type))
            self._agents.append(agent)
            self.__pareto_agents.append(agent)
            
        if self.__bonus_type == 1:
            n_social_agents = int(input("How many sincere social bonus pareto agents?"))
            n_social_pop_agents = int(input("How many popular social bonus pareto agents?"))
            n_social_pop_predic_agents = int(input("How many popular prediction social bonus agents?"))
            for i in range(n_social_agents):
                agent =strategies.Standard_social(self._environment, tot_agents + n_social_agents + n_social_pop_agents + n_social_pop_predic_agents, tot_agents + i, self.__bonus_type)
                self._agents.append(agent)
                self.__pareto_agents.append(agent)
            for i in range(n_social_pop_agents):
                agent = strategies.Popular_social(self._environment, tot_agents + n_social_agents + n_social_pop_agents + n_social_pop_predic_agents, i+tot_agents+n_social_agents, self.__bonus_type)
                self._agents.append(agent)
                self.__pareto_agents.append(agent)
            for i in range(n_social_pop_predic_agents):
                agent = strategies.Popular_prediction_social(self._environment, tot_agents + n_social_agents + n_social_pop_agents + n_social_pop_predic_agents, i+tot_agents+n_social_agents+n_social_pop_agents, self.__bonus_type)
                self._agents.append(agent)
                self.__pareto_agents.append(agent)

        self._calculate_number_of_agents()

    # creates the correct progress bar depending on game type 
    def __create_progress_bar(self):
        bar = IncrementalBar('Progress', max=11)
        return bar

    # changes the agents' willingness
    def __set_willingess(self, willingness):
        for agent in self.__pareto_agents:
            agent.set_willingness(willingness)
    
    # figure out agent types
    def __agent_types(self):
        for agent in self._agents: 
            self.__strategies.add(agent.get_strategy())

    # opens CSV file 
    def __open_file(self): 
        self._file = open('willingness_utilities.csv', mode='w')
        self._file = csv.writer(self._file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        self._file.writerow(['willingness', 'mean_utility', 'min_utility', 'max_utility'])
            
    def __play_game(self):              
        self.__create_willingness_agents(int(input("How many pareto standard agents?")), int(input("How many pareto popular agents?")), int(input("How many pareto popular prediction agents?")) )
        self.__open_file()
        self.__agent_types()
        bar = self.__create_progress_bar()


        # play game 
        for willingness in np.arange(0, 1.1, 0.1):
            self.__set_willingess(willingness)
            self._go_through_rounds_statistics(parameter = willingness)
            self._append_scores_per_run()  # this is not divided by rounds yet
            self._reset_scores()
            bar.next()
        
        # prepare results for plitting 
        self._prepare_for_plotting(11)

        bar.finish()

        # plot results 
        plots.plot_willingness_results(self._social_welfare_scores, self._min_utility_scores, self._max_utility_scores, self.__strategies)