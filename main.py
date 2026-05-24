#!/bin/python3
# import matplotlib.pyplot as plt
import io
import json
import os
import sqlite3

import matplotlib.image as mpimg
import numpy as np
import pygame

import assets
import display as dp
import physics
import shapes

# fonctions de la base de DB


# liste les sauvegardes disponibles
def list_saves():
    """
    permet de retourner la liste de parties enregistréest trouvées dans la DB
    """

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT id FROM saves ORDER BY id")
    rows = cur.fetchall()

    conn.close()

    print("Available saves:")
    for (save_id,) in rows:
        print(f"- {save_id}")

    return [r[0] for r in rows]


# à ne lancer qu'une fois
def init_db():
    """
    initialise la DB : game.db, lorsqu'elle n'existe pas
    """

    conn = sqlite3.connect("game.db")
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS saves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            grid BLOB NOT NULL,
            players TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# vérifie si la DB exite, si elle existe pas, on lance init_db()
def ensure_db_exists(db_path="game.db"):
    """
    vérifie que la DB : game.db existe, si c'est pas le cas ça la crée
    """
    if not os.path.exists(db_path):
        print("DB not found → initializing...")
        init_db()
    else:
        print("DB already exists.")


ensure_db_exists()
DB_PATH = os.path.join(os.path.dirname(__file__), "game.db")


# save
def save_game(grid, players):
    """
    fonction écrivant dans la DB l'état de la partie : joueurs et GRID afin de pouvoir recharger ces informations et reprendre la partie si besoin
    """

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # grid → bytes
    buffer = io.BytesIO()
    np.save(buffer, grid)
    grid_blob = buffer.getvalue()

    # players → JSON
    state_json = json.dumps(players)

    cur.execute(
        "INSERT INTO saves (grid, players) VALUES (?, ?)", (grid_blob, state_json)
    )

    conn.commit()
    conn.close()


def load_game(save_id):
    """
    fonction permettant de charger une partie sauvegardée dans la DB
    """

    conn = sqlite3.connect("game.db")
    cur = conn.cursor()

    cur.execute("SELECT grid, players FROM saves WHERE id=?", (save_id,))
    grid_blob, state_json = cur.fetchone()

    buffer = io.BytesIO(grid_blob)
    grid = np.load(buffer)

    players = json.loads(state_json)

    conn.close()
    return (
        grid,
        assets.Player.from_dict(players[0]),
        assets.Player.from_dict(players[1]),
    )


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
bridge1 = mpimg.imread("map/bridge1.png")
bridge2 = mpimg.imread("map/bridge2.png")
bridge3 = mpimg.imread("map/bridge3.png")
bridge4 = mpimg.imread("map/bridge4.png")
dirt_pixel = ground[99, 0]
grass_pixel = ground[86, 0]
bridge_pixel = bridge1[35, 33]

for y in range(Ny):
    for x in range(Nx):
        if ground[y, x][3] != 0.0:
            if (ground[y, x] == dirt_pixel).all():
                GRID[Ny - y - 1][x] = (1, -1, 3)
            if (ground[y, x] == grass_pixel).all():
                GRID[Ny - y - 1][x] = (1, -1, 4)
        if bridge1[y, x][3] != 0.0:
            GRID[Ny - y - 1][x] = (1, 1, 5)
        if bridge2[y, x][3] != 0.0:
            GRID[Ny - y - 1][x] = (1, 2, 5)
        if bridge3[y, x][3] != 0.0:
            GRID[Ny - y - 1][x] = (1, 3, 5)
        if bridge4[y, x][3] != 0.0:
            GRID[Ny - y - 1][x] = (1, 4, 5)


# dp.show_grid(GRID)
# plt.pause(0.1)

valid_ids = list_saves()

print("Valid save ids:", valid_ids)

# demande un save_id, si il est pas correcte, on commence une nouvelle partie

save_id = int(input("Enter save id: "))
if save_id not in valid_ids:
    print("Invalid save id.")
    print("Starting a new game !")
    player1 = assets.Player()
    player2 = assets.Player()
    worm1 = player1.Worm(25, Ny - 59 - 1, worm_id=0)
    worm2 = player2.Worm(163, Ny - 41 - 1, worm_id=0)
    player1.wormz.append(worm1)
    player2.wormz.append(worm2)
    for i in range(3):
        weapon1 = player1.missile()
        weapon2 = player2.missile()
        player1.weapons[0].append(weapon1)
        player2.weapons[0].append(weapon2)
else:
    GRID, player1, player2 = load_game(save_id)


players = [player1, player2]
player_id = 0
weapon_type = 0

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
    OVERRIDE = True
    if OVERRIDE:
        screen = pygame.display.set_mode((1920, 1080))
    clock = pygame.time.Clock()

    running = True
    clock.tick(2000)

    screen.fill((0, 255, 255))
    dp.show_grid_pygame(screen, GRID, player1.wormz, player2.wormz)
    dp.draw_shop(screen, player1, player2, font)

    refresh_UI = True

    pygame.display.flip()

    # main game loop

    nb_actions = 0
    check_step = False
    GRID, moved = physics.step(GRID, player1, player2)

    while running:
        # gestion des inputs

        for event in pygame.event.get():

            # si la fenetre change de taille
    
            info = pygame.display.Info()
            if (
                (screen_width != info.current_w)
                or (screen_height != info.current_h)
                or ((event.type == pygame.KEYDOWN) and (event.key == pygame.K_r))
            ):
                screen_width = info.current_w
                screen_height = info.current_h
                screen = pygame.display.set_mode((screen_width, screen_height))
                pygame.display.flip()
                screen.fill((0, 255, 255))
                refresh_UI = True
    
            # quitter le jeu ( action de quitter : cliquer la croix sur la fenetre pygame )
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                exit()
    
            # enregistre et quitte le jeu ( key : q )
            if (event.type == pygame.KEYDOWN) and (event.key == pygame.K_q):
                print("Sauvegarde en cours...")
                save_game(GRID, [player.to_dict() for player in players])
                running = False
                print("Sauvegarde terminée.")
    
            # ajout de worm ( clique gauche )
            if (
                (event.type == pygame.MOUSEBUTTONDOWN)
                and (event.button == 1)
                and (nb_actions < 3)
            ):
                if players[player_id].money >= 200:
                    players[player_id].money -= 200
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    grid_x = int(mouse_x // cell_size)
                    grid_y = int(Ny - 1 - (mouse_y // cell_size))
                    if GRID[grid_y][grid_x][0] == 0:
                        nb_actions += 1
                        print("NB_ACTIONS : ", nb_actions, " / 3")
                        new_worm = players[player_id].Worm(
                            grid_x, grid_y, worm_id=len(players[player_id].wormz)
                        )
                        players[player_id].wormz.append(new_worm)
                        refresh_UI = True
                        check_step = True
                    else:
                        print("CANNOT PUT WORM HERE")
    
            # change de worm selectionne pour le missile ( key : tab )
            if (event.type == pygame.KEYDOWN) and (event.key == pygame.K_TAB):
                if players[player_id].wormz != []:
                    id_worm_launch = (id_worm_launch + 1) % len(players[player_id].wormz)
                    screen.fill((0, 255, 255))
                    pygame.draw.circle(
                        screen,
                        (255, 0, 0),
                        (
                            players[player_id].wormz[id_worm_launch].x_pos * cell_size,
                            (Ny - players[player_id].wormz[id_worm_launch].y_pos - 1)
                            * cell_size,
                        ),
                        cell_size,
                    )
                    refresh_UI = True
    
            # change de type d'arme pour le clique droit ( key : left shift )
            if (event.type == pygame.KEYDOWN) and (event.key == pygame.K_LSHIFT):
                weapon_type = (weapon_type + 1) % 2
                print("WEAPON_TYPE : ", weapon_type)
                screen.fill((0, 255, 255))
                refresh_UI = True
    
            # finir un tour (changer de joueur) ( key : entrer )
            if (event.type == pygame.KEYDOWN) and (event.key == pygame.K_RETURN):
                id_worm_launch = 0
                player_id = (player_id + 1) % 2
                weapon_type = 0
                nb_actions = 0
                print("PLAYER ID : ", player_id)
                screen.fill((0, 255, 255))
                refresh_UI = True
    
            # acheter missile ( key : m )
            if (
                (event.type == pygame.KEYDOWN)
                and (event.key == pygame.K_m)
                and (nb_actions < 3)
                and (players[player_id].money >= 150)
            ):
                nb_actions += 1
                print("NB_ACTIONS : ", nb_actions, " / 3")
                weapon = players[player_id].missile()
                players[player_id].weapons[0].append(weapon)
                players[player_id].money -= 150
                screen.fill((0, 255, 255))
                refresh_UI = True
    
            # acheter strike , coute 2 actions (key : s)
            if (
                (event.type == pygame.KEYDOWN)
                and (event.key == pygame.K_s)
                and (nb_actions < 2)
                and (players[player_id].money >= 300)
            ):
                nb_actions += 2
                print("NB_ACTIONS : ", nb_actions, " / 3")
                weapon = players[player_id].strike()
                players[player_id].weapons[1].append(weapon)
                players[player_id].money -= 300
                screen.fill((0, 255, 255))
                refresh_UI = True
    
            # lancer un missile / strike (clique droit)
            if (
                (event.type == pygame.MOUSEBUTTONDOWN)
                and (event.button == 3)
                and (nb_actions < 3)
            ):
                nb_actions += 1
                print("NB_ACTIONS : ", nb_actions, " / 3")
                mouse_x, mouse_y = pygame.mouse.get_pos()
                grid_x = int(mouse_x // cell_size)
                grid_y = int(Ny - 1 - (mouse_y // cell_size))
                if (players[player_id].weapons[weapon_type] != []) and (
                    players[player_id].wormz != []
                ):
                    x_0_launch = players[player_id].wormz[id_worm_launch].x_pos
                    y_0_launch = players[player_id].wormz[id_worm_launch].y_pos
                    weapon = players[player_id].weapons[weapon_type].pop()
                    trajectory = weapon.launch_trajectory(
                        grid_x, grid_y, x_0_launch, y_0_launch
                    )
    
                    i = 0
                    exploded = False
                    while (i < len(trajectory[0])) and (not exploded):
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
                                for k in range(len(players)):
                                    player = players[k]
                                    for worm in player.wormz:
                                        if (
                                            (worm.x_pos - int(trajectory[0][i])) ** 2
                                            + (worm.y_pos - int(trajectory[1][i])) ** 2
                                        ) < weapon.radius_explosion**2:
                                            worm.take_damage(weapon.damage)
                                            if worm.health <= 0:
                                                player.kill_worm(worm.worm_id)
                                                players[(k + 1) % 2].money += 150
                                        elif (
                                            (worm.x_pos - int(trajectory[0][i])) ** 2
                                            + (worm.y_pos - int(trajectory[1][i])) ** 2
                                        ) < weapon.radius_break**2:
                                            worm.take_damage(weapon.damage / 2)
                                            if worm.health <= 0:
                                                player.kill_worm(worm.worm_id)
                                                players[(k + 1) % 2].money += 150
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
    
                        screen.fill((0, 255, 255))
                        dp.show_grid_pygame(screen, GRID, player1.wormz, player2.wormz)
                        dp.display_weapon(screen, trajectory[0][i], trajectory[1][i])
                        pygame.display.flip()
                        clock.tick(30)
                        i += 1
                else:
                    print("CAN'T SHOOT WEAPON")
    
                screen.fill((0, 255, 255))
                refresh_UI = True
                check_step = True
    
            # step
            if check_step:
                GRID, moved = physics.step(GRID, player1, player2)
                print("checking step funciton")

            if (not moved):
                check_step = False
    
            # met à jour l'affichage si la grille / les wormz ont bougés
            if moved:
                refresh_UI = True
            while moved:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
    
                GRID, moved = physics.step(GRID, player1, player2)
                GRID = physics.apply_object_cuts(GRID)
    
                screen.fill((0, 255, 255))
                dp.show_grid_pygame(screen, GRID, player1.wormz, player2.wormz)
                pygame.display.flip()
                clock.tick(30)
                check_step = True
    
            # affiche au dessus les élément d'UI après avoir rafraichi la grid et les wormz
            if refresh_UI:
                dp.show_grid_pygame(screen, GRID, player1.wormz, player2.wormz)
                dp.draw_shop(screen, player1, player2, font)
                dp.show_UI(
                    screen, player1, player2, font, player_id, weapon_type, nb_actions
                )
                refresh_UI = False
                pygame.display.flip()
    
            clock.tick(300)
    
pygame.quit()
