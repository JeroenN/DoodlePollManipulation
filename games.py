import quick_sort
import plots
import normal_distribution
import numpy as np
import strategies
import csv
import pandas as pd
import math
from environment import Environment


class Games:
    def __init__(self, agents, environment):
        self._agents = agents
        self._environment = environment

        self._social_welfare = 0
        self._social_bonus_utility = 0  # keeps track of the total utility that is gained from social bonus
        self._min_utility = 0
        self._min_indexes = []
        self._max_utility = 0

        self._rounds = 20
        self._social_welfare_scores = []
        self._min_utility_scores = []
        self._max_utility_scores = []
        self._n_agents = 0
        self._n_standard_agents = 0
        self._n_popular_agents = 0
        self._n_popular_prediction_agents = 0
        self._mean_utility_popular_agents = []

        self._mean_of_mean_utilities_sincere = 0
        self._mean_of_mean_utilities_popular = 0
        self._mean_of_mean_utilities_sincere_per_round = []
        self._mean_utility_strategic = []

        self._top = 6
        self._preference = 0

        self._calculate_number_of_agents()  # Determine how many agents there are of each type

    def __mean_of_mean_utilities(self):
        for agent in self._agents:
            if agent.get_strategy() == "standard":
                self._mean_of_mean_utilities_sincere += agent.get_utility()
        for agent in self._agents:
            if agent.get_strategy() == "popular":
                self._mean_of_mean_utilities_popular += agent.get_utility()

    def __append_scores_per_round(self):
        # calculate the mean of the mean utilities of the sincere agents, then append this for every round. Nex
        # a function should be made that export this list to an .csv file.
        mean_of_mean_utilities_sincere = 0
        for agent in self._agents:
            if agent.get_strategy() == "standard":
                mean_of_mean_utilities_sincere += agent.get_utility()

        mean_of_mean_utilities_sincere /= self._n_standard_agents
        self._mean_of_mean_utilities_sincere_per_round.append(mean_of_mean_utilities_sincere)

        # For the popular agent
        for agent in self._agents:
            if agent.get_strategy() == "standard":
                # if agent.get_utility() < 0.9:
                #    self._mean_utility_strategic.append(agent.get_utility()+0.01)
                # else:
                self._mean_utility_strategic.append(agent.get_utility())
                break

    def __reset_willingness(self):
        for agent in self._agents:
            agent.set_willingness(agent.willingness_mean, agent.willingness_sd)

    # Go through all the actions that have to be taken each round
    # 1. let the agents vote, 2. let the agents calculate the utility
    # 3. calculate social welfare and egalitarian welfare, 4. reset all the agents
    # their utility to 0 and set all the time slot votes to zero
    def _go_through_rounds(self, bonus_type=0):
        for _ in range(self._rounds):
            self._show_popular_prediction_agents_preferences()
            self._agents_vote()
            self._agents_calculate_utility()
            self.__mean_of_mean_utilities()
            # self.__append_scores_per_round()
            self.__calculate_social_welfare()
            self.__calculate_egalitarian_welfare()
            # self.__top_slot_preference()
            # self.__reset_willingness()
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
                if agent.get_strategy() == 'popular_prediction':
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
        self._preference = 0

    # Calculate how much agents there are of each type, also caclulate the total number of agents
    def _calculate_number_of_agents(self):
        # If this function is called multiple times then first the counts have to be reset
        self._n_standard_agents = 0
        self._n_popular_agents = 0
        self._n_popular_prediction_agents = 0
        for agent in self._agents:
            if agent.get_strategy() == "standard":
                self._n_standard_agents += 1
            if agent.get_strategy() == "popular":
                self._n_popular_agents += 1
            if agent.get_strategy() == "popular_prediction":
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

    # FIXME: using quicksort is rather in efficient for this problem, just use the standard method for
    # finding min and max
    def __calculate_egalitarian_welfare(self):
        welfares = []
        welfare_idx = []

        for idx, agent in enumerate(self._agents):
            welfares.append(agent.get_utility())
            welfare_idx.append(idx)

        quick_sort.quick_sort(welfares, welfare_idx, 0, self._n_agents - 1)

        self._min_utility += welfares[0]
        self._min_indexes.append(welfare_idx[0])
        self._max_utility += welfares[self._n_agents - 1]

    # Counts for each agent how often they were the agent that got the lowest welfare
    def __histogram_idx_min_utility(self):
        histogram_idx_min_utility = [0] * self._n_agents
        for element in self._min_indexes:
            histogram_idx_min_utility[element] += 1

        return histogram_idx_min_utility

    # calculates the mean utility of the popular agents and then adds it to list mean_utility_popular_agents
    def _create_list_mean_utility(self, utility_agents, n_agents, n_runs):
        mean_utility = []
        for idx in range(n_runs):
            mean_utility.append(utility_agents[idx] / n_agents / self._rounds)

        return mean_utility

    # Takes the idx of the voter in question, compares this with the list 'voter_order' this list
    # starts with the idx of the agent that votes first and goes up from there. This comparison
    # can be counted, how many element have to be cycled through to find the matching idx, and this tells
    # us what the voting place is of that particular agent (when that agent votes in comparison to the others).
    def _determine_voter_place(self, idx):
        voter_place = 0
        voter_order = self._environment.get_index_agents()
        while idx != voter_order[voter_place]:
            voter_place += 1
        return voter_place

    def _print_strategies(self):
        for idx in range(len(self._agents)):
            print(self._agents[idx], ", Strategy: ", self._agents[idx].get_strategy(), ", Total utility: ",
                  self._agents[idx].get_total_utility() / self._rounds, "pref slot won: ", self._agents[
                      idx].get_n_preferred_slot_won() / self._rounds)  # , "voter: ", self._determine_voter_place(idx))
            # print(agent.get_total_utility() / self._rounds)

    def _print_social_welfare(self):
        print('\nSocial welfare: ', self._social_welfare / self._rounds)
        print('\nMean utility; ', (self._social_welfare / len(self._agents)) / self._rounds)

    def _print_mean_of_mean_utilities(self):
        if self._n_standard_agents > 0:
            print("\nMean of mean utility sincere",
                  self._mean_of_mean_utilities_sincere / self._n_standard_agents / self._rounds)
        if self._n_popular_agents > 0:
            print("\nMean of mean utility popular",
                  self._mean_of_mean_utilities_popular / self._n_popular_agents / self._rounds)

    def _print_social_utility(self):
        print(
        '\nSocial welfare without social bonus:', (self._social_welfare - self._social_bonus_utility) / self._rounds)
        print('\nMean social bonus:', self._social_bonus_utility / self._rounds)

    def _print_egalitarian_welfare(self):
        print("\nMinimum utility ", self._min_utility / self._rounds)  # agent with smallest utility
        print(self.__histogram_idx_min_utility())
        print("\nMaximum utility: ", self._max_utility / self._rounds)  # agent with largest utility

    def _print_top_preference(self):
        print("top preference: ", self._preference / (self._n_agents * self._top * self._rounds))

        # create new agents and reset the game to work with these new agents

    def _create_agents(self, n_agents, n_pop_agents, n_pop_predic_agents, bonus_type):
        self._agents.clear()
        tot_agents = n_agents + n_pop_agents + n_pop_predic_agents

        for i in range(n_agents):
            agent = strategies.Standard(self._environment, tot_agents, i, bonus_type)
            self._agents.append(agent)
        for i in range(n_pop_agents):
            self._agents.append(strategies.Popular(self._environment, tot_agents, i + n_agents, bonus_type))

        self._n_agents = 0
        self._n_standard_agents = 0
        self._n_popular_agents = 0
        self._calculate_number_of_agents()
        self._environment.reset(self._agents)

    def _prepare_for_plotting(self, runs):
        for idx in range(0, runs):
            self._social_welfare_scores[idx] = (self._social_welfare_scores[idx] / self._rounds) / self._n_agents
            self._min_utility_scores[idx] = self._min_utility_scores[idx] / self._rounds
            self._max_utility_scores[idx] = self._max_utility_scores[idx] / self._rounds

    def __top_slot_preference(self):
        for agent in self._agents:
            slot_preference = agent.get_list_slot_preference()
            useless_list = list(range(0, self._environment.get_n_time_slots()))
            quick_sort.quick_sort(slot_preference, useless_list, 0, len(slot_preference) - 1)
            for i in range(len(slot_preference) - int(self._top), len(slot_preference)):
                self._preference += slot_preference[i]


class Normal(Games):
    def __init__(self, agents, environment, bonus_type):
        Games.__init__(self, agents, environment)
        self.__bonus_type = bonus_type
        self.__play_game()

    def __create_csv_file(self):
        df = pd.DataFrame(self._mean_utility_strategic)
        df.to_csv("sincere_utility.csv", index=False)

    def __print_results(self):
        print("Game ended! \n")
        self._print_strategies()
        self._print_social_welfare()
        self._print_mean_of_mean_utilities()
        self._print_egalitarian_welfare()
        self._print_top_preference()

        # if the bonus type is 1, also print the utility without social bonus
        if self.__bonus_type == 1:
            self._print_social_utility()

    # If this is chosen the program is only run once, thus no parameters are changed
    def __play_game(self):
        self._go_through_rounds(self.__bonus_type)
        self._environment.rank_popularity_time_slots()
        self.__print_results()
        self.__create_csv_file()


class Distribution(Games):
    def __init__(self, agents, environment, tot_agents):
        Games.__init__(self, agents, environment)
        self.__bonus_type = 0
        self.__tot_agents = tot_agents
        self.__play_game()

    def __create_csv_file(self):
        df = pd.DataFrame(self._mean_of_mean_utilities_sincere_per_round)
        df.to_csv("nine_sincere_mean_utilities.csv", index=False)

    def __print_results(self):
        print("Game ended! \n")
        self._print_strategies()
        self._print_social_welfare()
        self._print_mean_of_mean_utilities()
        self._print_egalitarian_welfare()

        # if the bonus type is 1, also print the utility without social bonus
        if self.__bonus_type == 1:
            self._print_social_utility()

    def __reset_scores(self):
        self._social_welfare_scores.clear()
        self._min_utility_scores.clear()
        self._max_utility_scores.clear()
        self._mean_of_mean_utilities_sincere = 0
        self._mean_of_mean_utilities_popular = 0
        self._mean_of_mean_utilities_sincere_per_round.clear()
        self._social_welfare = 0
        self._social_bonus_utility = 0  # keeps track of the total utility that is gained from social bonus
        self._min_utility = 0
        self._min_indexes.clear()
        self._max_utility = 0

    def __create_agents(self, n_sincere, n_pop):
        self._n_agents = n_sincere + n_pop
        self._n_popular_prediction_agents = n_sincere
        self._n_popular_agents = n_pop
        self._agents.clear()
        for i in range(n_sincere):
            agent = strategies.Popular_prediction(self._environment, self._n_agents, i, self.__bonus_type)
            self._agents.append(agent)
        for i in range(n_pop):
            agent = strategies.Mix_popular_adapt(self._environment, self._n_agents, i + n_sincere, self.__bonus_type)
            self._agents.append(agent)

    # If this is chosen the program is only run once, thus no parameters are changed
    def __play_game(self):
        for n_pop in range(0, self.__tot_agents + 1):
            n_sincere = self.__tot_agents - n_pop
            self.__create_agents(n_sincere, n_pop)
            print("n_pop: ", n_pop)
            print("n_predict", n_sincere)
            self._go_through_rounds(self.__bonus_type)
            self._environment.rank_popularity_time_slots()
            self.__print_results()
            self.__reset_scores()
            # self.__create_csv_file()


class Distribution_50(Games):
    def __init__(self, agents, environment, tot_agents):
        Games.__init__(self, agents, environment)
        self.__bonus_type = 0
        self.__tot_agents = tot_agents
        self.__play_game()

    def __create_csv_file(self):
        df = pd.DataFrame(self._mean_of_mean_utilities_sincere_per_round)
        df.to_csv("nine_sincere_mean_utilities.csv", index=False)

    def __print_results(self):
        self._print_social_welfare()
        max = 0
        for agent in self._agents:
            if agent.get_strategy() == "popular_prediction":
                utility = agent.get_total_utility() / self._rounds
                if utility > max:
                    max = utility
        print("popular agent utility: ", max)
        self._print_mean_of_mean_utilities()

    def __reset_scores(self):
        self._social_welfare_scores.clear()
        self._min_utility_scores.clear()
        self._max_utility_scores.clear()
        self._mean_of_mean_utilities_sincere = 0
        self._mean_of_mean_utilities_popular = 0
        self._mean_of_mean_utilities_sincere_per_round.clear()
        self._social_welfare = 0
        self._social_bonus_utility = 0  # keeps track of the total utility that is gained from social bonus
        self._min_utility = 0
        self._min_indexes.clear()
        self._max_utility = 0

    def __create_agents(self, n_tot):
        n_pop = math.floor(n_tot * 0.4) + 1  # 40% or less of the agents are popular, by rounding it down it is never
        # more than 40%
        n_sincere = n_tot - n_pop
        self._n_agents = n_sincere + n_pop
        self._n_standard_agents = n_sincere
        self._n_popular_prediction_agents = n_pop
        self._agents.clear()
        for i in range(n_sincere):
            agent = strategies.Standard(self._environment, self._n_agents, i, self.__bonus_type)
            self._agents.append(agent)
        for i in range(n_pop):
            agent = strategies.Popular_prediction(self._environment, self._n_agents, i + n_sincere, self.__bonus_type)
            self._agents.append(agent)

    # If this is chosen the program is only run once, thus no parameters are changed
    def __play_game(self):
        for n_tot in range(5, self.__tot_agents + 1, 5):
            self.__create_agents(n_tot)
            print("n_pop_predict: ", self._n_popular_prediction_agents)
            print("n_sincere", self._n_standard_agents)
            self._go_through_rounds(self.__bonus_type)
            self._environment.rank_popularity_time_slots()
            self.__print_results()
            self.__reset_scores()
            # self.__create_csv_file()


class KM(Games):
    def __init__(self, agents, environment):
        Games.__init__(self, agents, environment)
        self.__max_k = environment.get_n_time_slots() + 1
        self.__max_m = environment.get_n_time_slots() + 1
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
            if agent.get_strategy() == "popular":  # "mix_adaptable_popular":
                # if agent.get_pop_adapt() == 0:  # Checks whether it is the normal or popular strategy
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
            if agent.get_strategy() == "popular":  # "mix_adaptable_popular":
                # if agent.get_pop_adapt() == 0:          #Checks whether it is the normal or popular strategy
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
                    print("k: ", k, "m: ", m)
                    self.__set_km_popular_agents(k, m)
                    self._go_through_rounds()

                self._append_scores_per_run()
                self.__append_list_popular_agent_utility()
                self.__append_list_km(k, m)
                self._reset_scores()

        self._environment.rank_popularity_time_slots()
        self.__print_results()
        mean_utility_popular_agents = self._create_list_mean_utility(self.__popular_agent_utility,
                                                                     1,  # self._n_popular_agents,
                                                                     self.__n_runs)
        print(mean_utility_popular_agents)
        # plots.plot_3d_graph_cutoff(self.__list_m, self.__list_k, mean_utility_popular_agents, self.__max_m - 1,
        #                           self.__max_k - 1, 'slots taken into consideration per agent',
        #                           'votes per agent',  'mean utility', 'mean utility with popular strategy')
        plots.plot_heatmap(self.__list_m, self.__list_k, mean_utility_popular_agents,
                           'slots taken into consideration per agent', 'votes per agent',
                           'mean utility', 'mean utility with popular strategy')


class KM_predict(Games):
    def __init__(self, agents, environment):
        Games.__init__(self, agents, environment)
        self.__max_k = environment.get_n_time_slots() + 1
        self.__max_m = environment.get_n_time_slots() + 1
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
            if agent.get_strategy() == "popular_prediction":
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
            if agent.get_strategy() == "popular_prediction":
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
                    print("k: ", k, "m: ", m)
                    self.__set_km_popular_agents(k, m)
                    self._go_through_rounds()

                self._append_scores_per_run()
                self.__append_list_popular_agent_utility()
                self.__append_list_km(k, m)
                self._reset_scores()

        self._environment.rank_popularity_time_slots()
        self.__print_results()
        mean_utility_popular_agents = self._create_list_mean_utility(self.__popular_agent_utility,
                                                                     1,  # self._n_popular_agents,
                                                                     self.__n_runs)
        print(mean_utility_popular_agents)
        # plots.plot_3d_graph_cutoff(self.__list_m, self.__list_k, mean_utility_popular_agents, self.__max_m - 1,
        #                           self.__max_k - 1, 'slots taken into consideration per agent',
        #                           'votes per agent',  'mean utility', 'mean utility with popular strategy')
        plots.plot_heatmap(self.__list_m, self.__list_k, mean_utility_popular_agents,
                           'slots taken into consideration per agent', 'votes per agent',
                           'mean utility', 'mean utility with popular strategy')


class Agent_slot(Games):
    def __init__(self, agents, environment, max_agents, max_slots, percentage_strategic_agents, bonus_type):
        Games.__init__(self, agents, environment)
        self.__percentage_strategic_agents = percentage_strategic_agents
        self.__n_sincere_voters = 0
        self.__n_strategic_voters = 0
        # Set to 4 since if you have 25% strategic voters, the first game you can play with this is with 1
        # strategic voter and 3 sincere voters. If for each condition they are set to four the graphs can be more
        # easily compared
        self.__starting_n_agents = 4
        # Set to 4 since the popular strategy works best when it considers 4 slots and then votes on 1
        self.__starting_n_slots = 4
        self.__max_agents = max_agents
        self.__max_slots = max_slots
        self.__popular_agent_utility = []
        self.__list_slots = []
        self.__list_agents = []
        self.__n_runs = 0
        self.__bonus_type = bonus_type

        # self.__calculate_n_agent_per_type()
        self.__play_game()

    # The program loops through max_agents and max_slots both starting at 1, each loop is one run. This functions
    # calculates in how many runs this results and stores it in __n_runs
    def __calculate_number_of_runs(self):
        self.__n_runs = (self.__max_agents - self.__starting_n_agents + 1) * (
                    self.__max_slots - self.__starting_n_slots + 1)

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
        # TODO: just calculate how many sincere and strategic voters should be created instead of using this convoluted
        # way
        self.__calculate_n_agent_per_type(n_agents)
        self._agents.clear()
        for i in range(self.__n_sincere_voters):
            agent = strategies.Standard(self._environment, n_agents, i, self.__bonus_type)
            self._agents.append(agent)
        for i in range(self.__n_strategic_voters):
            agent = strategies.Popular_prediction(self._environment, n_agents, i + self.__n_sincere_voters,
                                                  self.__bonus_type)
            self._agents.append(agent)

        # print("n_agents:", n_agents)
        # for agent in self._agents:
        #    print("strategy: ", agent.get_strategy())

        # print("")
        if n_agents != len(self._agents):
            print("ERROR: not enough agents were created in the agent_slot_game")

    # TODO: change this to a name that better describes the function or split it in two
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
        # Loop over the the agents
        for n_agents in range(self.__starting_n_agents, self.__max_agents + 1):
            # Set the number of agents, if the percentage of strategic voter is 0 a special function has to be used
            if self.__percentage_strategic_agents == 0:
                self.__set_number_of_agents(n_agents)
            else:
                self.__set_number_of_agents_different_types(n_agents)
            # Loop over the slots
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
                            'number of agents', 'number of time slots', 'mean social welfare',
                            'Mean utility based on the number of agents and time slots')


# Play a game with x sincere agent plus 1 of the four strategies for each strategy for each number of time slots and each number of agents
# Next compare the utility obtained by the last agent in each game. Rank the strategies in accordance of who scored the highest
# Store this ranking in a list and at the end make a histogram out of it.
class Agent_slot_strategy(Games):
    def __init__(self, agents, environment, max_agents, max_slots, bonus_type):
        #max_agents = 10
        Games.__init__(self, agents, environment)
        # Set to 4 since if you have 25% strategic voters, the first game you can play with this is with 1
        # strategic voter and 3 sincere voters. If for each condition they are set to four the graphs can be more
        # easily compared
        self.__starting_n_agents = 4
        # Set to 4 since the popular strategy works best when it considers 4 slots and then votes on 1
        self.__starting_n_slots = 20
        self.__max_agents = max_agents
        self.__max_slots = max_slots
        self.__popular_agent_utility = []
        self.__list_slots = []
        self.__list_agents = []
        self.__n_runs = 0
        self.__bonus_type = bonus_type
        self.__score_agents_using_strategy = []
        self.__ranking = []

        self.__social_welfare_per_strategy = []
        self.__egalitarian_welfare_per_strategy = []
        self.__max_percentage_difference_social = 0
        self.__max_percentage_difference_egalitarian = 0
        self.__agents_max_percentage_difference = 0
        self.__slots_max_percentage_difference = 0
        self.__social_welfare_1 = 0
        self.__social_welfare_2 = 0
        self.__lowest_social_welfare_strategy = 0
        self.__highest_social_welfare_strategy = 0

        # self.__calculate_n_agent_per_type()
        self.__play_game()

    # The program loops through max_agents and max_slots both starting at 1, each loop is one run. This functions
    # calculates in how many runs this results and stores it in __n_runs
    def __calculate_number_of_runs(self):
        self.__n_runs = (self.__max_agents - self.__starting_n_agents + 1) * (
                    self.__max_slots - self.__starting_n_slots + 1)

    def __set_number_of_agents_different_types(self, n_agents, strategy):
        self._n_agents = n_agents
        # Clears all the agents, then it create the number of sincere voters that have to created and next
        # one popular agent is created
        self._agents.clear()
        for i in range(n_agents - 1):
            agent = strategies.Standard(self._environment, n_agents, i, self.__bonus_type)
            self._agents.append(agent)

        if strategy == 0:
            strategic_agent = strategies.Popular_adaptive(self._environment, n_agents, n_agents - 1, self.__bonus_type)
        elif strategy == 2:
            strategic_agent = strategies.Popular(self._environment, n_agents, n_agents - 1, self.__bonus_type)
        elif strategy == 1:
            strategic_agent = strategies.Popular_prediction(self._environment, n_agents, n_agents - 1,
                                                            self.__bonus_type)
        elif strategy == 3:
            strategic_agent = strategies.Standard(self._environment, n_agents, n_agents - 1, self.__bonus_type)
        else:
            print("ERROR, there are only 4 strategies")
            strategic_agent = strategies.Popular_adaptive(self._environment, n_agents, n_agents - 1, self.__bonus_type)

        self._agents.append(strategic_agent)
        # print("n_agents:", n_agents)
        # for agent in self._agents:
        #    print("strategy: ", agent.get_strategy())

        # print("")
        if n_agents != len(self._agents):
            print("ERROR: not enough agents were created in the agent_slot_game")

    # TODO: change this to a name that better describes the function or split it in two
    # Tell the agents how many time slots there are and change for how many slots the agent has a certain preference
    def __inform_agents_n_slots(self, n_slots):
        for agent in self._agents:
            agent.set_n_time_slots(n_slots)
            agent.create_time_slot_preference()

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

    def __print_orders_per_n_slots(self):
        # prints the frequency of each ranking order first for the each number of slot and then for each number of
        # agents
        for n_slots in range(self.__starting_n_slots, self.__max_slots):
            print("Game with ", n_slots, "time slots: ")
            # List that contains every unique combination of orders that has been found in raking_order
            unique_orders = []
            # Create the list of every unique order by looping over the list unique_orders, if the order that
            # currently is being looked at does not exist then add it to the list unique_orders
            for idx, order in enumerate(self.__ranking):
                is_unique = True
                # Check if we have the right slot
                if self.__list_slots[idx] == n_slots:
                    for unique_order in unique_orders:
                        if unique_order == order:
                            is_unique = False

                    if is_unique:
                        unique_orders.append(order)

            # Append the list self.__ranking_frequency with one for each element in unique_orders
            ranking_frequency = [0] * len(unique_orders)

            # Add one for each order in __ranking that matches with a unique order
            for idx_order, order in enumerate(self.__ranking):
                if self.__list_slots[idx_order] == n_slots:
                    for idx_unique_order, unique_order in enumerate(unique_orders):
                        if order == unique_order:
                            ranking_frequency[idx_unique_order] += 1

            # Print the results
            for idx, unique_order in enumerate(unique_orders):
                print(unique_order, ranking_frequency[idx])  # , self.__ranking_frequency[idx])

            # Clear it so that for the next n_slots the list can be used again
            unique_orders.clear()

    def __print_orders_per_n_agents(self):
        # prints the frequency of each ranking order first for the each number of slot and then for each number of
        # agents
        for n_agents in range(self.__starting_n_agents, self.__max_agents):
            print("Game with ", n_agents, "agents: ")
            # List that contains every unique combination of orders that has been found in raking_order
            unique_orders = []
            # Create the list of every unique order by looping over the list unique_orders, if the order that
            # currently is being looked at does not exist then add it to the list unique_orders
            for idx, order in enumerate(self.__ranking):
                is_unique = True
                # Check if we have the right slot
                if self.__list_agents[idx] == n_agents:
                    for unique_order in unique_orders:
                        if unique_order == order:
                            is_unique = False

                    if is_unique:
                        unique_orders.append(order)

            # Append the list self.__ranking_frequency with one for each element in unique_orders
            ranking_frequency = [0] * len(unique_orders)

            # Add one for each order in __ranking that matches with a unique order
            for idx_order, order in enumerate(self.__ranking):
                if self.__list_agents[idx_order] == n_agents:
                    for idx_unique_order, unique_order in enumerate(unique_orders):
                        if order == unique_order:
                            ranking_frequency[idx_unique_order] += 1

            # Print the results
            for idx, unique_order in enumerate(unique_orders):
                print(unique_order, ranking_frequency[idx])  # , self.__ranking_frequency[idx])

            # Clear it so that for the next n_slots the list can be used again
            unique_orders.clear()

    def __calculate_percentage_difference(self, number1, number2):
        delta = abs(number1 - number2)
        mean = (number1 + number2) / 2
        return (delta / mean) * 100

    def __calculate_max_percentage_difference_social_welfare(self, n_agents, n_slots):
        order_social_welfare = [0, 1, 2, 3]
        n_strategies = len(self.__social_welfare_per_strategy)

        quick_sort.quick_sort(self.__social_welfare_per_strategy, order_social_welfare, 0, n_strategies - 1)

        percentage_difference = self.__calculate_percentage_difference(self.__social_welfare_per_strategy[0],
                self.__social_welfare_per_strategy[n_strategies - 1])

        if self.__max_percentage_difference_social < percentage_difference:
            self.__max_percentage_difference_social = percentage_difference
            self.__agents_max_percentage_difference = n_agents
            self.__slots_max_percentage_difference = n_slots
            self.__social_welfare_1 = self.__social_welfare_per_strategy[0] / self._rounds / n_agents
            self.__social_welfare_2 = self.__social_welfare_per_strategy[n_strategies - 1] / self._rounds / n_agents
            self.__lowest_social_welfare_strategy = order_social_welfare[0]
            self.__highest_social_welfare_strategy = order_social_welfare[n_strategies - 1]

    def __calculate_max_percentage_difference_egalitarian_welfare(self, n_agents, n_slots):
        order_egalitarian_welfare = [0, 1, 2, 3]
        n_strategies = len(self.__egalitarian_welfare_per_strategy)

        quick_sort.quick_sort(self.__egalitarian_welfare_per_strategy, order_egalitarian_welfare, 0, n_strategies - 1)

        percentage_difference = self.__calculate_percentage_difference(self.__egalitarian_welfare_per_strategy[0],
                self.__egalitarian_welfare_per_strategy[n_strategies - 1])

        if self.__max_percentage_difference_egalitarian < percentage_difference:
            self.__max_percentage_difference_egalitarian = percentage_difference
            self.__agents_max_percentage_difference = n_agents
            self.__slots_max_percentage_difference = n_slots
            self.__egalitarian_welfare_1 = self.__egalitarian_welfare_per_strategy[0] / self._rounds / n_agents
            self.__egalitarian_welfare_2 = self.__egalitarian_welfare_per_strategy[n_strategies - 1] / self._rounds / n_agents
            self.__lowest_egalitarian_welfare_strategy = order_egalitarian_welfare[0]
            self.__highest_egalitarian_welfare_strategy = order_egalitarian_welfare[n_strategies - 1]

    def __print_max_percentage_difference_social_welfare(self):
        print("SOCIAL WELFARE:")
        print("max percentage difference: ", self.__max_percentage_difference_social, ", n_agents: ",
              self.__agents_max_percentage_difference, ", n_slots: ", self.__slots_max_percentage_difference,
              ",social welfare worst strategy: ", self.__social_welfare_1, ",strategy: ", self.__lowest_social_welfare_strategy,
              ",social welfare best strategy: ", self.__social_welfare_2, ",strategy: ", self.__highest_social_welfare_strategy)

    def __print_max_percentage_difference_egalitarian_welfare(self):
        print("EGALITARIAN WELFARE:")
        print("max percentage difference: ", self.__max_percentage_difference_egalitarian, ", n_agents: ",
              self.__agents_max_percentage_difference, ", n_slots: ", self.__slots_max_percentage_difference,
              ",egalitarian welfare worst strategy: ", self.__egalitarian_welfare_1, ",strategy: ",
              self.__lowest_egalitarian_welfare_strategy,
              ",egalitarian welfare best strategy: ", self.__egalitarian_welfare_2, ",strategy: ",
              self.__highest_egalitarian_welfare_strategy)

    def __play_game(self):
        # Loop over the the agents
        for n_agents in range(self.__starting_n_agents, self.__max_agents + 1):
            # progress
            print(n_agents, "of the ", 20, "agents done")
            # Loop over the slots
            for n_slots in range(self.__starting_n_slots, self.__max_slots + 1):
                # Play a game with each strategy for each number of time slots and each number of agents
                self._environment.change_time_slots(n_slots)
                for strategy in range(2):
                    # Set the number of agents
                    self.__set_number_of_agents_different_types(n_agents, strategy)

                    self._calculate_number_of_agents()
                    self._go_through_rounds()

                    self._append_scores_per_run()

                    # Appends the score of the last agent, that is the agent using the strategy
                    self.__score_agents_using_strategy.append(
                        self._agents[n_agents - 1].get_total_utility() / self._rounds)
                    self.__social_welfare_per_strategy.append(self._social_welfare)
                    self.__egalitarian_welfare_per_strategy.append(self._min_utility)


                    self._reset_scores()
                    self._environment.reset(self._agents)

                # store in which order the strategies were ranked in this particular run in __ranking and add another
                # element to __ranking_frequency and set it to one. Or, if this order is already is stored in __ranking
                # add one to ranking_frequency in the right place. That is the place that the ranking order is stored
                # in __ranking
                ranking_order = [0, 1, 2, 3]
                #order_found = False
                quick_sort.quick_sort(self.__score_agents_using_strategy, ranking_order, 0,
                                      len(self.__score_agents_using_strategy) - 1)
                #standard_order = [3, 2, 1, 0]
                #if ranking_order != standard_order:
                #print("n_agents: ", n_agents, ", n_slots: ", n_slots, ", order: ", ranking_order, self.__score_agents_using_strategy)

                #self.__print_orders(n_agents, n_slots, ranking_order)
                self.__ranking.append(ranking_order)

                self.__calculate_max_percentage_difference_social_welfare(n_agents, n_slots)
                self.__calculate_max_percentage_difference_egalitarian_welfare(n_agents, n_slots)
                print(self.__max_percentage_difference_egalitarian)
                self.__max_percentage_difference_egalitarian = 0
                #for idx, order in enumerate(self.__ranking):
                #    if order == ranking_order:
                #        self.__ranking_frequency[idx] += 1
                #        order_found = True

                #if not order_found:
                #    self.__ranking.append(ranking_order)
                #    self.__ranking_frequency.append(1)

                self.__append_parameters(n_slots, n_agents)
                self.__score_agents_using_strategy.clear()
                self.__social_welfare_per_strategy.clear()
                self.__egalitarian_welfare_per_strategy.clear()

        self.__print_max_percentage_difference_social_welfare()
        self.__print_max_percentage_difference_egalitarian_welfare()

        #self.__print_orders_per_n_slots()
        #self.__print_orders_per_n_agents()

    def __print_orders(self, n_agents, n_slots, ranking_order):
        standard_order = [3, 2, 1, 0]
        if ranking_order != standard_order:
            print("n_agents: ", n_agents, ", n_slots: ", n_slots, ", order: ", ranking_order,
                  self.__score_agents_using_strategy)


# Creates a 2d graph of how the number of slots affect the mean utility of all the sincere voters
class Slots(Games):
    def __init__(self, agents, environment, max_slots, bonus_type):
        Games.__init__(self, agents, environment)
        # Set to 4 since the popular strategy works best when it considers 4 slots and then votes on 1
        self.__starting_n_slots = 2
        self.__max_slots = max_slots
        self.__popular_agent_utility = []
        self.__list_slots = []
        self.__list_agents = []
        self.__n_runs = 0
        self.__bonus_type = bonus_type

        # self.__calculate_n_agent_per_type()
        self.__play_game()

    # The program loops through max_agents and max_slots both starting at 1, each loop is one run. This functions
    # calculates in how many runs this results and stores it in __n_runs
    def __calculate_number_of_runs(self):
        self.__n_runs = self.__max_slots - self.__starting_n_slots + 1

    # TODO: change this to a name that better describes the function or split it in two
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
    def __append_parameters(self, n_slots):
        self.__list_slots.append(n_slots)

    def __create_list_mean_utility_varying_agents_per_run(self):
        mean_utility = []
        for idx in range(len(self._social_welfare_scores)):
            mean_utility.append(self._social_welfare_scores[idx] / self._n_agents / self._rounds)
        return mean_utility

    def __play_game(self):
        # Loop over the the agents
        # Loop over the slots
        for n_slots in range(self.__starting_n_slots, self.__max_slots + 1):
            self._environment.change_time_slots(n_slots)
            self.__inform_agents_n_slots(n_slots)
            self._go_through_rounds()

            self._append_scores_per_run()
            self.__append_parameters(n_slots)
            self._reset_scores()
            self._environment.reset(self._agents)

        self._environment.rank_popularity_time_slots()
        self.__print_results()
        mean_utility = self.__create_list_mean_utility_varying_agents_per_run()
        plots.plot_slots(mean_utility, self._environment.get_n_time_slots())


class Slots_preference(Games):
    def __init__(self, agents, environment, max_slots, bonus_type):
        Games.__init__(self, agents, environment)
        # Set to 4 since the popular strategy works best when it considers 4 slots and then votes on 1
        self.__starting_n_slots = 2
        self.__max_slots = max_slots
        self.__popular_agent_utility = []
        self.__list_slots = []
        self.__list_agents = []
        self.__n_runs = 0
        self.__bonus_type = bonus_type
        self.__preference_per_time_slot = []

        # self.__calculate_n_agent_per_type()
        self.__play_game()

    # The program loops through max_agents and max_slots both starting at 1, each loop is one run. This functions
    # calculates in how many runs this results and stores it in __n_runs
    def __calculate_number_of_runs(self):
        self.__n_runs = self.__max_slots - self.__starting_n_slots + 1

    # TODO: change this to a name that better describes the function or split it in two
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
    def __append_parameters(self, n_slots):
        self.__list_slots.append(n_slots)

    def __create_list_mean_utility_varying_agents_per_run(self):
        mean_utility = []
        for idx in range(len(self._social_welfare_scores)):
            mean_utility.append(self._social_welfare_scores[idx] / self._n_agents / self._rounds)
        return mean_utility

    def __play_game(self):
        # Loop over the the agents
        # Loop over the slots
        for n_slots in range(self.__starting_n_slots, self.__max_slots + 1, 2):
            self._top = n_slots / 2
            self._environment.change_time_slots(n_slots)
            self.__inform_agents_n_slots(n_slots)
            self._go_through_rounds()

            self.__preference_per_time_slot.append(self._preference / (self._n_agents * self._top * self._rounds))
            self._append_scores_per_run()
            self.__append_parameters(n_slots)
            self._reset_scores()
            self._environment.reset(self._agents)

        self._environment.rank_popularity_time_slots()
        self.__print_results()
        # mean_utility = self.__create_list_mean_utility_varying_agents_per_run()
        plots.plot_preference(self.__preference_per_time_slot, self._environment.get_n_time_slots())


class Threshold(Games):
    def __init__(self, agents, environment, bonus_type):
        Games.__init__(self, agents, environment)
        self.__game_type = int(input(
            "What type of game do you want to play?\n1 = social welfare, 2 = price of anarchy\n"))  # 1 = social welfare, 2 = price of anarchy
        self.__bonus_type = bonus_type  # keeps track of the bonus type for when new agents have to be created

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

    def __play_game(self):
        bar = self.__create_progress_bar()

        for threshold in np.arange(0, 1.1, 0.1):
            self.__set_threshold_normal_agents(threshold)
            self._go_through_rounds()
            self._append_scores_per_run()  # this is not divided by rounds yet
            self._reset_scores()
            bar.next()

        self._prepare_for_plotting(11)

        social_welfare_normal = self._social_welfare_scores.copy()
        min_normal = self._min_utility_scores.copy()
        max_normal = self._max_utility_scores.copy()

        if self.__game_type == 2:
            self._create_agents(0, self._n_standard_agents, 0, self.__bonus_type)  # reverse the number of agents
            self.__clear_scores()

            for threshold in np.arange(0, 1.1, 0.1):
                self._go_through_rounds()
                self._append_scores_per_run()
                self._reset_scores()
                bar.next()
            self._prepare_for_plotting(11)

        bar.finish()
        plots.plot_threshold_results(social_welfare_normal, self._social_welfare_scores, min_normal,
                                     self._min_utility_scores, max_normal, self._max_utility_scores, self.__game_type)


class agent_type(Games):
    def __init__(self, agents, environment, bonus_type):
        Games.__init__(self, agents, environment)
        self.__bonus_type = bonus_type  # keeps track of bonus type for when agents need to be created
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


class willingness(Games):
    def __init__(self, agents, environment, bonus_type):
        Games.__init__(self, agents, environment)
        self.__bonus_type = bonus_type  # keeps track of the bonus type for when new agents have to be created
        self.__strategies = set()
        self.__play_game()

    # creates the correct progress bar depending on game type
    def __create_progress_bar(self):
        bar = IncrementalBar('Progress', max=11)
        return bar

    # changes the agents' willingness
    def __set_willingess(self, willingness):
        for agent in self._agents:
            if agent.get_strategy() == "standard" or agent.get_strategy() == "standard_social":
                agent.set_willingness(willingness, 0.1)
            else:
                agent.set_willingness(willingness, 0.2)

    # figure out agent types
    def __agent_types(self):
        for agent in self._agents:
            self.__strategies.add(agent.get_strategy())

    def __play_game(self):
        self.__agent_types()
        bar = self.__create_progress_bar()

        for willingness in np.arange(0, 1.1, 0.1):
            self.__set_willingess(willingness)
            self._go_through_rounds()
            self._append_scores_per_run()
            self._reset_scores()
            bar.next()

        self._prepare_for_plotting(11)

        bar.finish()
        plots.plot_willingness_results(self._social_welfare_scores, self._min_utility_scores, self._max_utility_scores,
                                       self.__strategies)
