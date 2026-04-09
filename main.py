#!/bin/python3
import numpy as np
import display
import shapes
import physics
import matplotlib.pyplot as plt

# taille de la grille
Nx, Ny = 400, 300

# types :
## 0 - AIR
## 1 - SOLID
## 2 - SABLE

GRID = np.array([[(0,0) for x in range(Nx)] for y in range(Ny)])


GRID = shapes.rectangle(0, 0, Nx, int(Ny/5), 255, GRID) # sol
GRID = shapes.rectangle(100, int(Ny/2), 50, 50, 1, GRID, material=2)
GRID = shapes.rectangle(120, int(Ny/3), 30, 20, 2, GRID, material=1)

GRID = shapes.rectangle(300, int(Ny/5), 50, 50, 3, GRID, material=1)
GRID = shapes.rectangle(300, int(Ny/5)+50, 50, 50, 3, GRID, material=2)
GRID = shapes.rectangle(280, int(Ny/5)+100, 50, 50, 3, GRID, material=1)

plt.ion()
display.show_grid(GRID)
plt.pause(0.1)


while not np.array_equal(GRID, physics.step(GRID)):
    for j in range(20):
        GRID = physics.step(GRID)
    GRID = physics.apply_object_cuts(GRID)
    display.show_grid(GRID)
    plt.pause(0.01)
