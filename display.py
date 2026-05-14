# display with matplotlib

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
import pygame
import os


cmap = ListedColormap(["gray", "red", "orange"])


# matplotlib
def show_grid_matplotlib(grid):
    grid_show = np.array([[cell[0] for cell in row] for row in grid])

    plt.clf()
    plt.imshow(grid_show, cmap=cmap, vmin=0, vmax=2, origin="lower")
    plt.colorbar(ticks=[0, 1, 2])


# pygame
def draw_cell(screen: pygame.Surface, x, y):
    cell_size = 10
    rect = pygame.Rect(x * cell_size, y * cell_size, cell_size - 1, cell_size - 1)
    pygame.draw.rect(screen, (255, 0, 0), rect)


def show_grid_pygame(screen, grid, wormz1, wormz2, cell_size=10):

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
        screen.blit(cache[tex], (worm.x_pos * cell_size, (Ny-worm.y_pos-1) * cell_size))

    for worm in wormz2:
        tex = -1
        path = f"textures/worm2.png"
        if not os.path.exists(path):
            continue

        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.scale(img, (cell_size, cell_size))
        cache[tex] = img
        screen.blit(cache[tex], (worm.x_pos * cell_size, (Ny-worm.y_pos-1) * cell_size))


weapon_cache = {}

def display_weapon(screen, traj_x, traj_y, cell_size=10):

    global weapon_cache

    Nx = 192
    Ny = 108

    tex = "weapon1"

    if tex not in weapon_cache:
        path = "textures/weapon1.png"
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.scale(img, (cell_size, cell_size))
        weapon_cache[tex] = img

    screen.blit(
        weapon_cache[tex],
        (traj_x * cell_size, (Ny - traj_y - 1) * cell_size)
    )

def draw_shop(screen, player1, player2, font):
    width = screen.get_width()

    pygame.draw.rect(screen, (100, 80, 80), pygame.Rect(width - 650, 10, 200, 40))
    pygame.draw.rect(screen, (100, 80, 80), pygame.Rect(width - 450, 10, 200, 40))


    txt1 = font.render(
        f"Weapon : {100}",
        True,
        (255,255,255)
    )

    txt2 = font.render(
        f"Worm : {200}",
        True,
        (255,255,255)
    )

    money1_txt = font.render(
        f"Money : {player1.money}",
        True,
        (255,255,0)
    )

    money2_txt = font.render(
        f"Money : {player2.money}",
        True,
        (255,255,0)
    )


    screen.blit(txt1, (100, 20))
    screen.blit(txt2, (300, 20))
    screen.blit(money1_txt, (500, 20))
    screen.blit(txt1, (width -600, 20))
    screen.blit(txt2, (width - 400, 20))
    screen.blit(money2_txt, (width - 200, 20))

