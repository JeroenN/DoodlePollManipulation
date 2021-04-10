from environment import Environment
import plots
import strategies
import quick_sort
import games
from progress.bar import IncrementalBar


# Right now this function creates agents with the standard strategy
# storing these agents might not be necessary anymore because it is stored in the environment now 
def create_agents(n_agents, n_pop_agents, n_pop_predic_agents, environment):
    agents = []
    tot_agents = n_agents + n_pop_agents + n_pop_predic_agents
    for i in range(n_agents):
        agent = strategies.Standard(environment, tot_agents, i)
        agents.append(agent)
    for i in range(n_pop_agents):
        agents.append(strategies.Popular(environment, tot_agents, i+n_agents))
    for i in range(n_pop_predic_agents):
        agents.append(strategies.Popular_prediction(environment, tot_agents, i + n_agents + n_pop_agents))
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
        print(agent, f", Strategy: {agent.get_strategy()}, Total utility: {agent.get_total_utility()/rounds}")

    print(f'\nSocial welfare: ', social_welfare/rounds)
    print(f'\nMean utility; ', (social_welfare/len(agents))/rounds)

    print(f"\nMinimum utility ", min_utility/rounds) # agent with smallest utility
    print(f"\nMaximum utility: ", max_utility/rounds) # agent with largest utility


def print_agent_slot_game_results(agents, rounds, social_welfare_scores, min_utility_scores, max_utility_scores,
                                  agents_per_run, slots_per_run):
    print("Game ended! \n")
    for agent in agents:
        print(agent, f", Strategy: {agent.get_strategy()}, Total utility: {agent.get_total_utility()/rounds}")

    for idx in range(len(social_welfare_scores)):
        print(f"n_agents: ", agents_per_run[idx])
        print(f"n_slots: ", slots_per_run[idx])
        print(f'Social welfare: ', social_welfare_scores[idx]/rounds)
        n_agents = agents_per_run[idx]
        print(f'Mean utility; ', (social_welfare_scores[idx] / n_agents / rounds))

        print(f"Minimum utility ", min_utility_scores[idx]/rounds) # agent with smallest utility
        print(f"Maximum utility: ", max_utility_scores[idx]/rounds) # agent with largest utility


# If this is chosen the program is only run once, thus no parameters are changed
def play_normal_game(environment, agents, rounds):
    social_welfare=0
    min_utility=0
    max_utility=0

    for _ in range(rounds):
        let_agents_vote(agents, environment)
        environment.determine_most_popular_time_slot()
        let_agents_calculate_utility(agents)
        social_welfare += calculate_social_welfare(agents)
        min, max = calculate_egalitarian_welfare(agents, rounds)
        min_utility += min
        max_utility += max
        environment.reset_environment(agents)

    environment.rank_popularity_time_slots()
    print_game_results(environment, agents, rounds, social_welfare, min_utility, max_utility)

def set_number_of_agents(environment, agents, n_agents):
    agents.clear()  # TODO: make this more efficient, should not be cleared every time
    for i in range(n_agents):
        agent = strategies.Standard(environment, i, n_agents)
        agents.append(agent)

def create_list_mean_utility_varying_agents_per_run(social_welfare_scores, agents_per_run, rounds):
    mean_utility = []
    for idx in range(len(social_welfare_scores)):
        n_agents = agents_per_run[idx]
        mean_utility.append(social_welfare_scores[idx] / n_agents / rounds)
    return mean_utility

def play_agent_slot_game(environment, agents, rounds):
    social_welfare = 0
    min_utility = 0
    max_utility = 0

    max_agents = 30
    max_slots = 30

    social_welfare_scores = []
    min_utility_scores = []
    max_utility_scores = []
    slots_per_run = []
    agents_per_run = []

    for n_agents in range(1, max_agents + 1):
        for n_slots in range(1, max_slots + 1):
            set_number_of_agents(environment, agents, n_agents)
            environment.change_time_slots(n_slots)
            for _ in range(rounds):
                let_agents_vote(agents, environment)
                environment.determine_most_popular_time_slot()
                let_agents_calculate_utility(agents)
                social_welfare += calculate_social_welfare(agents)
                min, max = calculate_egalitarian_welfare(agents, rounds)
                min_utility += min
                max_utility += max
                environment.reset_environment(agents)

            slots_per_run.append(n_slots)
            agents_per_run.append(n_agents)
            social_welfare_scores.append(social_welfare)
            min_utility_scores.append(min_utility)
            max_utility_scores.append(max_utility)
            social_welfare = 0
            min_utility = 0
            max_utility = 0

    environment.rank_popularity_time_slots()
    print_agent_slot_game_results(agents, rounds, social_welfare_scores, min_utility_scores, max_utility_scores, agents_per_run, slots_per_run)
    mean_utility = create_list_mean_utility_varying_agents_per_run(social_welfare_scores, agents_per_run, rounds)
    plots.plot_3d_graph(agents_per_run, slots_per_run, mean_utility, max_agents, max_slots, 'agents', 'slots',
                        'mean_utility', 'mean utility based on agents and time slots')

def print_max_threshold(threshold_welfares_standard):
    max = 0
    index = 0
    for idx in range(len(threshold_welfares_standard)):
        if max < threshold_welfares_standard[idx]:
            max = threshold_welfares_standard[idx]
            index = idx
    print(f"max welfare: ", max, "threshold: ", index/len(threshold_welfares_standard))

# Chooses which type of game is going to be played
def play_game(environment, agents):
    game_type = int(input("What type of game do you want to play?\n0 = normal game, 1 = km game, 2 = threshold game, 3 = agent slot game, 4 = agent type game \n"))  # 0 = normal game, 1 = km game, 2 = threshold game, 3 = agent slot game, 4 = type of agent game 
    rounds = 100

    print("Playing game...")

    if game_type == 0:
        games.Normal(agents, environment)
    elif game_type == 1:
        games.KM(agents, environment, 10, 10)
    elif game_type == 2:
        games.threshold(agents, environment)
    elif game_type == 3:
        play_agent_slot_game(environment, agents, rounds)
    elif game_type == 4: 
        games.agent_type(agents, environment)

def main():
    environment = create_environment(
        int(input("How many dates are in the Doodle poll?: ")))  # create and store environment
    agents = create_agents(int(input("How many standard voters are in the Doodle poll?: ")),
                           int(input("How many popular voters are in the Doodle poll?: ")),
                           int(input("How many popular prediction voters are in the Doodle poll?: ")),
                           environment)  # create and store agents
    environment.determine_willingness(agents)
    environment.rank_willingness()
    #arr = [85, 82, 88, 86, 85, 93, 98, 40, 73, 83]
    #mean = normal_distribution.calculate_mean(arr)
    #print(f"mean: ", mean)
    #print(normal_distribution.calculate_standard_deviation(arr, mean))

    play_game(environment, agents)

if __name__ == "__main__":
    main()
