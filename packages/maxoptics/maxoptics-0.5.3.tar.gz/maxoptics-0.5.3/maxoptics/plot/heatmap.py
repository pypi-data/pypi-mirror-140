import matplotlib.pyplot as plt
import numpy as np


def heatmap(x, y, Z):
    if len(x) == len(Z[0]):
        x = [x[0] - (x[1] - x[0])] + x
    if len(y) == len(Z):
        y = [y[0] - (y[1] - y[0])] + y
    X, Y = np.meshgrid(x, y)
    fig, ax = plt.subplots()
    pmesh = ax.pcolormesh(X, Y, Z, cmap="jet")
    plt.colorbar(pmesh, ax=ax)
    return fig
