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
    plt.show()