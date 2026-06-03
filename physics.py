# Implémente la physique du jeu.


from collections import defaultdict
import numpy as np
import random

# Types de matériaux utilisés pour les collisions.
AIR = 0
SOLID = 1
SAND = 2



# def step(grid):
#    h, w = grid.shape[:2]
#    new = grid.copy()
#
#    # Parcours de bas en haut.
#    for y in range(1, h):
#        for x in range(w):
#
#            material, obj_id, texture = grid[y, x]
#
#            if material == SAND:
#
#                # Essaie d'abord de tomber verticalement.
#                below_material, _, _ = grid[y - 1, x]
#
#                if below_material == AIR:
#                    new[y, x] = (AIR, -1, texture)
#                    new[y - 1, x] = (SAND, obj_id, texture)
#                    continue
#
#                # Essaie ensuite de glisser en diagonale.
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
#                # Si aucun mouvement n'est possible, le grain reste en place.
#
#    return new


def step(grid, player1, player2):
    """
    Met à jour les wormz et le sable, puis indique si l'affichage doit être rafraîchi.
    """

    # Détection de mouvement utilisée par la boucle de rendu.
    moved = False

    # Physique et dégâts des unités du joueur 1.
    for worm in player1.wormz:
        if worm.is_supposed_to_fall(grid):
            moved = True
            worm.gravity(grid)
        elif grid[worm.y_pos][worm.x_pos][0] != 0:
            # Dégâts d'étouffement si le worm est coincé dans un matériau solide.
            worm.take_damage(0.75)
            worm.y_pos += 3
            if worm.health <= 0:
                player1.kill_worm(worm.worm_id)
                player2.money += 150


    # Physique et dégâts des unités du joueur 2.
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


    # Parcourt la grille pour simuler la physique des particules de sable.
    for y in range(1, h):
        for x in range(w):

            material, obj_id, texture = grid[y, x]

            if material == SAND:

                below_material, _, _ = grid[y - 1, x]

                # Chute verticale si la cellule du dessous est vide.
                if below_material == AIR:
                    new[y, x] = (AIR, -1, texture)
                    new[y - 1, x] = (SAND, obj_id, texture)
                    moved = True
                    continue

                # Glissement diagonal aléatoire si la chute verticale est bloquée.
                directions = [-1, 1]
                random.shuffle(directions)

                for dx in directions:
                    nx = x + dx
                    if 0 <= nx < w:
                        diag_material, _, _ = grid[y - 1, nx]

                        if diag_material == AIR:
                            new[y, x] = (AIR, -1, texture)
                            new[y - 1, nx] = (SAND, obj_id, texture)
                            moved = True
                            break

    return new, moved



def step_vectorized(grid, player1, player2, direction=None):
    """
    Version vectorisée de `step`.

    Une direction diagonale globale est choisie pour tous les grains de sable,
    au lieu d'un choix aléatoire indépendant pour chaque grain.
    """

    moved = False

    # =========================================================
    # 1. WORMS : traitement séquentiel nécessaire.
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
    # 2. SABLE : version vectorisée.
    # =========================================================
    h, w = grid.shape[:2]
    new = grid.copy()

    material = grid[:, :, 0]
    sand = (material == SAND)
    air = (material == AIR)

    if direction is None:
        direction = random.choice([-1, 1])

    # =========================================================
    # 2.1 Chute verticale.
    # =========================================================
    can_fall = sand.copy()
    can_fall[1:, :] &= air[:-1, :]

    # Utilise l'indexation complète pour éviter les effets de bord de l'indexation chaînée.
    fall_y, fall_x = np.where(can_fall)

    for y, x in zip(fall_y, fall_x):
        new[y, x, 0] = AIR
        new[y - 1, x, 0] = SAND
        new[y - 1, x, 1] = grid[y, x, 1]
        new[y - 1, x, 2] = grid[y, x, 2]

    moved |= can_fall.any()

    # Met à jour la grille de référence pour la phase suivante.
    grid = new.copy()
    material = grid[:, :, 0]
    sand = (material == SAND)
    air = (material == AIR)

    # =========================================================
    # 2.2 Glissement diagonal avec direction globale.
    # =========================================================
    new2 = grid.copy()

    can_move = sand.copy()

    if direction == -1:
        # Glissement à gauche.
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
        # Glissement à droite.
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
    # 3. Grille finale.
    # =========================================================
    grid = new2

    return grid, moved


def apply_object_cuts(grid):
    # Transforme en sable les parties d'un objet situées au-dessus d'une coupure.
    h, w = grid.shape[:2]

    objects = defaultdict(list)

    # Regroupe les cellules appartenant au même objet.
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

        # Cherche une section horizontale entièrement détruite, sans cellule SOLID.
        for y, xs in rows.items():
            for x in xs:
                if grid[y, x, 0] == SOLID:
                    break
            else:
                cut_y = y
                break

        if cut_y is None:
            continue

        # Convertit en SAND tout ce qui se trouve au-dessus de la coupure.
        for x, y in cells:
            if y > cut_y and grid[y, x, 0] == SOLID:
                grid[y, x, 0] = SAND

    return grid
