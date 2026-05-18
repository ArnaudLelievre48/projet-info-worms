# display with matplotlib

import os

import matplotlib.pyplot as plt
import numpy as np
import pygame
from matplotlib.colors import ListedColormap

cmap = ListedColormap(["gray", "red", "orange"])


# matplotlib
def show_grid_matplotlib(grid):
    """
    fonction qui a permis de débuger au début pour afficher dans matplotlib la GRID
    """

    grid_show = np.array([[cell[0] for cell in row] for row in grid])

    plt.clf()
    plt.imshow(grid_show, cmap=cmap, vmin=0, vmax=2, origin="lower")
    plt.colorbar(ticks=[0, 1, 2])


# pygame
def draw_cell(screen: pygame.Surface, x, y):
    """
    fonction permettant d'afficher une cellule de taille 10x10 : un bloc de la GRID
    """

    cell_size = 10
    rect = pygame.Rect(x * cell_size, y * cell_size, cell_size - 1, cell_size - 1)
    pygame.draw.rect(screen, (255, 0, 0), rect)


def show_grid_pygame(screen, grid, wormz1, wormz2, cell_size=10):
    """
    fonction permettant d'afficher la GRID avec les texture corresppondante au dessus (10px x 10px), ainsi que les wormz,  utilise du cache pour éviter d'avoir à re-render tout le temps
    """
    Ny = len(grid)
    Nx = len(grid[0])

    if not hasattr(show_grid_pygame, "cache"):
        show_grid_pygame.cache = {}

    cache = show_grid_pygame.cache

    for y in range(Ny):
        for x in range(Nx):
            material, obj, tex = grid[Ny - 1 - y][x]

            # AIR = explicitly do nothing (fine ONLY because screen is cleared)
            if material == 0:
                continue

            if tex not in cache:
                path = f"textures/{tex}.png"
                if not os.path.exists(path):
                    continue

                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, (cell_size, cell_size))
                cache[tex] = img

            screen.blit(cache[tex], (x * cell_size, y * cell_size))

    for worm in wormz1:
        tex = -1
        path = f"textures/worm1.png"
        if not os.path.exists(path):
            continue

        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.scale(img, (cell_size, cell_size))
        cache[tex] = img
        screen.blit(
            cache[tex], (worm.x_pos * cell_size, (Ny - worm.y_pos - 1) * cell_size)
        )

    for worm in wormz2:
        tex = -1
        path = f"textures/worm2.png"
        if not os.path.exists(path):
            continue

        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.scale(img, (cell_size, cell_size))
        cache[tex] = img
        screen.blit(
            cache[tex], (worm.x_pos * cell_size, (Ny - worm.y_pos - 1) * cell_size)
        )


weapon_cache = {}


def display_weapon(screen, traj_x, traj_y, cell_size=10):
    """
    fonction permettant l'affichage des weapons lors de leurs trajectoire
    """

    global weapon_cache

    Nx = 192
    Ny = 108

    tex = "weapon1"

    if tex not in weapon_cache:
        path = "textures/weapon1.png"
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.scale(img, (cell_size, cell_size))
        weapon_cache[tex] = img

    screen.blit(weapon_cache[tex], (traj_x * cell_size, (Ny - traj_y - 1) * cell_size))


def draw_shop(screen, player1, player2, font):
    """
    permet d'afficher le prix des items pour les 2 joueurs, une feature envisagée aurait été d'appliquer des bonus et malus de prix, mais on a pas eu le temps...
    """
    width = screen.get_width()

    pygame.draw.rect(screen, (100, 80, 80), pygame.Rect(width - 650, 10, 200, 40))
    pygame.draw.rect(screen, (100, 80, 80), pygame.Rect(width - 450, 10, 200, 40))

    txt1 = font.render(f"Weapon : {100} | {300}", True, (255, 255, 255))

    txt2 = font.render(f"Worm : {200}", True, (255, 255, 255))

    screen.blit(txt1, (100, 20))
    screen.blit(txt2, (300, 20))
    screen.blit(txt1, (width - 600, 20))
    screen.blit(txt2, (width - 400, 20))


def show_UI(
    screen, player1, player2, font, player_id, weapon_type, nb_actions, cell_size=10
):
    """
    fonction permettant d'afficher l'UI : ensemble des informations descrivant qui joue, avec quelle arme, la quantité d'argent, de wormz, d'armes...
    """
    txtmoney1 = font.render(f"player1's money: {player1.money}", True, (255, 255, 255))
    txtmoney2 = font.render(f"player2's money: {player2.money}", True, (255, 255, 255))

    txtmissile1 = font.render(
        f"player1's missiles: {len(player1.weapons[0])}", True, (255, 255, 255)
    )
    txtstrike1 = font.render(
        f"player1's missiles: {len(player1.weapons[1])}", True, (255, 255, 255)
    )

    txtmissile2 = font.render(
        f"player2's missiles: {len(player2.weapons[0])}", True, (255, 255, 255)
    )
    txtstrike2 = font.render(
        f"player2's missiles: {len(player2.weapons[1])}", True, (255, 255, 255)
    )

    txt_player = font.render(f"player {player_id+1}", True, (255, 255, 255))
    if weapon_type == 0:
        weapon_name = "Missile"
    if weapon_type ==1 :
        weapon_name = "Strike"
    txt_weapon_type = font.render(f"weapon type: {weapon_name}", True, (255, 255, 255))
    txt_nb_actions = font.render(f"nb actions: {nb_actions} / 3", True, (255, 255, 255))

    screen.blit(txtmoney1, (10 * cell_size, 15 * cell_size))
    screen.blit(txtmissile1, (10 * cell_size, 20 * cell_size))
    screen.blit(txtstrike1, (10 * cell_size, 25 * cell_size))

    screen.blit(txtmoney2, (158 * cell_size, 15 * cell_size))
    screen.blit(txtmissile2, (158 * cell_size, 20 * cell_size))
    screen.blit(txtstrike2, (158 * cell_size, 25 * cell_size))

    screen.blit(txt_player, (96 * cell_size, 5 * cell_size))
    screen.blit(txt_weapon_type, (96 * cell_size, 10 * cell_size))
    screen.blit(txt_nb_actions, (96 * cell_size, 15 * cell_size))
