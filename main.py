from environment import Environment
import plots
import strategies
import quick_sort
import games
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

def print_game_results_multiple_runs(agents, rounds, social_welfare_scores, min_utility_scores, max_utility_scores,
                                     popular_agent_utility, list_k, list_m):
    print("Game ended! \n")
    for agent in agents:
        print(agent, f", Strategy: {agent.get_strategy()}, Total utility: {agent.get_total_utility()/rounds}")

    for idx in range(len(social_welfare_scores)):
        print(f"n_votes: ", list_k[idx])
        print(f"n_considerations: ", list_m[idx])
        print(f'Social welfare: ', social_welfare_scores[idx]/rounds)
        print(f'Mean utility; ', (social_welfare_scores[idx]/len(agents))/rounds)

        print(f"Minimum utility ", min_utility_scores[idx]/rounds) # agent with smallest utility
        print(f"Maximum utility: ", max_utility_scores[idx]/rounds) # agent with largest utility

        print(f"popular agent utility: ", popular_agent_utility[idx]/rounds, "\n")

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

def set_number_of_agents(environment, agents, n_agents):
    agents.clear()  # TODO: make this more efficient, should not be cleared every time
    for i in range(n_agents):
        agent = strategies.Standard(environment, i)
        agents.append(agent)

def create_list_mean_utility_varying_agents_per_run(social_welfare_scores, agents_per_run, rounds):
    mean_utility = []
    for idx in range(len(social_welfare_scores)):
        n_agents = agents_per_run[idx]
        mean_utility.append(social_welfare_scores[idx] / n_agents / rounds)
    return mean_utility

def create_list_mean_utility(social_welfare_scores, n_agents, rounds):
    mean_utility = []
    for idx in range(len(social_welfare_scores)):
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
                social_welfare += calculate_social_welfare(environment, agents, rounds)
                min, max = calculate_egalitarian_welfare(agents, rounds)
                min_utility += min
                max_utility += max
                environment.reset_enviroment(agents)

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

# If this is chosen the program will run of multiple rounds, each round either k (the number of slots the popular agent takes in consideration) or m (the number of votes the popular agents casts) is changed
def play_km_game(environment, agents, rounds, n_popular_agents=1):
    social_welfare = 0
    min_utility = 0
    max_utility = 0
    max_k = 10
    max_m = 10

    social_welfare_scores = []
    min_utility_scores = []
    max_utility_scores = []
    popular_agent_utility = []
    list_k = []
    list_m = []

    for k in range(1, max_k):
        for m in range(1, max_m):
            if not k > m:
                set_km_popular_agents(agents, k, m)
                for _ in range(rounds):
                    let_agents_vote(agents, environment)
                    environment.determine_most_popular_time_slot()
                    let_agents_calculate_utility(agents)
                    social_welfare += calculate_social_welfare(environment, agents, rounds)
                    min, max = calculate_egalitarian_welfare(agents, rounds)
                    min_utility += min
                    max_utility += max
                    environment.reset_enviroment(agents)

            for agent in agents:
                if agent.get_strategy() == "popular":
                    popular_agent_utility.append(agent.get_total_utility())
                    agent.reset_total_utility()

            list_k.append(k)
            list_m.append(m)
            social_welfare_scores.append(social_welfare)
            min_utility_scores.append(min_utility)
            max_utility_scores.append(max_utility)
            social_welfare = 0
            min_utility = 0
            max_utility = 0

    environment.rank_popularity_time_slots()
    print_game_results_multiple_runs(agents, rounds, social_welfare_scores, min_utility_scores, max_utility_scores,
                                     popular_agent_utility, list_k, list_m)
    mean_utility = create_list_mean_utility(popular_agent_utility, n_popular_agents, rounds)
    plots.plot_3d_graph_cutoff(list_k, list_m, mean_utility, max_k-1, max_m-1, 'votes per agent',
                        'slots taken into consideration per agent', 'mean utility', 'mean utility with popular strategy')

def set_threshold_normal_agents(agents, threshold):
    for agent in agents:
        if agent.get_strategy() == "standard":
            agent.set_threshold(threshold)

def print_threshold_results(threshold_welfares_standard, threshold_welfares_popular, game_type):

    if game_type == 1:
        plt.plot(np.arange(0, 1.01, 0.01), threshold_welfares_standard)
        plt.xlabel('Threshold')
        plt.ylabel('Social welfare')
        plt.title('Influence of threshold on social welfare')
        plt.show()
        plt.savefig('social_welfare_threshold.png')
    elif game_type == 2:
        price_of_anarchy=[]

        for i in range(0, 11):
            price_of_anarchy.append(threshold_welfares_standard[i]/threshold_welfares_popular[i])

        plt.plot(np.arange(0, 1.1, 0.01), price_of_anarchy)
        plt.xlabel('Threshold')
        plt.ylabel('Price of Anarchy')
        plt.title('Influence of threshold on price of anarchy')
        plt.show()
        plt.savefig('price_of_anarchy_threshold.png')

def print_max_threshold(threshold_welfares_standard):
    max = 0
    index = 0
    for idx in range(len(threshold_welfares_standard)):
        if max < threshold_welfares_standard[idx]:
            max = threshold_welfares_standard[idx]
            index = idx
    print(f"max welfare: ", max, "threshold: ", index/len(threshold_welfares_standard))


def play_threshold_game(environment, agents, rounds):
    social_welfare = 0
    egalitarian_welfare = 0
    threshold_welfares_standard = []
    threshold_welfares_popular = []
    threshold_egalitarian_standard = []
    threshold_egalitarian_popular = []
    game_type = 2  # 1 = social welfare,  2 = price of anarchy

    if game_type == 1:
        bar = IncrementalBar('Progress', max=11)
    elif game_type == 2:
        bar = IncrementalBar('Progress', max=22)

    for threshold in np.arange(0, 1.1, 0.1):  # TODO: change to reflect useful
        for _ in range(rounds):
            set_threshold_normal_agents(agents, threshold)
            let_agents_vote(agents, environment)
            environment.determine_most_popular_time_slot()
            let_agents_calculate_utility(agents)
            social_welfare += calculate_social_welfare(agents)
            egalitarian_welfare += calculate_egalitarian_welfare(agents, rounds)[0]
            environment.reset_enviroment(agents)
        threshold_welfares_standard.append(social_welfare / rounds)
        threshold_egalitarian_standard.append(egalitarian_welfare / rounds)
        social_welfare = 0  # reset social welfare between games
        egalitarian_welfare = 0  # reset egalitarian welfare between games
        bar.next()

    if game_type == 2:
        agents = create_agents(0, 10, environment)
        environment.reset_enviroment(agents)
        social_welfare = 0
        for threshold in np.arange(0, 1.1, 0.1):  # TODO: change to reflect useful
            for _ in range(rounds):
                set_threshold_normal_agents(agents, threshold)
                let_agents_vote(agents, environment)
                environment.determine_most_popular_time_slot()
                let_agents_calculate_utility(agents)
                social_welfare += calculate_social_welfare(agents)
                egalitarian_welfare += calculate_egalitarian_welfare(agents, rounds)[0]
                environment.reset_enviroment(agents)
            threshold_welfares_popular.append(social_welfare / rounds)
            threshold_egalitarian_popular.append(egalitarian_welfare / rounds)
            social_welfare = 0  # reset social welfare between games
            egalitarian_welfare = 0  # reset egalitarian welfare between games
            bar.next()

    bar.finish()
    plots.plot_threshold_results(threshold_welfares_standard, threshold_welfares_popular,
                                 threshold_egalitarian_standard, threshold_egalitarian_popular, game_type)


def play_type_of_agent_game(environment, rounds):
    n_of_agents = 100
    social_welfare = 0
    egalitarian_welfare = 0
    agent_welfares = []
    agent_egalitarian = []

    bar = IncrementalBar('Progress', max=n_of_agents + 1)

    for i in range(0, n_of_agents + 1):
        agents = create_agents(n_of_agents - i, i, environment)  # create agents
        environment.reset_enviroment(agents)
        for _ in range(rounds):
            let_agents_vote(agents, environment)
            environment.determine_most_popular_time_slot()
            let_agents_calculate_utility(agents)
            social_welfare += calculate_social_welfare(agents)
            egalitarian_welfare += calculate_egalitarian_welfare(agents, rounds)[0]
            environment.reset_enviroment(agents)
        agent_welfares.append((social_welfare / rounds) / n_of_agents)
        agent_egalitarian.append(egalitarian_welfare / rounds)
        social_welfare = 0  # reset social welfare between games
        egalitarian_welfare = 0  # reset egalitarian welfare between games
        bar.next()
    bar.finish()
    plots.plot_agent_results(agent_welfares, agent_egalitarian, n_of_agents)
    
# Chooses which type of game is going to be played
def play_game(environment, agents):
    game_type = 2  # 0 = normal game, 1 = km game, 2 = threshold game
    rounds = 50000

    print("Playing game...")

    if game_type == 0:
        play_normal_game(environment, agents, rounds)
    elif game_type == 1:
        games.km(agents, environment, 4, 4)
        #play_km_game(environment, agents, rounds)
    elif game_type == 2:
        play_threshold_game(environment, agents, rounds)
    elif game_type == 3:
        play_agent_slot_game(environment, agents, rounds)
    elif game_type == 4: 
        play_type_of_agent_game(environment, rounds)

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
