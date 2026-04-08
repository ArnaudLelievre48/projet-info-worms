# display with matplotlib

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

cmap = ListedColormap(['gray', 'red', 'orange'])

def show_grid(grid):
    plt.clf()
    plt.imshow(grid, cmap=cmap, vmin=0, vmax=2, origin='lower')
    plt.colorbar(ticks=[0, 1, 2])
    plt.show()
