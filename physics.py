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
