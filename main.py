#!/bin/python3
# import matplotlib.pyplot as plt
import argparse
import io
import json
import os
import sqlite3

import matplotlib.image as mpimg
import numpy as np
import pygame

import assets
import DSL
import display as dp
import physics
import shapes

# Fonctions d'accès à la base de données.


# Liste les sauvegardes disponibles.
def list_saves():
    """
    Retourne les identifiants des parties enregistrées dans la base de données.
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


# Initialise le schéma de la base.
def init_db():
    """
    Crée la base `game.db` et sa table de sauvegardes si elles n'existent pas.
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


# Vérifie que la base existe avant de lancer le jeu.
def ensure_db_exists(db_path="game.db"):
    """
    Crée la base `game.db` si elle est absente.
    """
    if not os.path.exists(db_path):
        print("DB not found → initializing...")
        init_db()
    else:
        print("DB already exists.")


ensure_db_exists()
DB_PATH = os.path.join(os.path.dirname(__file__), "game.db")


# Sauvegarde l'état courant de la partie.
def save_game(grid, players):
    """
    Écrit la grille et l'état des joueurs dans la base pour pouvoir reprendre la partie.
    """

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Sérialisation de la grille en octets.
    buffer = io.BytesIO()
    np.save(buffer, grid)
    grid_blob = buffer.getvalue()

    # Sérialisation des joueurs en JSON.
    state_json = json.dumps(players)

    cur.execute(
        "INSERT INTO saves (grid, players) VALUES (?, ?)", (grid_blob, state_json)
    )

    conn.commit()
    conn.close()


def load_game(save_id):
    """
    Charge une partie sauvegardée depuis la base de données.
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

parser = argparse.ArgumentParser()
parser.add_argument(
    "-c",
    "--config",
    help="fichier de configuration custom pour une nouvelle partie",
)
args = parser.parse_args()


# Dimensions de la grille.
Nx, Ny = 192, 108
cell_size = 10
game_config = DSL.load_config(args.config, Ny) if args.config else DSL.default_config(Ny)

# Types de matériaux :
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

# Lit les images utilisées pour générer la carte et ses objets.

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

prices = game_config["prices"]
kill_reward = game_config["bonuses"]["kill_reward"]

##### CODE DE TEST LEGACY, qui n'est plus compatible avec le projet #####
#
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
    # Initialise Pygame et sa fenêtre.
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

    # Menu de démarrage : nouvelle partie ou chargement de la dernière sauvegarde.
    if args.config:
        print(f"Starting a new custom game from {args.config} !")
        player1, player2 = DSL.create_players(game_config)
    else:
        menu_action, save_id = dp.run_start_menu(screen, clock, GRID, valid_ids, cell_size)
        if menu_action == "load" and save_id in valid_ids:
            print(f"Loading save #{save_id}...")
            GRID, player1, player2 = load_game(save_id)
        else:
            print("Starting a new game !")
            player1, player2 = DSL.create_players(game_config)

    players = [player1, player2]
    player_id = 0
    weapon_type = 0

    running = True

    screen.fill((0, 255, 255))
    dp.show_grid_pygame(screen, GRID, player1.wormz, player2.wormz)
    dp.draw_shop(screen, player1, player2, font, prices)

    refresh_UI = True

    pygame.display.flip()

    # Boucle principale du jeu.

    nb_actions = 0
    check_step = False
    #GRID, moved = physics.step(GRID, player1, player2)
    GRID, moved = physics.step_vectorized(GRID, player1, player2)

    while running:
        # Gestion des entrées utilisateur.

        for event in pygame.event.get():

            # Redimensionne la fenêtre si sa taille change ou si la touche R est pressée.
    
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
    
            # Quitte le jeu via la fermeture de la fenêtre Pygame.
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                exit()
    
            # Sauvegarde la partie puis quitte le jeu avec la touche Q.
            if (event.type == pygame.KEYDOWN) and (event.key == pygame.K_q):
                print("Sauvegarde en cours...")
                save_game(GRID, [player.to_dict() for player in players])
                running = False
                print("Sauvegarde terminée.")
    
            # Ajoute un worm avec le clic gauche.
            if (
                (event.type == pygame.MOUSEBUTTONDOWN)
                and (event.button == 1)
                and (nb_actions < 3)
            ):
                if players[player_id].money >= prices["worm"]:
                    players[player_id].money -= prices["worm"]
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
    
            # Change le worm sélectionné pour lancer un missile avec Tab.
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
    
            # Change le type d'arme utilisé par le clic droit avec Maj gauche.
            if (event.type == pygame.KEYDOWN) and (event.key == pygame.K_LSHIFT):
                weapon_type = (weapon_type + 1) % 2
                print("WEAPON_TYPE : ", weapon_type)
                screen.fill((0, 255, 255))
                refresh_UI = True
    
            # Termine le tour et passe au joueur suivant avec Entrée.
            if (event.type == pygame.KEYDOWN) and (event.key == pygame.K_RETURN):
                id_worm_launch = 0
                player_id = (player_id + 1) % 2
                weapon_type = 0
                nb_actions = 0
                print("PLAYER ID : ", player_id)
                screen.fill((0, 255, 255))
                refresh_UI = True
    
            # Achète un missile avec la touche M.
            if (
                (event.type == pygame.KEYDOWN)
                and (event.key == pygame.K_m)
                and (nb_actions < 3)
                and (players[player_id].money >= prices["missile"])
            ):
                nb_actions += 1
                print("NB_ACTIONS : ", nb_actions, " / 3")
                weapon = DSL.make_weapon(
                    players[player_id], "missile", game_config["weapon_stats"]["missile"]
                )
                players[player_id].weapons[0].append(weapon)
                players[player_id].money -= prices["missile"]
                screen.fill((0, 255, 255))
                refresh_UI = True
    
            # Achète un strike avec la touche S ; cette action coûte deux points.
            if (
                (event.type == pygame.KEYDOWN)
                and (event.key == pygame.K_s)
                and (nb_actions < 2)
                and (players[player_id].money >= prices["strike"])
            ):
                nb_actions += 2
                print("NB_ACTIONS : ", nb_actions, " / 3")
                weapon = DSL.make_weapon(
                    players[player_id], "strike", game_config["weapon_stats"]["strike"]
                )
                players[player_id].weapons[1].append(weapon)
                players[player_id].money -= prices["strike"]
                screen.fill((0, 255, 255))
                refresh_UI = True
    
            # Lance un missile ou un strike avec le clic droit.
            if (
                (event.type == pygame.MOUSEBUTTONDOWN)
                and (event.button == 3)
                and (nb_actions < 3)
            ):
                print("NB_ACTIONS : ", nb_actions, " / 3")
                mouse_x, mouse_y = pygame.mouse.get_pos()
                grid_x = int(mouse_x // cell_size)
                grid_y = int(Ny - 1 - (mouse_y // cell_size))
                x_0_launch = players[player_id].wormz[id_worm_launch].x_pos
                y_0_launch = players[player_id].wormz[id_worm_launch].y_pos
                if (players[player_id].weapons[weapon_type] != []) and (
                    players[player_id].wormz != [] and ( (weapon_type == 1) or ( ( (x_0_launch - grid_x)**2 + (y_0_launch - grid_y)**2) <= (players[player_id].wormz[-1].worm_range**2) ) ) 
                ):
                    nb_actions += 1
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
                                                players[(k + 1) % 2].money += kill_reward
                                        elif (
                                            (worm.x_pos - int(trajectory[0][i])) ** 2
                                            + (worm.y_pos - int(trajectory[1][i])) ** 2
                                        ) < weapon.radius_break**2:
                                            worm.take_damage(weapon.damage / 2)
                                            if worm.health <= 0:
                                                player.kill_worm(worm.worm_id)
                                                players[(k + 1) % 2].money += kill_reward
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
                        clock.tick(60)
                        i += 1
                else:
                    print("CAN'T SHOOT WEAPON")
    
                screen.fill((0, 255, 255))
                refresh_UI = True
                check_step = True
    
            # Met à jour la physique si nécessaire.
            if check_step:
                #GRID, moved = physics.step(GRID, player1, player2)
                GRID, moved = physics.step_vectorized(GRID, player1, player2)
                print("checking step function")

            if (not moved):
                check_step = False
    
            # Rafraîchit l'affichage si la grille ou les wormz ont bougé.
            if moved:
                refresh_UI = True
            while moved:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
    
                #GRID, moved = physics.step(GRID, player1, player2)
                GRID, moved = physics.step_vectorized(GRID, player1, player2)
                GRID = physics.apply_object_cuts(GRID)
    
                screen.fill((0, 255, 255))
                dp.show_grid_pygame(screen, GRID, player1.wormz, player2.wormz)
                pygame.display.flip()
                clock.tick(120)
                check_step = True

            GRID, moved = physics.step_vectorized(GRID, player1, player2, direction=-1)
            GRID, moved = physics.step_vectorized(GRID, player1, player2, direction=1)
            check_step = True
    
            # Affiche les éléments d'interface après le rafraîchissement de la grille et des wormz.
            if refresh_UI:
                dp.show_grid_pygame(screen, GRID, player1.wormz, player2.wormz)
                dp.draw_shop(screen, player1, player2, font, prices)
                dp.show_UI(
                    screen, player1, player2, font, player_id, weapon_type, nb_actions
                )
                refresh_UI = False
                pygame.display.flip()
    
            clock.tick(300)
    
pygame.quit()
