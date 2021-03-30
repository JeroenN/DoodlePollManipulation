import quick_sort
import plots
from progress.bar import IncrementalBar
import numpy as np 
import strategies

class Games:
    def __init__(self, agents, environment):
        self._agents = agents
        self._environment = environment

        self._social_welfare = 0
        self._min_utility = 0
        self._max_utility = 0
        self._rounds = 100
        self._social_welfare_scores = []
        self._min_utility_scores = []
        self._max_utility_scores = []
        self._n_agents = 0
        self._n_standard_agents = 0
        self._n_popular_agents = 0
        self._mean_utility_popular_agents = []

        self._calculate_number_of_agents()  # Determine how many agents there are of each type

    # Go through all the actions that have to be taken each round
    # 1. let the agents vote, 2. let the agents calculate the utility
    # 3. calculate social welfare and egalitarian welfare, 4. reset all the agents
    # their utility to 0 and set all the time slot votes to zero
    def _go_through_rounds(self):
        for _ in range(self._rounds):
            self._agents_vote()
            self._agents_calculate_utility()
            self.__calculate_social_welfare()
            self.__calculate_egalitarian_welfare()
            self._environment.reset_enviroment(self._agents)

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
        for agent in self._agents:
            if agent.get_strategy() == "standard":
                self._n_standard_agents += 1
            if agent.get_strategy() == "popular":
                self._n_popular_agents += 1
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
        self._max_utility += welfares[self._n_agents - 1]

    # calculates the mean utility of the popular agents and then adds it to list mean_utility_popular_agents
    def _create_list_mean_utility(self, utility_agents, n_agents, n_runs):
        mean_utility = []
        for idx in range(n_runs):
            mean_utility.append(utility_agents[idx] / n_agents / self._rounds)

        return mean_utility

    # create new agents and reset the game to work with these new agents 
    def _create_agents(self, n_agents, n_pop_agents):
        self._agents.clear()

        for i in range(n_agents):
            agent = strategies.Standard(self._environment, i)
            self._agents.append(agent)
        for i in range(n_pop_agents):
            self._agents.append(strategies.Popular(self._environment, i+n_agents))
        
        self._n_agents = 0
        self._n_standard_agents = 0
        self._n_popular_agents = 0
        self._calculate_number_of_agents()
        self._environment.reset_enviroment(self._agents)

    def _prepare_for_plotting(self, runs):
        for idx in range(0, runs):
            self._social_welfare_scores[idx] = (self._social_welfare_scores[idx]/self._rounds) / self._n_agents
            self._min_utility_scores[idx] = self._min_utility_scores[idx]/self._rounds 
            self._max_utility_scores[idx] = self._max_utility_scores[idx]/self._rounds

class km(Games):
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
    # and returns n_runs
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

    # Prints all the different results that we have caluclated
    def __print_results(self):
        print("Game ended! \n")
        # prints the strategy used by each agent and the average utility of each agent
        for agent in self._agents:
            print(agent, f", Strategy: {agent.get_strategy()}, Total utility: {agent.get_total_utility()/self._rounds}")

        print("lengte social welfare scores: ", len(self._social_welfare_scores))
        for idx in range(self.__n_runs):
            print(f"n_votes: ", self.__list_k[idx])
            print(f"n_considerations: ", self.__list_m[idx])
            print(f'Social welfare: ', self._social_welfare_scores[idx]/self._rounds)
            print(f'Mean utility; ', self._social_welfare_scores[idx]/self._n_agents/self._rounds)

            print(f'Minimum utility ', self._min_utility_scores[idx]/self._rounds)  # agent with smallest utility
            print(f"Maximum utility: ", self._max_utility_scores[idx]/self._rounds)  # agent with largest utility

            print(f"popular agent utility: ", self.__popular_agent_utility[idx]/self._rounds, "\n")

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
        plots.plot_3d_graph_cutoff(self.__list_k, self.__list_m, mean_utility_popular_agents, self.__max_k-1, self.__max_m-1,
                                   'votes per agent', 'slots taken into consideration per agent', 'mean utility',
                                   'mean utility with popular strategy')

class threshold(Games):
    def __init__(self, agents, environment):
        Games.__init__(self, agents, environment)
        self.__game_type = 2 # 1 = social welfare, 2 = price of anarchy

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
            if agent.get_strategy() == "standard":
                agent.set_threshold(threshold)

    # clear welfare scores
    def __clear_scores(self):
        self._social_welfare_scores.clear()
        self._min_utility_scores.clear()
        self._max_utility_scores.clear()

    def __play_game(self):
        bar = self.__create_progress_bar()

        for threshold in np.arange(0, 1.1, 0.1):  # TODO: change to reflect useful
            self.__set_threshold_normal_agents(threshold)
            self._go_through_rounds()
            self._append_scores_per_run() # this is not divided by rounds yet 
            self._reset_scores()
            bar.next()
        
        self._prepare_for_plotting(11)

        social_welfare_normal = self._social_welfare_scores.copy()
        min_normal = self._min_utility_scores.copy()
        max_normal = self._max_utility_scores.copy()

        if self.__game_type == 2:
            self._create_agents(0, self._n_standard_agents) # reverse the number of agents 
            self.__clear_scores()
            for threshold in np.arange(0, 1.1, 0.1):
                for _ in range(self._rounds):
                    self._go_through_rounds()
                self._append_scores_per_run()
                self._reset_scores()
                bar.next()
            self._prepare_for_plotting(11)

        bar.finish()
        plots.plot_threshold_results(social_welfare_normal, self._social_welfare_scores, min_normal, self._min_utility_scores, max_normal, self._max_utility_scores, self.__game_type)

class agent_type(Games):
    def __init__(self, agents, environment):
        Games.__init__(self, agents, environment)

        self.__play_game()

    def __play_game(self):
        bar = IncrementalBar('Progress', max=self._n_agents + 1)

        for i in range(0, self._n_agents + 1):
            self._create_agents(self._n_agents - i, i)
            self._go_through_rounds()
            self._append_scores_per_run()
            self._reset_scores()          
            bar.next()
        self._prepare_for_plotting(self._n_agents+1)
        bar.finish()

        plots.plot_agent_results(self._social_welfare_scores, self._min_utility_scores, self._max_utility_scores, self._n_agents)
        