#!/bin/python3
import numpy as np
import display
import shapes
import physics
import matplotlib.pyplot as plt

# taille de la grille
Nx, Ny = 200, 100

# types :
## 0 - AIR
## 1 - SOLID
## 2 - SABLE

GRID = np.array([[(0,0) for x in range(Nx)] for y in range(Ny)])


GRID = shapes.rectangle(0, 0, Nx, int(Ny/5), 255, GRID) # sol

GRID = shapes.rectangle(int(Nx/3), int(Ny/2), 20, 20, 1, GRID, material=2)
GRID = shapes.rectangle(int(Nx/2.8), int(Ny/3), 15, 10, 2, GRID, material=1)

GRID = shapes.triangle(int(Nx/1.2), int(Ny/1.7), 20, 10, 3, GRID, material=1)
GRID = shapes.h_circle(int(Nx/1.5), int(Ny/1.5), 10, 3, GRID, material=1)

plt.ion()
display.show_grid(GRID)
plt.pause(0.1)


while not np.array_equal(GRID, physics.step(GRID)):
    for j in range(10):
        GRID = physics.step(GRID)
        print(j)
    GRID = physics.apply_object_cuts(GRID)
    display.show_grid(GRID)
    plt.pause(0.001)
