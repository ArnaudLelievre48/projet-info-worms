# implémente la physique


from collections import defaultdict
import numpy as np
import random

# Définition des types de matériaux pour la gestion des collisions
AIR = 0
SOLID = 1
SAND = 2



#def step(grid):
#    h, w = grid.shape[:2]
#    new = grid.copy()
#
#    # bottom → top
#    for y in range(1, h):
#        for x in range(w):
#
#            material, obj_id, texture = grid[y, x]
#
#            if material == SAND:
#
#                # --- try DOWN ---
#                below_material, _, _ = grid[y - 1, x]
#
#                if below_material == AIR:
#                    new[y, x] = (AIR, -1, texture)
#                    new[y - 1, x] = (SAND, obj_id, texture)
#                    continue
#
#                # --- try DIAGONALS ---
#                directions = [-1, 1]
#                random.shuffle(directions)
#
#                moved = False
#
#                for dx in directions:
#                    nx = x + dx
#                    if 0 <= nx < w:
#                        diag_material, _, _ = grid[y - 1, nx]
#
#                        if diag_material == AIR:
#                            new[y, x] = (AIR, -1, texture)
#                            new[y - 1, nx] = (SAND, obj_id, texture)
#                            moved = True
#                            break
#
#                # if not moved → stays in place
#
#    return new


def step(grid, player1, player2):
    """
    met à jour la position des wormz et met à jour la grille, retourne aussi si l'affichage a besoin d'être rafraichi avec : moved
    """

    # Initialisation de la détection de mouvement pour la boucle de rendu
    moved = False  # ← AJOUT

    # Gestion de la physique et des dégâts pour les unités du Joueur 1
    for worm in player1.wormz:
        if worm.is_supposed_to_fall(grid):
            moved = True
            worm.gravity(grid)
        elif grid[worm.y_pos][worm.x_pos][0] != 0:
            # Dégâts d'étouffement si le Worm est coincé dans un matériau solide
            worm.take_damage(0.75)
            worm.y_pos += 3
            if worm.health <= 0:
                player1.kill_worm(worm.worm_id)
                player2.money += 150


    # Gestion de la physique et des dégâts pour les unités du Joueur 2
    for worm in player2.wormz:
        if worm.is_supposed_to_fall(grid):
            moved = True
            worm.gravity(grid)
        elif grid[worm.y_pos][worm.x_pos][0] != 0:
            worm.take_damage(0.75)
            worm.y_pos += 3
            if worm.health <= 0:
                player2.kill_worm(worm.worm_id)
                player1.money += 150





    h, w = grid.shape[:2]
    new = grid.copy()


    # Parcours de la grille pour simuler la physique des particules (sable)
    for y in range(1, h):
        for x in range(w):

            material, obj_id, texture = grid[y, x]

            if material == SAND:

                below_material, _, _ = grid[y - 1, x]

                # Chute verticale si la cellule du dessous est vide
                if below_material == AIR:
                    new[y, x] = (AIR, -1, texture)
                    new[y - 1, x] = (SAND, obj_id, texture)
                    moved = True  # ← AJOUT
                    continue

                # Glissement diagonal aléatoire si la chute verticale est bloquée
                directions = [-1, 1]
                random.shuffle(directions)

                for dx in directions:
                    nx = x + dx
                    if 0 <= nx < w:
                        diag_material, _, _ = grid[y - 1, nx]

                        if diag_material == AIR:
                            new[y, x] = (AIR, -1, texture)
                            new[y - 1, nx] = (SAND, obj_id, texture)
                            moved = True  # ← AJOUT
                            break

    return new, moved  # ← SEUL changement de retour



def step_vectorized(grid, player1, player2, direction=None):
    """
    la fonction step, mais de facon completement vectorielle en utilisant une direction aléatoire pour tous les blocs au lieu de déplacer chaque bloc individuels de manière aléatoire
    """

    moved = False

    # =========================================================
    # 1. WORMS (unchanged - must stay sequential)
    # =========================================================
    for player, enemy in [(player1, player2), (player2, player1)]:
        for worm in player.wormz:

            if worm.is_supposed_to_fall(grid):
                worm.gravity(grid)
                moved = True

            elif grid[worm.y_pos, worm.x_pos, 0] != AIR:
                worm.take_damage(0.75)
                worm.y_pos += 3
                moved = True

                if worm.health <= 0:
                    player.kill_worm(worm.worm_id)
                    enemy.money += 150

    # =========================================================
    # 2. SAND (SAFE VECTOR VERSION)
    # =========================================================
    h, w = grid.shape[:2]
    new = grid.copy()

    material = grid[:, :, 0]
    sand = (material == SAND)
    air = (material == AIR)

    if direction is None:
        direction = random.choice([-1, 1])

    # =========================================================
    # 2.1 DOWN MOVEMENT (SAFE)
    # =========================================================
    can_fall = sand.copy()
    can_fall[1:, :] &= air[:-1, :]

    # IMPORTANT: write using full indexing (no chained indexing)
    fall_y, fall_x = np.where(can_fall)

    for y, x in zip(fall_y, fall_x):
        new[y, x, 0] = AIR
        new[y - 1, x, 0] = SAND
        new[y - 1, x, 1] = grid[y, x, 1]
        new[y - 1, x, 2] = grid[y, x, 2]

    moved |= can_fall.any()

    # update reference grid for next phase
    grid = new.copy()
    material = grid[:, :, 0]
    sand = (material == SAND)
    air = (material == AIR)

    # =========================================================
    # 2.2 DIAGONAL MOVEMENT (SAFE + GLOBAL DIRECTION)
    # =========================================================
    new2 = grid.copy()

    can_move = sand.copy()

    if direction == -1:
        # left
        can_move[1:, 1:] &= air[:-1, :-1]

        ys, xs = np.where(can_move)

        for y, x in zip(ys, xs):
            if (x-1 < 0) or (y-1 < 0):
                new2[y, x, 0] = SOLID
                continue
            new2[y, x, 0] = AIR
            new2[y - 1, x - 1, 0] = SAND
            new2[y - 1, x - 1, 1] = grid[y, x, 1]
            new2[y - 1, x - 1, 2] = grid[y, x, 2]

    else:
        # right
        can_move[1:, :-1] &= air[:-1, 1:]

        ys, xs = np.where(can_move)

        for y, x in zip(ys, xs):
            if (x+1 > w-1) or (y-1 < 0):
                new2[y, x, 0] = SOLID
                continue
            new2[y, x, 0] = AIR
            new2[y - 1, x + 1, 0] = SAND
            new2[y - 1, x + 1, 1] = grid[y, x, 1]
            new2[y - 1, x + 1, 2] = grid[y, x, 2]

    moved |= can_move.any()

    # =========================================================
    # 3. FINAL GRID
    # =========================================================
    grid = new2

    return grid, moved


def apply_object_cuts(grid):
    # Gère la rupture des ponts ou objets : transforme le solide en sable si la structure est coupée
    h, w = grid.shape[:2]

    objects = defaultdict(list)

    # Regroupement des cellules appartenant au même objet
    for y in range(h):
        for x in range(w):
            obj_id = grid[y, x, 1]
            if obj_id != 0:
                objects[obj_id].append((x, y))

    for obj_id, cells in objects.items():

        rows = defaultdict(list)
        for x, y in cells:
            rows[y].append(x)

        cut_y = None

        # Recherche d'une section horizontale entièrement détruite (sans SOLID)
        for y, xs in rows.items():
            for x in xs:
                if grid[y, x, 0] == SOLID:
                    break
            else:
                cut_y = y
                break

        if cut_y is None:
            continue

        # 🔥 Conversion en SABLE pour tout ce qui se trouve au-dessus de la coupure
        for x, y in cells:
            if y > cut_y and grid[y, x, 0] == SOLID:
                grid[y, x, 0] = SAND

    return grid
