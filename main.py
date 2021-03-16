from environment import Environment
import strategies
import quick_sort
import numpy as np
from matplotlib import pyplot as plt
from progress.bar import IncrementalBar

# Right now this function creates agents with the standard strategy
# storing these agents might not be necessary anymore because it is stored in the environment now 
def create_agents(n_agents, n_pop_agents, environment):
    agents = []
    for i in range(n_agents):
        agent = strategies.Standard(environment, i)
        agents.append(agent)
    for i in range(n_pop_agents):
        agents.append(strategies.Popular(environment, i+n_agents))

    return agents

def create_environment(n_time_slots):
    return Environment(n_time_slots)

def print_game(environment, agents):
    print(environment, '\n')
    #print('\n'.join(map(str, agents)))
    # agents[0].print_voted_time_slots()
    # agents[0].print_time_slot_preference()

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

def calculate_social_welfare(environment, agents, rounds):
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

def print_game_results_multiple_runs(agents, rounds, social_welfare_scores, min_utility_scores, max_utility_scores):
    print("Game ended! \n")
    for agent in agents:
        print(agent, f", Strategy: {agent.get_strategy()}, Total utility: {agent.get_total_utility()/rounds}")

    for idx in range(len(social_welfare_scores)):
        print(f'\nSocial welfare: ', social_welfare_scores[idx]/rounds)
        print(f'\nMean utility; ', (social_welfare_scores[idx]/len(agents))/rounds)

        print(f"\nMinimum utility ", min_utility_scores[idx]/rounds) # agent with smallest utility
        print(f"\nMaximum utility: ", max_utility_scores[idx]/rounds) # agent with largest utility

# If this is chosen the program is only run once, thus no parameters are changed
def play_normal_game(environment, agents, rounds):
    social_welfare=0
    min_utility=0
    max_utility=0

    for _ in range(rounds):
        let_agents_vote(agents, environment)
        environment.determine_most_popular_time_slot()
        let_agents_calculate_utility(agents)
        social_welfare += calculate_social_welfare(environment, agents, rounds)
        min, max = calculate_egalitarian_welfare(agents, rounds)
        min_utility += min
        max_utility += max
        environment.reset_enviroment(agents)

    environment.rank_popularity_time_slots()
    print_game_results(environment, agents, rounds, social_welfare, min_utility, max_utility)

def set_km_popular_agents(agents, k, m):
    for agent in agents:
        if agent.get_strategy() == "popular":
            agent.set_k(k)
            agent.set_m(m)

# If this is chosen the program will run of multiple rounds, each round either k (the number of slots the popular agent takes in consideration) or m (the number of votes the popular agents casts) is changed
def play_km_game(environment, agents, rounds):
    social_welfare=0
    min_utility=0
    max_utility=0
    max_k = 5
    max_m = 5

    social_welfare_scores = []
    min_utility_scores = []
    max_utility_scores = []

    for k in range(1, max_k):
        for m in range(1, max_m):
            set_km_popular_agents(agents, k, m)
            for _ in range(rounds):
                set_km_popular_agents(agents)
                let_agents_vote(agents, environment)
                environment.determine_most_popular_time_slot()
                let_agents_calculate_utility(agents)
                social_welfare += calculate_social_welfare(environment, agents, rounds)
                min, max = calculate_egalitarian_welfare(agents, rounds)
                min_utility += min
                max_utility += max
                environment.reset_enviroment(agents)
            social_welfare_scores.append(social_welfare)
            min_utility_scores.append(min_utility)
            max_utility_scores.append(max_utility)
            social_welfare = 0
            min_utility = 0
            max_utility = 0

    environment.rank_popularity_time_slots()
    print_game_results(environment, agents, rounds, social_welfare, min_utility, max_utility)

def set_threshold_normal_agents(agents, threshold):
    for agent in agents:
        if agent.get_strategy() == "standard":
            agent.set_threshold(threshold)

def print_threshold_results(threshold_welfares_standard, threshold_welfares_popular):
    price_of_anarchy=[]

    for i in range(0, 11):
        price_of_anarchy.append(threshold_welfares_popular[i]/threshold_welfares_standard[i])

    plt.plot(np.arange(0, 1.1, 0.1), price_of_anarchy)
    plt.xlabel('Threshold')
    plt.ylabel('Social welfare')
    plt.title('Influence of threshold on social welfare')
    plt.show()
    plt.savefig('test.png')

def play_threshold_game(environment, agents, rounds):
    social_welfare=0
    threshold_welfares_standard=[]
    threshold_welfares_popular=[]

    bar = IncrementalBar('Progress', max = 22)

    for threshold in np.arange(0, 1.1, 0.1): # TODO: change to reflect useful 
        for _ in range(rounds):
            set_threshold_normal_agents(agents, threshold)
            let_agents_vote(agents, environment)
            environment.determine_most_popular_time_slot()
            let_agents_calculate_utility(agents)
            social_welfare += calculate_social_welfare(environment, agents, rounds)
            environment.reset_enviroment(agents)
        threshold_welfares_standard.append(social_welfare/rounds)
        social_welfare = 0 #reset social welfare between games
        bar.next()

    environment = create_environment(10)
    agents = create_agents(0, 10, environment)
    social_welfare=0
    for threshold in np.arange(0, 1.1, 0.1): # TODO: change to reflect useful 
        for _ in range(rounds):
            set_threshold_normal_agents(agents, threshold)
            let_agents_vote(agents, environment)
            environment.determine_most_popular_time_slot()
            let_agents_calculate_utility(agents)
            social_welfare += calculate_social_welfare(environment, agents, rounds)
            environment.reset_enviroment(agents)
        threshold_welfares_popular.append(social_welfare/rounds)
        social_welfare = 0 #reset social welfare between games
        bar.next()
    
    bar.finish()
    print_threshold_results(threshold_welfares_standard, threshold_welfares_popular)


def play_game(environment, agents):
    type_of_game = 2  # 0 = normal game, 1 = km game
    rounds = 1000
    print("Playing game...")

    if type_of_game == 0:
        play_normal_game(environment, agents, rounds)
    elif type_of_game == 1:
        play_km_game(environment, agents, rounds)
    elif type_of_game == 2: 
        play_threshold_game(environment, agents, rounds)

def main():
    environment = create_environment(
        int(input("How many dates are in the Doodle poll?: ")))  # create and store environment
    agents = create_agents(int(input("How many standard voters are in the Doodle poll?: ")), int(input("How many popular voters are in the Doodle poll?: ")),
                           environment)  # create and store agents
    environment.determine_willingness(agents)
    environment.rank_willingness()
    play_game(environment, agents)

if __name__ == "__main__":
    main()
