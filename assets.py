from abc import ABC, ABCMeta, abstractmethod

import numpy as np


class Player:
    def __init__(self, wormz=None, weapons=None, money=1000):
        """
        Initialise un joueur avec son argent, ses wormz et son inventaire d'armes.
        """

        if wormz is None:
            wormz = []

        if weapons is None:
            weapons = [[], []]  # 0 pour les missiles, 1 pour les strikes.

        self.wormz = wormz
        self.weapons = weapons
        self.money = money

    def kill_worm(self, worm_id):
        """
        Parcourt les wormz du joueur et supprime celui qui possède l'identifiant donné.
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
        Encode l'état du joueur dans un dictionnaire sérialisable en base de données.
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
        Reconstruit un joueur à partir des données précédemment produites par `to_dict`.
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
                Player.missile()  # On reconstruit l'objet, puis on écrase ses attributs.
                for m in data["weapons"][0]
            ],
            [Player.strike() for s in data["weapons"][1]],
        ]

        # Restaure les attributs des armes sauvegardées.
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
            Initialise un worm avec sa position, ses points de vie et ses paramètres de gameplay.
            """

            self.health = health  # Points de vie restants.
            self.worm_range = worm_range  # Distance maximale de visée des missiles.
            self.weight = weight  # Nombre minimal de blocs de soutien avant rupture.
            self.x_pos, self.y_pos = x_pos, y_pos
            self.worm_id = worm_id

        def take_damage(self, damage):
            """
            Retire les dégâts reçus aux points de vie du worm.
            """

            self.health -= damage

        def is_supposed_to_fall(self, GRID):
            """
            Vérifie si le worm doit tomber, sans modifier sa position.
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
            Applique la gravité au worm comme pour les grains de sable.
            """

            if GRID[self.y_pos - 1][self.x_pos][0] == 0:  # Air sous le worm.
                self.y_pos -= 1
            elif (0 < self.x_pos) and (self.x_pos < 192):
                if (
                    GRID[self.y_pos - 1][self.x_pos + 1][0] == 0
                ):  # Air en diagonale droite.
                    self.y_pos -= 1
                    self.x_pos += 1
                elif (
                    GRID[self.y_pos - 1][self.x_pos - 1][0] == 0
                ):  # Air en diagonale gauche.
                    self.y_pos -= 1
                    self.x_pos -= 1

    class Weapons(metaclass=ABCMeta):
        def __init__(
            self, radius_range=100, radius_explosion=5, radius_break=8, damage=3
        ):
            """
            Initialise une arme avec sa portée, ses rayons d'effet et ses dégâts.
            """

            self.radius_range = radius_range
            self.radius_explosion = radius_explosion
            self.radius_break = radius_break
            self.damage = damage

        @abstractmethod
        def launch_trajectory(self, x_target, y_target, x_pos, y_pos):
            """
            Définit la trajectoire que doit suivre l'arme.
            """
            pass

    class missile(Weapons):
        def __init__(self):
            super().__init__(
                radius_range=100, radius_explosion=5, radius_break=8, damage=3
            )

        def launch_trajectory(self, x_target, y_target, x_pos, y_pos):
            """
            Calcule une trajectoire quadratique entre la position de départ et la cible.
            """
            # Équation : y = -g/2 * (x - x_target) * (x - x_pos)
            # + ((y_target - y_pos) / (x_target - x_pos)) * (x - x_pos) + y_pos.
            X = np.linspace(x_pos, x_target, 50)  # 50 points.
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
            Calcule la trajectoire verticale d'un strike vers la cible.
            """

            # Trajectoire verticale.
            X = np.linspace(x_target, x_target, 50)  # 50 points.
            Y = np.linspace(y_target + 108, y_target, 50)
            return (X, Y)
