#from mpl_toolkits import mplot3d
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

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
    ax.set_zbound(lower=0.54, upper=0.68)
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
    plt.show()

def plot_heatmap(x, y, z, x_label, y_label, z_label, title):
    for idx in range(len(z)):
        if z[idx] == 0:
            z[idx] = np.nan

    df = pd.DataFrame.from_dict(np.array([x, y, z]).T)
    df.columns = [x_label, y_label, z_label]
    pivotted = df.pivot(y_label, x_label, z_label)
    sns.heatmap(pivotted, annot = True, cbar_kws={'label': z_label})
    plt.title(title)
    plt.show()

def plot_threshold_results(threshold_welfares_standard, threshold_welfares_popular, min_standard, min_popular, max_standard, max_popular, game_type):

    if game_type == 1: 
        plt.plot(np.arange(0, 1.1, 0.1), threshold_welfares_standard, label="Mean utility")
        plt.plot(np.arange(0, 1.1, 0.1), min_standard, label="Minimum utility")
        plt.plot(np.arange(0, 1.1, 0.1), max_standard, label="Maximum utility")
        plt.xlabel('Threshold')
        plt.ylabel('Utility')
        plt.title('Influence of threshold on social and utilitarian welfare')
        plt.legend(loc='upper right', bbox_to_anchor=(1, 0.875))
        plt.show()
        plt.savefig('welfares_threshold.png')

    elif game_type == 2: 
        price_of_anarchy_social=[]
        price_of_anarchy_min=[]
        price_of_anarchy_max=[]

        for i in range(0, 11):
            price_of_anarchy_social.append(threshold_welfares_standard[i]/threshold_welfares_popular[i])
            price_of_anarchy_min.append(min_standard[i]/min_popular[i])
            price_of_anarchy_max.append(max_standard[i]/max_popular[i])

        plt.plot(np.arange(0, 1.1, 0.1), price_of_anarchy_social, label="Mean utility")
        plt.plot(np.arange(0, 1.1, 0.1), price_of_anarchy_min, label="Minimum utility")
        plt.plot(np.arange(0, 1.1, 0.1), price_of_anarchy_max, label="Maximum utility")
        plt.xlabel('Threshold')
        plt.ylabel('Price of Anarchy')
        plt.title('Influence of threshold on Price of Anarchy')
        plt.legend()
        plt.show()
        plt.savefig('price_of_anarchy_welfares_threshold.png')

def plot_agent_results(agent_welfares, agent_min, agent_max, n_of_agents):

    plt.plot(range(0, n_of_agents+1), agent_welfares, label="Mean utility")
    plt.plot(range(0, n_of_agents+1), agent_min, label = "Minimum utility")
    plt.plot(range(0, n_of_agents+1), agent_max, label="Maximum utility")
    plt.xlabel(f'Number of popular agents out of {n_of_agents}')
    plt.ylabel('Utility')
    plt.title("Influence of type-of-agent ratio on social and utilitarian welfare")
    plt.show()
    plt.savefig(f'agents_welfares_{n_of_agents}.png')

def plot_willingness_results(welfares, min_utility, max_utility, strategies):
    plt.plot(np.arange(0, 1.1, 0.1), welfares, label="Mean utility")
    plt.plot(np.arange(0, 1.1, 0.1), min_utility, label="Minimum utility")
    plt.plot(np.arange(0, 1.1, 0.1), max_utility, label="Maximum utility")
    plt.xlabel('Willingness')
    plt.ylabel('Utility')
    plt.title('Influence of willingness on social and utilitarian welfare')
    plt.legend(loc='upper right', bbox_to_anchor=(1, 0.875))
    plt.show()
    plt.savefig(f'welfares_willingness_{list(strategies)}.png')
