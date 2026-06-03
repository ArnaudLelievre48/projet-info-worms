# Ajoute des formes à la grille.

# Dimensions de la grille de jeu.
Nx, Ny = 192, 108

"""
Module de gestion des formes géométriques pour la grille de jeu.
"""

from abc import ABC, abstractmethod

class Shape(ABC):
    """
    Classe abstraite représentant une forme générique sur la grille.
    """
    def __init__(self, x0, y0, object_id=999, material=1, texture=1):
        """
        Initialise les paramètres communs à toutes les formes.
        """
        self.x0 = x0
        self.y0 = y0
        self.object_id = object_id
        self.material = material
        self.texture = texture

    @abstractmethod
    def draw(self, grid):
        """
        Méthode abstraite pour dessiner la forme sur la grille fournie.
        """
        pass


class Rectangle(Shape):
    """
    Forme rectangulaire dessinable sur la grille.
    """
    def __init__(self, x0, y0, dx, dy, object_id=999, material=1, texture=1):
        """
        Initialise un rectangle avec ses dimensions dx et dy.
        """
        super().__init__(x0, y0, object_id, material, texture)
        self.dx = dx
        self.dy = dy

    def draw(self, grid):
        """
        Modifie la grille pour dessiner un rectangle (matériau, id_objet, texture).
        """
        for x in range(self.dx):
            for y in range(self.dy):
                grid[y + self.y0][x + self.x0] = (self.material, self.object_id, self.texture)
        return grid


class Triangle(Shape):
    """
    Triangle isocèle dessinable sur la grille.
    """
    def __init__(self, x0, y0, dx, dy, object_id=999, material=1, texture=1):
        """
        Initialise un triangle isocèle de base dx et hauteur dy.
        Author: Amédée PICHARD
        """
        super().__init__(x0, y0, object_id, material, texture)
        self.dx = dx
        self.dy = dy

    def draw(self, grid):
        """
        Dessine un triangle isocèle en testant la position x par rapport à la largeur dx.
        """
        for x in range(self.dx):
            for y in range(self.dy):
                if x <= self.dx / 2:
                    if y <= (self.dy / (self.dx / 2)) * x:
                        grid[y + self.y0][x + self.x0] = (self.material, self.object_id, self.texture)
                else:
                    if y <= 2 * self.dy - (self.dy / (self.dx / 2)) * x:
                        grid[y + self.y0][x + self.x0] = (self.material, self.object_id, self.texture)
        return grid


class HCircle(Shape):
    """
    Demi-cercle dessinable sur la grille.
    """
    def __init__(self, x0, y0, r, object_id=999, material=1, texture=1):
        """
        Initialise un demi-cercle de rayon r.
        """
        super().__init__(x0, y0, object_id, material, texture)
        self.r = r

    def draw(self, grid):
        """
        Dessine un demi-cercle sur la grille.
        """
        for x in range(2 * self.r):
            for y in range(self.r):
                if y**2 + (x - self.r)**2 <= self.r**2:
                    grid[y + self.y0][x + self.x0 - self.r] = (self.material, self.object_id, self.texture)
        return grid




def transform(grid, x_0, y_0, radius, material):
    """
    Transforme les matériaux dans un rayon donné autour de `(x_0, y_0)`.

    Utilisé pour détruire une zone (SOLID vers AIR) ou fragiliser une structure
    (SOLID vers SAND).
    """
    # Fonction d'explosion : remplace les zones touchées par de l'air ou du sable.
    for x in range(Nx):
        for y in range(Ny):
            if ( (x - x_0)**2 + (y - y_0)**2 ) < ( radius**2) :
                if grid[y][x][0] != 0:
                    grid[y][x][0] = material
                    # grid[y][x][2] = material
                    if material == 0:
                        grid[y][x][1] = 0
    return grid
