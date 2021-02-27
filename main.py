from environment import Environment
from agent import Agent
from strategies import Standard

# Right now this function creates agents with the standard strategy
# storing these agents might not be necessary anymore because it is stored in the environment now 
def create_agents(n_agents, environment):
    agents = []
    for i in range(n_agents):
        agents.append(Standard(environment, i))
    return agents


def create_environment(n_time_slots):
    return Environment(n_time_slots)

def let_agents_vote(agents):
    for agent in agents:
        agent.vote()  # Agents vote for their preferred time slots

def let_agents_calculate_utility(agents):
    for agent in agents:
        agent.calculate_utility()
        agent.change_time_slot_preference()

def calculate_social_welfare(environment, agents):
    social_welfare = 0
    for agent in agents:
        social_welfare += agent.get_utility()
    
    return social_welfare

def print_game(environment, agents):
    print(environment, f"and {len(agents)} agents:")
    print('\n'.join(map(str, agents)))
    # get social welfare? + put in graph OR display social welfare over time 

def print_game_results(environment, agents):
    print("Game ended! \n")
    for agent in agents:
        print(agent, f", Utility: {agent.get_utility()}")

    print(f'\nSocial welfare: ', calculate_social_welfare(environment, agents))

def play_game(environment, agents):
    print("\nPlaying game... \n")
    while(environment.increase_time()):
        let_agents_vote(agents)
        environment.determine_most_popular_time_slot()
        let_agents_calculate_utility(agents)

    print_game_results(environment, agents)

def main():
    environment = create_environment(
        int(input("How many dates are in the Doodle poll?: ")))  # create and store environment
    agents = create_agents(int(input("How many voters are in the Doodle poll?: ")),
                           environment)  # create and store agents
    print_game(environment, agents)
    play_game(environment, agents)


if __name__ == "__main__":
    main()
