import quick_sort
import plots

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
        self._mean_utility = []

        self._calculate_number_of_agents() # Determine how many agents there are of each type

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
            if agent.get_strategy == 'standard':
                self._n_standard_agents += 1
            if agent.get_strategy == 'popular':
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

    # calculates the mean utility and then adds it to list mean_utility
    def _create_list_mean_utility(self, n_runs):
        print(f"agents: ", len(self._agents))
        print(f"rounds: ", self._rounds)
        for idx in range(n_runs):
            print(f"welfare: ", self._social_welfare_scores[idx])
            self._mean_utility.append(self._social_welfare_scores[idx] / self._n_agents / self._rounds)





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
        print(f"n_runs: ", self.__n_runs)
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
    # displaying the results either in the form of text or a nice graph or both
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
        self._create_list_mean_utility(self.__n_runs)
        plots.plot_3d_graph_cutoff(self.__list_k, self.__list_m, self._mean_utility, self.__max_k-1, self.__max_m-1,
                                   'votes per agent', 'slots taken into consideration per agent', 'mean utility',
                                   'mean utility with popular strategy')