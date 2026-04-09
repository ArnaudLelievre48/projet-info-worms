# display with matplotlib

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

cmap = ListedColormap(['gray', 'red', 'orange'])

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

cmap = ListedColormap(['gray', 'red', 'orange'])

def show_grid(grid):
    grid_show = np.array([[cell[0] for cell in row] for row in grid])

    plt.clf()
    plt.imshow(grid_show, cmap=cmap, vmin=0, vmax=2, origin='lower')
    plt.colorbar(ticks=[0, 1, 2])
    plt.show()
