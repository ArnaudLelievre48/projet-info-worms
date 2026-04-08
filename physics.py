# implémente la physique

import numpy as np
import random

def step(grid):
    h, w = grid.shape
    new = grid.copy()

    # iterate from bottom → top (important!)
    for y in range(1, h):
        for x in range(w):
            if grid[y, x] == 2:  # sand

                # try down
                if grid[y - 1, x] == 0:
                    new[y, x] = 0
                    new[y - 1, x] = 2

                else:
                    # randomize left/right to avoid bias
                    directions = [-1, 1]
                    random.shuffle(directions)

                    moved = False
                    for dx in directions:
                        nx = x + dx
                        if 0 <= nx < w:
                            if grid[y - 1, nx] == 0:
                                new[y, x] = 0
                                new[y - 1, nx] = 2
                                moved = True
                                break

                    if not moved:
                        # stays in place
                        pass

    return new
