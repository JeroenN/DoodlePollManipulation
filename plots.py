from mpl_toolkits import mplot3d
import numpy as np
import matplotlib.pyplot as plt

def plot_agents_slots_mean_utility(agents_per_run, slots_per_run, mean_utility, max_agents, max_slots):
    X = np.reshape(agents_per_run, (max_agents, max_slots))
    Y = np.reshape(slots_per_run, (max_agents, max_slots))
    Z = np.reshape(mean_utility, (max_agents, max_slots))
    plt.figure()
    ax = plt.axes(projection='3d')
    ax.plot_surface(X, Y, Z, rstride=1, cstride=1,
                    cmap='viridis', edgecolor='none')
    ax.set_title('effect of number of agents and slots on mean utility')
    ax.set_xlabel('number of agents')
    ax.set_ylabel('number of slots')
    ax.set_zlabel('mean utility')
    plt.show()