#!/bin/python3
#import matplotlib.pyplot as plt
import numpy as np
import pygame

import display as dp
import physics
import shapes
import assets

#backend = "MATPLOTLIB"
backend = "PYGAME"

shop_buttons = {
    "weapon": {
        "rect": pygame.Rect(10, 10, 200, 40),
        "price": 100
    },

    "worm": {
        "rect": pygame.Rect(220, 10, 200, 40),
        "price": 200
    }
}

# taille de la grille
Nx, Ny = 200, 100
cell_size = 16

# types :
## 0 - AIR
## 1 - SOLID
## 2 - SABLE

GRID = np.array([[(0, 0, 0) for x in range(Nx)] for y in range(Ny)])


GRID = shapes.rectangle(0, 0, Nx, int(Ny / 5), GRID, object_id=-1, material=1, texture=1)  # sol

GRID = shapes.rectangle(int(Nx / 2.8), int(Ny / 5), 15, 10, GRID, object_id=1, material=1, texture=1)

GRID = shapes.triangle(int(Nx / 1.2), int(Ny / 1.7), 20, 10, GRID, object_id=2, material=1, texture=1)

GRID = shapes.h_circle(int(Nx / 1.5), int(Ny / 1.5), 10, GRID,object_id=2, material=1, texture=1)

GRID = shapes.rectangle(int(Nx / 1.5)-5, int(Ny / 5), 10, int(Ny / 1.5) - int(Ny/5), GRID, object_id=2, material=1, texture=1)

#dp.show_grid(GRID)
#plt.pause(0.1)


player1 = assets.Player()
weapon1 = player1.Weapons()
weapon2 = player1.Weapons()
weapon3 = player1.Weapons()
player1.weapons.append(weapon1)
player1.weapons.append(weapon2)
player1.weapons.append(weapon3)
player2 = assets.Player()


#if backend == "MATPLOTLIB":
#    plt.ion()
#    while not np.array_equal(GRID, physics.step(GRID)):
#        for j in range(10):
#            GRID = physics.step(GRID)
#            print(j)
#            GRID = physics.apply_object_cuts(GRID)
#            dp.show_grid_matplotlib(GRID)
#            plt.pause(0.001)

if backend == "PYGAME":
    # init pygame and its screen
    pygame.init()
    font = pygame.font.SysFont(None, 30)
    info = pygame.display.Info()
    screen_width  = info.current_w
    screen_height = info.current_h
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()


    running = True
    clock.tick(2000)

    screen.fill((0, 0, 0))
    dp.show_grid_pygame(screen, GRID, player1.wormz, player2.wormz)

    # main game loop
    while running:

        # gestion des inputs
        event = pygame.event.poll()

        # quitter le jeu
        if event.type == pygame.QUIT:
            running = False

        # ajout de worm
        if (event.type == pygame.MOUSEBUTTONDOWN) and (event.button == 1):
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid_x = int(mouse_x // cell_size)
            grid_y = int(Ny - 1 - (mouse_y // cell_size))
            new_worm = player1.Worm(grid_x, grid_y, worm_id=len(player1.wormz))
            player1.wormz.append(new_worm)
            screen.fill((0, 0, 0))
            dp.show_grid_pygame(screen, GRID, player1.wormz, player2.wormz)

        if (event.type == pygame.MOUSEBUTTONDOWN) and (event.button == 3):
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid_x = int(mouse_x // cell_size)
            grid_y = int(Ny - 1 - (mouse_y // cell_size))
            if player1.weapons != []:
                weapon = player1.weapons.pop()
                print(player1.weapons)
                trajectory = weapon.launch_trajectory(grid_x, grid_y, 0, 50)

                i = 0
                exploded = False
                while (i < len(trajectory[0])) and (not exploded):
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            exit()

                    if (0 < int(trajectory[0][i]) < Nx) and (0 < int(trajectory[1][i]) < Ny):
                        if GRID[int(trajectory[1][i])][int(trajectory[0][i])][0] in [1,2]:
                            exploded = True
                            print("EXPLOSION")
                            for worm in player1.wormz:
                                if ( (worm.x_pos - int(trajectory[0][i]))**2 + (worm.y_pos - int(trajectory[1][i]))**2 ) < weapon.radius_explosion**2:
                                    worm.take_damage(weapon.damage)
                                    if worm.health <= 0:
                                        player1.kill_worm(worm.worm_id)
                                        print(player1.wormz)
                                elif ( (worm.x_pos - int(trajectory[0][i]))**2 + (worm.y_pos - int(trajectory[1][i]))**2 ) < weapon.radius_break**2:
                                    worm.take_damage(weapon.damage/2)
                                    if worm.health <= 0:
                                        player1.kill_worm(worm.worm_id)
                                        print(player1.wormz)
                                print("health : ", worm.health)
                            GRID = shapes.transform(GRID, int(trajectory[0][i]), int(trajectory[1][i]), weapon.radius_break, 2)
                            GRID = shapes.transform(GRID, int(trajectory[0][i]), int(trajectory[1][i]), weapon.radius_explosion, 0)
                            dp.show_grid_pygame(screen, GRID, player1.wormz, player2.wormz)
                            pygame.display.flip()
                            clock.tick(2000)

                    screen.fill((0, 0, 0))
                    dp.show_grid_pygame(screen, GRID, player1.wormz, player2.wormz)
                    dp.display_weapon(screen, trajectory[0][i], trajectory[1][i])
                    pygame.display.flip()
                    clock.tick(60)
                    i+=1

            else:
                print("NO MORE WEAPONS")
            screen.fill((0, 0, 0))
            dp.show_grid_pygame(screen, GRID, player1.wormz, player2.wormz)




        # step
        GRID, moved = physics.step(GRID, player1.wormz, player2.wormz)
        while moved:
            event = pygame.event.poll()
            if event.type == pygame.QUIT:
                running = False

            GRID, moved = physics.step(GRID, player1.wormz, player2.wormz)
            GRID = physics.apply_object_cuts(GRID)

            screen.fill((0, 0, 0))
            dp.show_grid_pygame(screen, GRID, player1.wormz, player2.wormz)
            pygame.display.flip()
            clock.tick(60)

        #dp.show_grid_pygame(screen, GRID, player1.wormz, player2.wormz)
        dp.draw_shop(screen, player1, shop_buttons, font)
        pygame.display.flip()
        clock.tick(60)


    pygame.quit()
