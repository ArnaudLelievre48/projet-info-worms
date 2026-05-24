from abc import ABC, ABCMeta, abstractmethod

import numpy as np


class Player:
    def __init__(self, wormz=None, weapons=None, money=1000):
        """
        initialise la classe Player avec 1000 d'argent par défaut, et des listes / liste de liste vides pour wormz et weapons -> le remplissage de worm et weappons est géré dans main.py
        """

        if wormz is None:
            wormz = []

        if weapons is None:
            weapons = [[], []]  # 0 for missiles, 1 for strikes

        self.wormz = wormz
        self.weapons = weapons
        self.money = money

    def kill_worm(self, worm_id):
        """
        parcours la liste de worm du joueur, et supprime le worm d'id : worm_id
        """

        for i in range(len(self.wormz)):
            if self.wormz[i].worm_id == worm_id:
                self.wormz.pop(i)
                if len(self.wormz) == 0:
                    print("--------------------")
                    print("  GAME FINISHED !   ")
                    print("--------------------")
                    quit()
                return

    def to_dict(self):
        """
        encode dans un disctionnaire les informations du joueur afin d'écrire ces informations dans la DB
        """

        return {
            "money": self.money,
            "wormz": [
                {
                    "id": w.worm_id,
                    "x": w.x_pos,
                    "y": w.y_pos,
                    "health": w.health,
                    "worm_range": w.worm_range,
                    "weight": w.weight,
                }
                for w in self.wormz
            ],
            "weapons": [
                [
                    {
                        "radius_range": m.radius_range,
                        "radius_explosion": m.radius_explosion,
                        "radius_break": m.radius_break,
                        "damage": m.damage,
                    }
                    for m in self.weapons[0]
                ],
                [
                    {
                        "radius_range": s.radius_range,
                        "radius_explosion": s.radius_explosion,
                        "radius_break": s.radius_break,
                        "damage": s.damage,
                    }
                    for s in self.weapons[1]
                ],
            ],
        }

    @staticmethod
    def from_dict(data):
        """
        permet de créer les players en fonctions des données des joueurs récupérés depuis la DB (précédement encodés par : to_dict)
        """

        player = Player()

        player.money = data["money"]

        player.wormz = [
            Player.Worm(
                x_pos=w["x"],
                y_pos=w["y"],
                health=w["health"],
                worm_range=w["worm_range"],
                weight=w["weight"],
                worm_id=w["id"],
            )
            for w in data["wormz"]
        ]

        player.weapons = [
            [
                Player.missile()  # on reconstruit puis on écrase les attributs
                for m in data["weapons"][0]
            ],
            [Player.strike() for s in data["weapons"][1]],
        ]

        # remise des attributs weapons (important)
        for obj, saved in zip(player.weapons[0], data["weapons"][0]):
            obj.radius_range = saved["radius_range"]
            obj.radius_explosion = saved["radius_explosion"]
            obj.radius_break = saved["radius_break"]
            obj.damage = saved["damage"]

        for obj, saved in zip(player.weapons[1], data["weapons"][1]):
            obj.radius_range = saved["radius_range"]
            obj.radius_explosion = saved["radius_explosion"]
            obj.radius_break = saved["radius_break"]
            obj.damage = saved["damage"]

        return player

    class Worm:
        def __init__(self, x_pos, y_pos, health=3, worm_range=120, weight=5, worm_id=None):
            """
            initialise un worm avec 3 de vie, une position x et y, et un worm_id qui est par défaut None, les autres sont des features qui n'ont pas encore été pu être utilisées
            """

            self.health = health  # nombre de degats avant de mourrir
            self.worm_range = worm_range  # distance de missiles à viser
            self.weight = weight  # nombre de block min en dessous pour pas casser
            self.x_pos, self.y_pos = x_pos, y_pos
            self.worm_id = worm_id

        def take_damage(self, damage):
            """
            met à jour la vie du worm en lui enlevant à sa vie : damage
            """

            self.health -= damage

        def is_supposed_to_fall(self, GRID):
            """
            vérifie si le worm est censé tomber, ne le fait pas bouger pour autant
            """

            return (GRID[self.y_pos - 1][self.x_pos][0] == 0) or (
                ((0 < self.x_pos) and (self.x_pos < 129))
                and (
                    (GRID[self.y_pos - 1][self.x_pos + 1][0] == 0)
                    or (GRID[self.y_pos - 1][self.x_pos - 1][0] == 0)
                )
            )

        def gravity(self, GRID):
            """
            applique la gravité en changeant la position du worm de la meme manière que les grains de sable
            """

            if GRID[self.y_pos - 1][self.x_pos][0] == 0:  # si AIR en dessous
                self.y_pos -= 1
            elif (0 < self.x_pos) and (self.x_pos < 192):
                if (
                    GRID[self.y_pos - 1][self.x_pos + 1][0] == 0
                ):  # si AIR en diagonale gauche
                    self.y_pos -= 1
                    self.x_pos += 1
                elif (
                    GRID[self.y_pos - 1][self.x_pos - 1][0] == 0
                ):  # si AIR en diagonale droite
                    self.y_pos -= 1
                    self.x_pos -= 1

    class Weapons(metaclass=ABCMeta):
        def __init__(
            self, radius_range=100, radius_explosion=5, radius_break=8, damage=3
        ):
            """
            initialise un weapon avec un range, un radius_explosion; un radius_break et un quantité de damage
            """

            self.radius_range = radius_range
            self.radius_explosion = radius_explosion
            self.radius_break = radius_break
            self.damage = damage

        @abstractmethod
        def launch_trajectory(self, x_target, y_target, x_pos, y_pos):
            """
            méthode abstraite qui définie la trajectoire que doit effectuer le weapon (missile ou strike)
            """
            pass

    class missile(Weapons):
        def __init__(self):
            super().__init__(
                radius_range=100, radius_explosion=5, radius_break=8, damage=3
            )

        def launch_trajectory(self, x_target, y_target, x_pos, y_pos):
            """
            trajectoire quadratique entre x_target, y_target et x_pos, y_pos
            """
            # eq trajectory : y = -g/2 (x-x_target)*(x-x_pos) + ((y_target-y_pos)/(x_target - x_pos))*(x-x_pos) + y_pos
            X = np.linspace(x_pos, x_target, 50)  # 20 points
            if x_target == x_pos:
                Y = np.linspace(y_pos, y_target, 50)
            else:
                Y = (
                    -0.01 * (X - x_target) * (X - x_pos)
                    + ((y_target - y_pos) / (x_target - x_pos)) * (X - x_pos)
                    + y_pos
                )
            return (X, Y)

    class strike(Weapons):
        def __init__(self):
            super().__init__(
                radius_range=400, radius_explosion=5, radius_break=15, damage=2
            )

        def launch_trajectory(self, x_target, y_target, x_pos, y_pos):
            """
            trajectoire verticale pour les strike arrivant à x_target, y_target
            """

            # trajectoire verticale
            X = np.linspace(x_target, x_target, 50)  # 20 points
            Y = np.linspace(y_target + 108, y_target, 50)
            return (X, Y)
