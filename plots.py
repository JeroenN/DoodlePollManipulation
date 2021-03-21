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