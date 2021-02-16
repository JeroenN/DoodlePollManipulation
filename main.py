from environment import Environment
from agent import Agent
import agent


# TODO:
# create something that counts the utility at the end of the round

# Right now this function creates agents with the standard strategy
def create_agents(n_agents, environment):
    agents = []
    for i in range(n_agents):
        agents.append(agent.Standard(environment, i))
    return agents


def create_environment(n_time_slots):
    return Environment(n_time_slots)


def print_game(environment, agents):
    print(environment, '\n')
    print('\n'.join(map(str, agents)))
    # agents[0].print_voted_time_slots()
    # agents[0].print_time_slot_preference()

def let_agents_vote(agents):
    for agent in agents:
        agent.vote()  # Agents vote for their preferred time slots

def let_agents_calculate_utility(agents):
    for agent in agents:
        agent.calculate_utility()
        agent.change_time_slot_preference()

def play_game(agents):
    rounds = 10
    for i in range(rounds):
        let_agents_vote(agents)
        let_agents_calculate_utility(agents)
    for agent in agents:
        print(f"agent utility {agent.get_utility()}")


def main():
    environment = create_environment(
        int(input("How many dates are in the Doodle poll?: ")))  # create and store environment
    agents = create_agents(int(input("How many voters are in the Doodle poll?: ")),
                           environment)  # create and store agents
    print_game(environment, agents)
    play_game(agents)


if __name__ == "__main__":
    main()
