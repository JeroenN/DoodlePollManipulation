from environment import Environment
from agent import Agent 

# TODO:
# create something that counts the utility at the end of the round
# make a standard strategy, this strategy should have a threshold and a way to determine when it should vote

def create_agents(n_agents, environment):
    agents = []
    for i in range(n_agents):
        agents.append(Agent(environment, i))
    return agents

def create_enviroment(n_time_slots):
    return Environment(n_time_slots)

def print_game(environment, agents):
    print(environment, '\n')
    print('\n'.join(map(str, agents)))

def main():
    environment = create_enviroment(int(input("How many dates are in the Doodle poll?: "))) # create and store environment
    agents = create_agents(int(input("How many voters are in the Doodle poll?: ")), environment) # create and store agents
    print_game(environment, agents)

if __name__ == "__main__":
    main()