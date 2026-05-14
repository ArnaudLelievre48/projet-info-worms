#!/bin/python3
# import matplotlib.pyplot as plt
import numpy as np
import pygame
import matplotlib.image as mpimg

import assets
import display as dp
import physics
import shapes

# backend = "MATPLOTLIB"
backend = "PYGAME"


# taille de la grille
Nx, Ny = 192, 108
cell_size = 10

# types :
## 0 - AIR
## 1 - SOLID
## 2 - SABLE

GRID = np.array([[(0, 0, 0) for x in range(Nx)] for y in range(Ny)])


ground = mpimg.imread("map/ground.png")
dirt_pixel = ground[99,0]
grass_pixel = ground[86,0]
print(dirt_pixel)

for y in range(Ny):
    for x in range(Nx):
        if ground[y,x][3] != 0.:
            if (ground[y,x] == dirt_pixel).all():
                GRID[Ny-y-1][x] = (1, -1, 3)
            if (ground[y,x] == grass_pixel).all():
                GRID[Ny-y-1][x] = (1, -1, 4)


# dp.show_grid(GRID)
# plt.pause(0.1)


player1 = assets.Player()
player2 = assets.Player()

for i in range(3):
    weapon1 = player1.Weapons()
    weapon2 = player2.Weapons()
    player1.weapons.append(weapon1)
    player2.weapons.append(weapon2)


players = [player1, player2]
player_id = 0


# if backend == "MATPLOTLIB":
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
    id_worm_launch = 0
    font = pygame.font.SysFont(None, 30)
    info = pygame.display.Info()
    screen_width = info.current_w
    screen_height = info.current_h
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()

    running = True
    clock.tick(2000)

    screen.fill((0, 0, 0))
    dp.show_grid_pygame(screen, GRID, player1.wormz, player2.wormz)
    dp.draw_shop(screen, player1, player2, font)

    refresh_UI = True

    pygame.display.flip()

    # main game loop

    nb_actions = 0

    while running:

        # gestion des inputs
        event = pygame.event.poll()

        # si la fenetre change de taille
        info = pygame.display.Info()
        if (screen_width != info.current_w) or (screen_height != info.current_h) or ( (event.type == pygame.KEYDOWN) and (event.key == pygame.K_r) ):
            screen_width = info.current_w
            screen_height = info.current_h
            screen = pygame.display.set_mode((screen_width, screen_height))
            pygame.display.flip()
            refresh_UI = True


        # quitter le jeu
        if event.type == pygame.QUIT:
            running = False

        # ajout de worm
        if (event.type == pygame.MOUSEBUTTONDOWN) and (event.button == 1) and (nb_actions < 3):
            if players[player_id].money >= 200:
                players[player_id].money -= 200
                mouse_x, mouse_y = pygame.mouse.get_pos()
                grid_x = int(mouse_x // cell_size)
                grid_y = int(Ny - 1 - (mouse_y // cell_size))
                if GRID[grid_y][grid_x][0] == 0:
                    nb_actions += 1
                    print("NB_ACTIONS : ", nb_actions, " / 3")
                    new_worm = players[player_id].Worm(grid_x, grid_y, worm_id=len(players[player_id].wormz))
                    players[player_id].wormz.append(new_worm)
                    refresh_UI = True
                else:
                    print("CANNOT PUT WORM HERE")

        # change de worm selectionne pour le missile
        if (event.type == pygame.KEYDOWN) and (event.key == pygame.K_TAB):
            if players[player_id].wormz != []:
                id_worm_launch = (id_worm_launch + 1) % len(players[player_id].wormz)
                screen.fill((0, 0, 0))
                pygame.draw.circle(
                    screen,
                    (255, 0, 0),
                    (
                        players[player_id].wormz[id_worm_launch].x_pos * cell_size,
                        (Ny - players[player_id].wormz[id_worm_launch].y_pos - 1) * cell_size,
                    ),
                    cell_size,
                )
                refresh_UI = True

        # finir un tour (changer de joueur)
        if (event.type == pygame.KEYDOWN) and (event.key == pygame.K_RETURN):
            player_id = (player_id+1)%2
            nb_actions = 0
            print("PLAYER ID : ", player_id)
            screen.fill((0, 0, 0))
            refresh_UI = True

        # acheter missile
        if (event.type == pygame.KEYDOWN) and (event.key == pygame.K_b) and (nb_actions < 3):
            nb_actions += 1
            print("NB_ACTIONS : ", nb_actions, " / 3")
            weapon = players[player_id].Weapons()
            players[player_id].weapons.append(weapon)
            players[player_id].money -= 100
            screen.fill((0, 0, 0))
            refresh_UI = True

        # lancer un missile
        if (event.type == pygame.MOUSEBUTTONDOWN) and (event.button == 3) and (nb_actions < 3):
            nb_actions += 1
            print("NB_ACTIONS : ", nb_actions, " / 3")
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid_x = int(mouse_x // cell_size)
            grid_y = int(Ny - 1 - (mouse_y // cell_size))
            if (players[player_id].weapons != []) and (players[player_id].wormz != []):
                x_0_launch = players[player_id].wormz[id_worm_launch].x_pos
                y_0_launch = players[player_id].wormz[id_worm_launch].y_pos
                weapon = players[player_id].weapons.pop()
                trajectory = weapon.launch_trajectory(
                    grid_x, grid_y, x_0_launch, y_0_launch
                )

                i = 0
                exploded = False
                while (i < len(trajectory[0])) and (not exploded):

                    event = pygame.event.poll()
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            exit()

                    if (0 < int(trajectory[0][i]) < Nx) and (
                        0 < int(trajectory[1][i]) < Ny
                    ):
                        if GRID[int(trajectory[1][i])][int(trajectory[0][i])][0] in [
                            1,
                            2,
                        ] or (i == len(trajectory[0]) - 1):
                            exploded = True
                            for player in players:
                                for worm in player.wormz:
                                    if (
                                        (worm.x_pos - int(trajectory[0][i])) ** 2
                                        + (worm.y_pos - int(trajectory[1][i])) ** 2
                                    ) < weapon.radius_explosion**2:
                                        worm.take_damage(weapon.damage)
                                        if worm.health <= 0:
                                            player.kill_worm(worm.worm_id)
                                    elif (
                                        (worm.x_pos - int(trajectory[0][i])) ** 2
                                        + (worm.y_pos - int(trajectory[1][i])) ** 2
                                    ) < weapon.radius_break**2:
                                        worm.take_damage(weapon.damage / 2)
                                        if worm.health <= 0:
                                            player.kill_worm(worm.worm_id)
                                    print("health : ", worm.health)
                            GRID = shapes.transform(
                                GRID,
                                int(trajectory[0][i]),
                                int(trajectory[1][i]),
                                weapon.radius_break,
                                2,
                            )
                            GRID = shapes.transform(
                                GRID,
                                int(trajectory[0][i]),
                                int(trajectory[1][i]),
                                weapon.radius_explosion,
                                0,
                            )
                            dp.show_grid_pygame(
                                screen, GRID, player1.wormz, player2.wormz
                            )
                            pygame.display.flip()
                            clock.tick(2000)

                    screen.fill((0, 0, 0))
                    dp.show_grid_pygame(screen, GRID, player1.wormz, player2.wormz)
                    dp.display_weapon(screen, trajectory[0][i], trajectory[1][i])
                    pygame.display.flip()
                    clock.tick(60)
                    i += 1
            else:
                print("CAN'T SHOOT WEAPON")

            screen.fill((0, 0, 0))
            refresh_UI = True

        # step
        GRID, moved = physics.step(GRID, player1, player2)
        if moved:
            refresh_UI = True
        while moved:

            event = pygame.event.poll()
            if event.type == pygame.QUIT:
                running = False

            GRID, moved = physics.step(GRID, player1, player2)
            GRID = physics.apply_object_cuts(GRID)

            screen.fill((0, 0, 0))
            dp.show_grid_pygame(screen, GRID, player1.wormz, player2.wormz)
            pygame.display.flip()
            clock.tick(60)


        if refresh_UI:
            dp.show_grid_pygame(screen, GRID, player1.wormz, player2.wormz)
            dp.draw_shop(screen, player1, player2, font)
            refresh_UI = False
            pygame.display.flip()

        #dp.draw_UI(screen, player1, font)
        clock.tick(60)

    pygame.quit()
