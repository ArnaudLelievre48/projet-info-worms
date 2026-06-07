# Fonctions d'affichage avec Matplotlib et Pygame.

import os

import matplotlib.pyplot as plt
import numpy as np
import pygame
from matplotlib.colors import ListedColormap

cmap = ListedColormap(["gray", "red", "orange"])


# Affichage Matplotlib.
def show_grid_matplotlib(grid):
    """
    Affiche la grille avec Matplotlib pour faciliter le débogage.
    """

    grid_show = np.array([[cell[0] for cell in row] for row in grid])

    plt.clf()
    plt.imshow(grid_show, cmap=cmap, vmin=0, vmax=2, origin="lower")
    plt.colorbar(ticks=[0, 1, 2])


# Affichage Pygame.
def draw_cell(screen: pygame.Surface, x, y, cell_size=10):
    """
    Dessine une cellule de la grille sur l'écran Pygame.
    """

    rect = pygame.Rect(x * cell_size, y * cell_size, cell_size - 1, cell_size - 1)
    pygame.draw.rect(screen, (255, 0, 0), rect)


def show_grid_pygame(screen, grid, wormz1, wormz2, cell_size=10):
    """
    Affiche la grille avec les textures correspondantes, ainsi que les wormz.

    Les textures sont mises en cache pour éviter de les recharger à chaque frame.
    """
    Ny = len(grid)
    Nx = len(grid[0])

    if not hasattr(show_grid_pygame, "cache"):
        show_grid_pygame.cache = {}

    cache = show_grid_pygame.cache

    for y in range(Ny):
        for x in range(Nx):
            material, obj, tex = grid[Ny - 1 - y][x]

            # AIR : rien à dessiner, car l'écran est effacé avant chaque rendu.
            if material == 0:
                continue

            if tex not in cache:
                path = "textures/{}.png".format(tex)
                if not os.path.exists(path):
                    continue

                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, (cell_size, cell_size))
                cache[tex] = img

            screen.blit(cache[tex], (x * cell_size, y * cell_size))

    for worm in wormz1:
        tex = -1
        path = "textures/worm1.png"
        if not os.path.exists(path):
            continue

        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.scale(img, (2*cell_size, 2*cell_size))
        cache[tex] = img
        screen.blit(
            cache[tex], (worm.x_pos * cell_size - cell_size/2, (Ny - worm.y_pos - 1) * cell_size - cell_size)
        )

    for worm in wormz2:
        tex = -1
        path = "textures/worm2.png"
        if not os.path.exists(path):
            continue

        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.scale(img, (2*cell_size, 2*cell_size))
        cache[tex] = img
        screen.blit(
            cache[tex], (worm.x_pos * cell_size - cell_size/2, (Ny - worm.y_pos - 1) * cell_size - cell_size)
        )


def draw_missile_range(screen, grid, worm, cell_size=10):
    """
    Affiche la portée de tir du missile autour du worm sélectionné.
    """
    Ny = len(grid)
    radius = int(worm.worm_range * cell_size)
    diameter = radius * 2
    center_x = int(worm.x_pos * cell_size + cell_size / 2)
    center_y = int((Ny - worm.y_pos - 1) * cell_size + cell_size / 2)
    worm_center_y = int((Ny - worm.y_pos - 1) * cell_size)

    range_surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
    pygame.draw.circle(range_surface, (40, 220, 80, 20), (radius, radius), radius)
    pygame.draw.circle(range_surface, (40, 220, 80, 130), (radius, radius), radius, 3)

    screen.blit(range_surface, (center_x - radius, center_y - radius))
    pygame.draw.circle(
        screen,
        (255, 255, 255),
        (center_x, worm_center_y),
        int(cell_size * 1.75),
        3,
    )


weapon_cache = {}


def display_weapon(screen, traj_x, traj_y, cell_size=10):
    """
    Affiche une arme à une position donnée de sa trajectoire.
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


def draw_shop(screen, player1, player2, font, prices=None):
    """
    Affiche les prix des objets achetables pour les deux joueurs.
    """
    if prices is None:
        prices = {"worm": 200, "missile": 150, "strike": 300}

    width = screen.get_width()

    pygame.draw.rect(screen, (100, 80, 80), pygame.Rect(width - 650, 10, 200, 40))
    pygame.draw.rect(screen, (100, 80, 80), pygame.Rect(width - 450, 10, 200, 40))

    txt1 = font.render(
        "Weapon : {} | {}".format(prices["missile"], prices["strike"]), True, (255, 255, 255)
    )

    txt2 = font.render("Worm : {}".format(prices["worm"]), True, (255, 255, 255))

    screen.blit(txt1, (100, 20))
    screen.blit(txt2, (300, 20))
    screen.blit(txt1, (width - 600, 20))
    screen.blit(txt2, (width - 400, 20))


def show_UI(
    screen, player1, player2, font, player_id, weapon_type, nb_actions, cell_size=10
):
    """
    Affiche l'interface de jeu : joueur actif, arme sélectionnée, argent et inventaire.
    """
    txtmoney1 = font.render("player1's money: {}".format(player1.money), True, (255, 255, 255))
    txtmoney2 = font.render("player2's money: {}".format(player2.money), True, (255, 255, 255))

    txtmissile1 = font.render(
        "player1's missiles: {}".format(len(player1.weapons[0])), True, (255, 255, 255)
    )
    txtstrike1 = font.render(
        "player1's missiles: {}".format(len(player1.weapons[1])), True, (255, 255, 255)
    )

    txtmissile2 = font.render(
        "player2's missiles: {}".format(len(player2.weapons[0])), True, (255, 255, 255)
    )
    txtstrike2 = font.render(
        "player2's missiles: {}".format(len(player2.weapons[1])), True, (255, 255, 255)
    )

    txt_player = font.render("player {}".format(player_id + 1), True, (255, 255, 255))
    if weapon_type == 0:
        weapon_name = "Missile"
    if weapon_type ==1 :
        weapon_name = "Strike"
    txt_weapon_type = font.render("weapon type: {}".format(weapon_name), True, (255, 255, 255))
    txt_nb_actions = font.render("nb actions: {} / 3".format(nb_actions), True, (255, 255, 255))

    screen.blit(txtmoney1, (10 * cell_size, 15 * cell_size))
    screen.blit(txtmissile1, (10 * cell_size, 20 * cell_size))
    screen.blit(txtstrike1, (10 * cell_size, 25 * cell_size))

    screen.blit(txtmoney2, (158 * cell_size, 15 * cell_size))
    screen.blit(txtmissile2, (158 * cell_size, 20 * cell_size))
    screen.blit(txtstrike2, (158 * cell_size, 25 * cell_size))

    screen.blit(txt_player, (96 * cell_size, 5 * cell_size))
    screen.blit(txt_weapon_type, (96 * cell_size, 10 * cell_size))
    screen.blit(txt_nb_actions, (96 * cell_size, 15 * cell_size))


def draw_start_menu_background(screen, grid, cell_size, tick):
    """
    Dessine un fond de menu animé dans le thème du terrain du jeu.
    """
    width = screen.get_width()
    height = screen.get_height()

    sky_top = (82, 188, 221)
    sky_bottom = (164, 227, 238)
    for y in range(height):
        ratio = y / max(height - 1, 1)
        color = (
            int(sky_top[0] * (1 - ratio) + sky_bottom[0] * ratio),
            int(sky_top[1] * (1 - ratio) + sky_bottom[1] * ratio),
            int(sky_top[2] * (1 - ratio) + sky_bottom[2] * ratio),
        )
        pygame.draw.line(screen, color, (0, y), (width, y))

    cloud_color = (236, 249, 248)
    cloud_shadow = (205, 235, 232)
    for i, base_y in enumerate((120, 220, 165)):
        x = ((tick * (0.25 + i * 0.08)) + i * width * 0.37) % (width + 260) - 180
        pygame.draw.ellipse(
            screen, cloud_shadow, pygame.Rect(x + 18, base_y + 20, 170, 42)
        )
        pygame.draw.ellipse(screen, cloud_color, pygame.Rect(x, base_y + 16, 190, 48))
        pygame.draw.circle(screen, cloud_color, (int(x + 52), base_y + 24), 34)
        pygame.draw.circle(screen, cloud_color, (int(x + 112), base_y + 15), 42)

    Ny = len(grid)
    Nx = len(grid[0])
    scale = max(width / (Nx * cell_size), height / (Ny * cell_size))
    preview_cell = max(4, int(cell_size * scale))
    terrain_width = Nx * preview_cell
    terrain_height = Ny * preview_cell
    offset_x = (width - terrain_width) // 2
    offset_y = height - terrain_height + 30

    if not hasattr(draw_start_menu_background, "cache"):
        draw_start_menu_background.cache = {}
    cache = draw_start_menu_background.cache

    for y in range(Ny):
        for x in range(Nx):
            material, obj, tex = grid[Ny - 1 - y][x]
            if material == 0:
                continue
            if tex not in cache or cache[tex].get_width() != preview_cell:
                path = "textures/{}.png".format(tex)
                if not os.path.exists(path):
                    continue
                img = pygame.image.load(path).convert_alpha()
                cache[tex] = pygame.transform.scale(img, (preview_cell, preview_cell))
            screen.blit(
                cache[tex], (offset_x + x * preview_cell, offset_y + y * preview_cell)
            )

    for i in range(42):
        x = int((i * 73 + tick * (1.4 + (i % 5) * 0.25)) % width)
        y = int(height * 0.48 + ((i * 37 + tick * 1.8) % max(int(height * 0.42), 1)))
        radius = 2 + (i % 3)
        color = (121, 87, 52) if i % 2 else (196, 171, 89)
        pygame.draw.circle(screen, color, (x, y), radius)

    missile_x = int((tick * 2.4) % (width + 220) - 110)
    missile_y = int(height * 0.26 + np.sin(tick * 0.035) * 42)
    pygame.draw.line(
        screen,
        (255, 236, 151),
        (missile_x - 64, missile_y + 18),
        (missile_x - 12, missile_y + 4),
        5,
    )
    pygame.draw.circle(screen, (232, 83, 44), (missile_x, missile_y), 8)
    pygame.draw.circle(screen, (62, 62, 62), (missile_x + 12, missile_y - 3), 5)


def draw_menu_button(screen, font, rect, text, mouse_pos, enabled=True):
    hovered = enabled and rect.collidepoint(mouse_pos)
    if enabled:
        fill = (55, 71, 79) if not hovered else (72, 97, 106)
        border = (255, 239, 178) if hovered else (219, 204, 150)
        text_color = (255, 255, 255)
    else:
        fill = (102, 114, 118)
        border = (135, 148, 152)
        text_color = (190, 201, 204)

    pygame.draw.rect(screen, (0, 0, 0), rect.move(0, 5), border_radius=8)
    pygame.draw.rect(screen, fill, rect, border_radius=8)
    pygame.draw.rect(screen, border, rect, width=3, border_radius=8)

    label = font.render(text, True, text_color)
    label_rect = label.get_rect(center=rect.center)
    screen.blit(label, label_rect)


def draw_controls_help(screen, title_font, text_font):
    """
    Affiche les commandes principales du jeu sur la gauche du menu.
    """
    controls = [
        ("Clic gauche", "Acheter et placer un worm"),
        ("Clic droit", "Lancer l'arme selectionnee"),
        ("Tab", "Changer de worm pour le tir"),
        ("Maj gauche", "Changer de type d'arme"),
        ("Entree", "Terminer le tour"),
        ("M", "Acheter un missile"),
        ("S", "Acheter un strike"),
        ("R", "Rafraichir la fenetre"),
        ("Q", "Sauvegarder et quitter"),
    ]

    width = screen.get_width()
    height = screen.get_height()
    panel_width = min(430, max(300, width // 4))
    panel_x = 42
    panel_y = max(96, int(height * 0.18))
    row_height = 38
    padding = 22
    panel_height = padding * 2 + 36 + len(controls) * row_height

    panel = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
    shadow = panel.move(0, 6)
    pygame.draw.rect(screen, (0, 0, 0), shadow, border_radius=8)
    pygame.draw.rect(screen, (245, 250, 244), panel, border_radius=8)
    pygame.draw.rect(screen, (83, 99, 78), panel, width=3, border_radius=8)

    title = title_font.render("COMMANDES", True, (36, 48, 52))
    screen.blit(title, (panel.x + padding, panel.y + padding - 2))

    key_color = (55, 71, 79)
    action_color = (36, 48, 52)
    key_bg = (219, 204, 150)
    y = panel.y + padding + 44
    key_width = 116

    for key, action in controls:
        key_rect = pygame.Rect(panel.x + padding, y - 5, key_width, 28)
        pygame.draw.rect(screen, key_bg, key_rect, border_radius=6)
        pygame.draw.rect(screen, (83, 99, 78), key_rect, width=2, border_radius=6)

        key_label = text_font.render(key, True, key_color)
        screen.blit(key_label, key_label.get_rect(center=key_rect.center))

        action_label = text_font.render(action, True, action_color)
        screen.blit(action_label, (key_rect.right + 14, y))
        y += row_height


def run_start_menu(screen, clock, grid, save_ids, cell_size=10):
    """
    Affiche le menu de démarrage et retourne ("play", None) ou ("load", save_id).
    """
    title_font = pygame.font.SysFont(None, 92)
    button_font = pygame.font.SysFont(None, 48)
    info_font = pygame.font.SysFont(None, 28)
    controls_title_font = pygame.font.SysFont(None, 34)
    controls_font = pygame.font.SysFont(None, 25)
    available_save_ids = sorted(save_ids)
    selected_save_index = len(available_save_ids) - 1
    tick = 0

    while True:
        selected_save_id = (
            available_save_ids[selected_save_index] if available_save_ids else None
        )
        mouse_pos = pygame.mouse.get_pos()
        width = screen.get_width()
        height = screen.get_height()
        button_width = min(620, width - 64)
        button_height = 72
        button_x = (width - button_width) // 2
        play_rect = pygame.Rect(button_x, int(height * 0.43), button_width, button_height)
        load_rect = pygame.Rect(button_x, play_rect.bottom + 24, button_width, button_height)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return "play", None
            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_n
                and available_save_ids
            ):
                selected_save_index = (selected_save_index + 1) % len(
                    available_save_ids
                )
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if play_rect.collidepoint(event.pos):
                    return "play", None
                if selected_save_id is not None and load_rect.collidepoint(event.pos):
                    return "load", available_save_ids[selected_save_index]

        selected_save_id = (
            available_save_ids[selected_save_index] if available_save_ids else None
        )

        draw_start_menu_background(screen, grid, cell_size, tick)
        draw_controls_help(screen, controls_title_font, controls_font)

        title = title_font.render("WORMS", True, (36, 48, 52))
        title_shadow = title_font.render("WORMS", True, (255, 239, 178))
        title_rect = title.get_rect(center=(width // 2, int(height * 0.25)))
        screen.blit(title_shadow, title_rect.move(4, 4))
        screen.blit(title, title_rect)

        draw_menu_button(screen, button_font, play_rect, "PLAY", mouse_pos)
        load_text = "CHARGER LA SAUVEGARDE"
        draw_menu_button(
            screen,
            button_font,
            load_rect,
            load_text,
            mouse_pos,
            enabled=selected_save_id is not None,
        )

        if selected_save_id is None:
            info_text = "Aucune sauvegarde disponible"
        else:
            info_text = (
                "Sauvegarde #{} "
                "({}/{})".format(
                    selected_save_id,
                    selected_save_index + 1,
                    len(available_save_ids),
                )
            )
        info_shadow = info_font.render(info_text, True, (0, 0, 0))
        info = info_font.render(info_text, True, (200, 200, 200))
        screen.blit(info_shadow, info.get_rect(center=(width // 2+3, load_rect.bottom + 28+3)))
        screen.blit(info, info.get_rect(center=(width // 2, load_rect.bottom + 28)))

        pygame.display.flip()
        tick += 1
        clock.tick(60)
