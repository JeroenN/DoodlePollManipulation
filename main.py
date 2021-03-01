from environment import Environment
import strategies


# TODO:

# Right now this function creates agents with the standard strategy
def create_agents(n_agents, environment):
    agents = []
    for i in range(n_agents):
        agents.append(strategies.Standard(environment, i))
    agents.append(strategies.Popular(environment, 6))

    return agents


def create_environment(n_time_slots):
    return Environment(n_time_slots)


def print_game(environment, agents):
    print(environment, '\n')
    #print('\n'.join(map(str, agents)))
    # agents[0].print_voted_time_slots()
    # agents[0].print_time_slot_preference()

def let_agents_vote(agents):
    for agent in agents:
        agent.vote()  # Agents vote for their preferred time slots

def let_agents_calculate_utility(agents):
    for agent in agents:
        agent.calculate_utility()
        agent.change_time_slot_preference()

def play_game(environment, agents):
    rounds = 10

    for i in range(rounds):
        let_agents_vote(agents)
        environment.determine_most_popular_time_slot()
        let_agents_calculate_utility(agents)
        environment.reset_time_slots()
    for agent in agents:
        print(f"agent utility {agent.get_utility()}")

    print(environment.get_time_slots())
    environment.rank_popularity_time_slots()
    print(environment.get_time_slots())
    print(environment.initial_idx_time_slots)

def main():
    environment = create_environment(
        int(input("How many dates are in the Doodle poll?: ")))  # create and store environment
    agents = create_agents(int(input("How many voters are in the Doodle poll?: ")),
                           environment)  # create and store agents
    print_game(environment, agents)
    play_game(environment, agents)


if __name__ == "__main__":
    main()
