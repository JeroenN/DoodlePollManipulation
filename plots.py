from mpl_toolkits import mplot3d
import numpy as np
import matplotlib.pyplot as plt

def plot_3d_graph(x, y, z, x_max, y_max, x_label, y_label, z_label, title):
    X = np.reshape(x, (x_max, y_max))
    Y = np.reshape(y, (x_max, y_max))
    Z = np.reshape(z, (x_max, y_max))
    plt.figure()
    ax = plt.axes(projection='3d')
    ax.plot_surface(X, Y, Z, rstride=1, cstride=1,
                    cmap='viridis', edgecolor='none')
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_zlabel(z_label)
    plt.show()


def find_min(list):
    min = 1000000
    for item in list:
        if item < min and not item == 0:
            min = item
    return min

def plot_3d_graph_cutoff(x, y, z, x_max, y_max, x_label, y_label, z_label, title):
    for idx in range(len(z)):
        if z[idx] == 0:
            z[idx] = np.nan

    X = np.reshape(x, (x_max, y_max))
    Y = np.reshape(y, (x_max, y_max))
    Z = np.reshape(z, (x_max, y_max))
    print(Z)
    plt.figure()
    ax = plt.axes(projection='3d')
    ax.plot_surface(X, Y, Z, rstride=1, cstride=1,
                    cmap='viridis', edgecolor='none', vmin=np.nanmin(z), vmax=np.nanmax(z))
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_zlabel(z_label)
    ax.set_title('effect of number of agents and slots on mean utility')
    ax.set_xlabel('number of agents')
    ax.set_ylabel('number of slots')
    ax.set_zlabel('mean utility')
    plt.show()

def plot_threshold_results(threshold_welfares_standard, threshold_welfares_popular, threshold_egalitarian_standard, threshold_egalitarian_popular, game_type):

    if game_type == 1: 
        plt.plot(np.arange(0, 1.1, 0.1), threshold_welfares_standard)
        plt.xlabel('Threshold')
        plt.ylabel('Social welfare')
        plt.title('Influence of threshold on social welfare')
        plt.show()
        plt.savefig('social_welfare_threshold.png')
        plt.clf()
        
        plt.plot(np.arange(0, 1.1, 0.1), threshold_egalitarian_standard)
        plt.xlabel('Threshold')
        plt.ylabel('Egalitarian welfare')
        plt.title('Influence of threshold on egalitarian')
        plt.show()
        plt.savefig('egalitarian_welfare_threshold.png')
    elif game_type == 2: 
        price_of_anarchy_social=[]
        price_of_anarchy_egalitarian=[]

        #TODO: Remove debugging statement 
        print(threshold_welfares_popular[0])

        for i in range(0, 11):
            price_of_anarchy_social.append(threshold_welfares_standard[i]/threshold_welfares_popular[i])
            price_of_anarchy_egalitarian.append(threshold_egalitarian_standard[i]/threshold_egalitarian_popular[i])

        plt.plot(np.arange(0, 1.1, 0.1), price_of_anarchy_social)
        plt.xlabel('Threshold')
        plt.ylabel('Price of Anarchy')
        plt.title('Influence of threshold on price of anarchy in terms of social welfare')
        plt.show()
        plt.savefig('price_of_anarchy_social_threshold.png')
        plt.clf()

        plt.plot(np.arange(0, 1.1, 0.1), price_of_anarchy_egalitarian)
        plt.xlabel('Threshold')
        plt.ylabel('Price of Anarchy')
        plt.title('Influence of threshold on price of anarchy in terms of egalitarian welfare')
        plt.show()
        plt.savefig('price_of_anarchy_egalitarian_threshold.png')

def plot_agent_results(agent_welfares, agent_egalitarian, n_of_agents):
    plt.plot(range(0, n_of_agents+1), agent_welfares)
    plt.xlabel('Number of popular agents')
    plt.ylabel('Mean utility')
    plt.show()
    plt.savefig(f'agents_social_welfare_{n_of_agents}.png')
    plt.clf()

    plt.plot(range(0, n_of_agents+1), agent_egalitarian)
    plt.xlabel(f'Number of popular agents out of {n_of_agents}')
    plt.ylabel('Egalitarian welfare')
    plt.show()
    plt.savefig(f'agents_egalitarian_welfare_{n_of_agents}.png')

