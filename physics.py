# implémente la physique


from collections import defaultdict
import numpy as np
import random

AIR = 0
SOLID = 1
SAND = 2



def step(grid):
    h, w = grid.shape[:2]
    new = grid.copy()

    # bottom → top
    for y in range(1, h):
        for x in range(w):

            material, obj_id = grid[y, x]

            if material == SAND:

                # --- try DOWN ---
                below_material, _ = grid[y - 1, x]

                if below_material == AIR:
                    new[y, x] = (AIR, -1)
                    new[y - 1, x] = (SAND, obj_id)
                    continue

                # --- try DIAGONALS ---
                directions = [-1, 1]
                random.shuffle(directions)

                moved = False

                for dx in directions:
                    nx = x + dx
                    if 0 <= nx < w:
                        diag_material, _ = grid[y - 1, nx]

                        if diag_material == AIR:
                            new[y, x] = (AIR, -1)
                            new[y - 1, nx] = (SAND, obj_id)
                            moved = True
                            break

                # if not moved → stays in place

    return new


def apply_object_cuts(grid):
    h, w = grid.shape[:2]

    objects = defaultdict(list)

    # group cells by object_id
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

        # find a row with no SOLID
        for y, xs in rows.items():
            for x in xs:
                if grid[y, x, 0] == SOLID:
                    break
            else:
                cut_y = y
                break

        if cut_y is None:
            continue

        # 🔥 ONLY convert SOLID → SAND (prevents duplication)
        for x, y in cells:
            if y > cut_y and grid[y, x, 0] == SOLID:
                grid[y, x, 0] = SAND

    return grid
