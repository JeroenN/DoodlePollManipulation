from environment import Environment
import plots
import strategies
import quick_sort
import games


# Right now this function creates agents with the standard strategy
# storing these agents might not be necessary anymore because it is stored in the environment now 
def create_agents(n_agents, n_mix_pop_adapt, n_pop_agents, n_pop_adapt, n_pop_predic_agents, n_above_average_utility,
                  n_highest_utility, n_median_utility, environment,
                  bonus_type, n_social_agents = 0, n_social_pop_agents = 0, n_social_pop_predic_agents = 0):
    agents = []
    #tot_agents = 10

    #for i in range(8):
    #    agents.append(strategies.Standard(environment, tot_agents, i, bonus_type))
    #agents.append(strategies.Popular(environment, tot_agents, 8, bonus_type))
    #for i in range(1):
    #    agents.append(strategies.Standard(environment, tot_agents, 9, bonus_type))

    tot_agents = n_agents +n_mix_pop_adapt + n_pop_agents + n_pop_adapt + n_pop_predic_agents +\
                 n_above_average_utility + n_highest_utility

    for i in range(n_agents):
        agent = strategies.Standard(environment, tot_agents, i, bonus_type)
        agents.append(agent)
    for i in range(n_pop_agents):
        agents.append(strategies.Popular(environment, tot_agents, i+n_agents, bonus_type))
    for i in range(n_pop_predic_agents):
        agents.append(strategies.Popular_prediction(environment, tot_agents, i + n_agents + n_pop_agents, bonus_type))
    for i in range(n_above_average_utility):
        agent = strategies.Above_average_utility(environment, tot_agents, i + n_agents + n_pop_agents + n_pop_predic_agents, bonus_type)
        agents.append(agent)
    for i in range(n_highest_utility):
        agent = strategies.Highest_utility(environment, tot_agents, i + n_agents + n_pop_agents + n_pop_predic_agents + n_above_average_utility, bonus_type)
        agents.append(agent)
    for i in range(n_median_utility):
        agent = strategies.Median_utility(environment, tot_agents, i + n_agents + n_pop_agents + n_pop_predic_agents + n_above_average_utility + n_highest_utility, bonus_type)
        agents.append(agent)
    for i in range(n_pop_adapt):
        agents.append(strategies.Popular_adaptive(environment, tot_agents, i + n_agents + n_pop_agents + n_pop_predic_agents + n_above_average_utility + n_highest_utility, bonus_type))
    for i in range(n_mix_pop_adapt):
        agents.append(strategies.Mix_popular_adapt(environment, tot_agents, i + n_agents + n_pop_agents + n_pop_predic_agents + n_above_average_utility + n_highest_utility + n_pop_adapt, bonus_type))
    return agents

def create_environment(n_time_slots):
    return Environment(n_time_slots)

def print_game(environment, agents):
    print(environment, '\n')

def let_agents_vote(agents, environment):
    idx = environment.get_index_agent_willingness()
    while idx is not None:
        agent = agents[idx]
        agent.vote()  # Agents vote for their preferred time slots
        idx = environment.get_index_agent_willingness()

def let_agents_calculate_utility(agents):
    for agent in agents:
        agent.calculate_utility()
        agent.change_time_slot_preference()

def calculate_social_welfare(agents):
    social_welfare = 0
    for agent in agents:
        social_welfare += agent.get_utility()
    
    return social_welfare

def calculate_egalitarian_welfare(agents, rounds):
    welfares = []
    welfare_idx = []

    for idx, agent in enumerate(agents):
        welfares.append(agent.get_utility())
        welfare_idx.append(idx)

    quick_sort.quick_sort(welfares, welfare_idx, 0, len(agents)-1)

    return welfares[0], welfares[len(agents)-1]

def print_game_results(environment, agents, rounds, social_welfare, min_utility, max_utility):
    print("Game ended! \n")
    for agent in agents:
        print(agent, ", Strategy: {agent.get_strategy()}, Total utility: {agent.get_total_utility()/rounds}")

    print('\nSocial welfare: ', social_welfare/rounds)
    print('\nMean utility; ', (social_welfare/len(agents))/rounds)

    print("\nMinimum utility ", min_utility/rounds) # agent with smallest utility
    print("\nMaximum utility: ", max_utility/rounds) # agent with largest utility


def print_agent_slot_game_results(agents, rounds, social_welfare_scores, min_utility_scores, max_utility_scores,
                                  agents_per_run, slots_per_run):
    print("Game ended! \n")
    for agent in agents:
        print(agent, ", Strategy: {agent.get_strategy()}, Total utility: {agent.get_total_utility()/rounds}")

    for idx in range(len(social_welfare_scores)):
        print("n_agents: ", agents_per_run[idx])
        print("n_slots: ", slots_per_run[idx])
        print('Social welfare: ', social_welfare_scores[idx]/rounds)
        n_agents = agents_per_run[idx]
        print('Mean utility; ', (social_welfare_scores[idx] / n_agents / rounds))

        print("Minimum utility ", min_utility_scores[idx]/rounds) # agent with smallest utility
        print("Maximum utility: ", max_utility_scores[idx]/rounds) # agent with largest utility

def set_number_of_agents(environment, agents, n_agents, bonus_type):
    agents.clear()  # TODO: make this more efficient, should not be cleared every time
    for i in range(n_agents):
        agent = strategies.Standard(environment, n_agents,i, bonus_type)
        agents.append(agent)

def create_list_mean_utility_varying_agents_per_run(social_welfare_scores, agents_per_run, rounds):
    mean_utility = []
    for idx in range(len(social_welfare_scores)):
        n_agents = agents_per_run[idx]
        mean_utility.append(social_welfare_scores[idx] / n_agents / rounds)
    return mean_utility

def print_max_threshold(threshold_welfares_standard):
    max = 0
    index = 0
    for idx in range(len(threshold_welfares_standard)):
        if max < threshold_welfares_standard[idx]:
            max = threshold_welfares_standard[idx]
            index = idx
    print("max welfare: ", max, "threshold: ", index/len(threshold_welfares_standard))

# Chooses which type of game is going to be played
def play_game(environment, agents, bonus_type):
    game_type = int(input("What type of game do you want to play?\n0 = normal game, 1 = km game, 2 = threshold game,"
                          " 3 = agent slot game, 4 = agent type game, 5 = willingness game, 6 = Distribution, 7 = Slots,"
                          " 8 = Slots preference, 9 = agent slot strategy game\n"))

    print("Playing game...")

    if game_type == 0:
        games.Normal(agents, environment, bonus_type)
    elif game_type == 1:
        games.KM(agents, environment)
    elif game_type == 2:
        games.Threshold(agents, environment, bonus_type)
    elif game_type == 3:
        games.Agent_slot(agents, environment, 20, 20, 0, bonus_type)
    elif game_type == 4: 
        games.agent_type(agents, environment, bonus_type)
    elif game_type == 5:
        games.willingness(agents, environment, bonus_type)
    elif game_type == 6:
        games.Distribution_50(agents, environment, 20)
    elif game_type == 7:
        games.Slots(agents, environment, 20, bonus_type)
    elif game_type == 8:
        games.Slots_preference(agents, environment, 20, bonus_type)
    elif game_type == 9:
        games.Agent_slot_strategy(agents, environment, 20, 20, bonus_type)


def main():
    environment = create_environment(
        10) #int(input("How many dates are in the Doodle poll?: ")))  # create and store environment

    bonus_type = 0 # int(input("Do you want the agents to use social bonus?\n 0 = no, 1 = yes\n"))
    
    if bonus_type == 0:
        agents = create_agents(0, #int(input("How many sincere voters are in the Doodle poll?: ")),
                               0, #int(input("How many mix adaptable popular are in the Doodle poll?: ")),
                            0, #int(input("How many popular voters are in the Doodle poll?: ")),
                            0, #int(input("How many adaptive popular voters are in the Doodle poll?: ")),
                            0, #int(input("How many popular prediction voters are in the Doodle poll?: ")),
                            0, #int(input("How many above average utility voters are in the Doodle poll?: ")),
                            0, #int(input("How many highest utility voters are in the Doodle poll?: ")),
                            0, #int(input("How many median utility voters are in the Doodle poll?: ")),
                            environment,
                            bonus_type)  # create and store agents
        
    elif bonus_type == 1:
        agents = create_agents(int(input("How many standard voters are in the Doodle poll?: ")),
                            int(input("How many popular voters are in the Doodle poll?: ")),
                            int(input("How many popular prediction voters are in the Doodle poll?: ")), 
                            environment,
                            bonus_type,
                            int(input("How many standard social bonus voters are in the Doodle poll?: ")), 
                            int(input("How many popular social bonus voters are in the Doodle poll?: ")), 
                            int(input("How many popular prediction social bonus voters are in the Doodle poll?: ")))

    environment.determine_willingness(agents)
    environment.rank_willingness()

    play_game(environment, agents, bonus_type)

if __name__ == "__main__":
    main()
