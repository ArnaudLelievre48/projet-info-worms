#!/bin/python3
import matplotlib.pyplot as plt
import numpy as np
import pygame

import display as dp
import physics
import shapes

#backend = "MATPLOTLIB"
backend = "PYGAME"

# taille de la grille
Nx, Ny = 200, 100

# types :
## 0 - AIR
## 1 - SOLID
## 2 - SABLE

GRID = np.array([[(0, 0, 0) for x in range(Nx)] for y in range(Ny)])


GRID = shapes.rectangle(0, 0, Nx, int(Ny / 5), -1, GRID, material=1, texture=1)  # sol

GRID = shapes.rectangle(int(Nx / 3), int(Ny / 2), 20, 20, 1, GRID, material=2, texture=2)

GRID = shapes.rectangle(int(Nx / 2.8), int(Ny / 3), 15, 10, 2, GRID, material=1, texture=1)

GRID = shapes.triangle(int(Nx / 1.2), int(Ny / 1.7), 20, 10, 3, GRID, material=1, texture=1)

GRID = shapes.h_circle(int(Nx / 1.5), int(Ny / 1.5), 10, 3, GRID, material=1, texture=1)

#dp.show_grid(GRID)
#plt.pause(0.1)


if backend == "MATPLOTLIB":
    plt.ion()
    while not np.array_equal(GRID, physics.step(GRID)):
        for j in range(10):
            GRID = physics.step(GRID)
            print(j)
            GRID = physics.apply_object_cuts(GRID)
            dp.show_grid_matplotlib(GRID)
            plt.pause(0.001)

elif backend == "PYGAME":
    pygame.init()

    info = pygame.display.Info()

    screen_width  = info.current_w
    screen_height = info.current_h

    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()

    running = True
    clock.tick(1000)
    while running:
        screen.fill((0, 0, 0))

        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            running = False

        GRID = physics.step(GRID)
        GRID = physics.apply_object_cuts(GRID)


        dp.show_grid_pygame(screen, GRID)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
