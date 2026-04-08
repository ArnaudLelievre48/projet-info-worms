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

GRID = np.array([[0 for x in range(Nx)] for y in range(Ny)])


GRID = shapes.rectangle(0, 0, Nx, int(Ny/5), GRID) # sol
GRID = shapes.rectangle(100, int(Ny/2), 50, 50, GRID, material=2)
GRID = shapes.rectangle(120, int(Ny/3), 30, 20, GRID, material=1)

plt.ion()

display.show_grid(GRID)
plt.pause(0.1)


while not np.array_equal(GRID, physics.step(GRID)):
    for j in range(10):
        GRID = physics.step(GRID)
    display.show_grid(GRID)
    plt.pause(0.1)
