from abc import ABC, ABCMeta

class Player(metaclass=ABCMeta):

    def __init__(self, wormz=None, money=1000):
        if wormz is None:
            wormz = []

        self.wormz = wormz
        self.money = money

    class worm:
        def __init__(self, x_pos, y_pos, health=3, range=100, weight=5):
            self.health = health # nombre de degats avant de mourrir
            self.range = range # distance de missiles à viser
            self.weight = weight # nombre de block min en dessous pour pas casser
            self.x_pos, self.y_pos = x_pos, y_pos

        def take_damage(self, damage):
            self.health -= damage

        def is_supposed_to_fall(self, GRID):
            return ( (GRID[self.y_pos-1][self.x_pos][0] == 0) or (( (0 < self.x_pos)  and (self.x_pos < 200) ) and ( (GRID[self.y_pos-1][self.x_pos+1][0] == 0) or (GRID[self.y_pos-1][self.x_pos-1][0] == 0) )) )

        def gravity(self, GRID):
            if GRID[self.y_pos-1][self.x_pos][0] == 0: # si AIR en dessous
                self.y_pos -= 1
            elif ( (0 < self.x_pos)  and (self.x_pos < 200) ):
                if GRID[self.y_pos-1][self.x_pos+1][0] == 0: # si AIR en diagonale gauche
                    self.y_pos -= 1
                    self.x_pos += 1
                elif GRID[self.y_pos-1][self.x_pos-1][0] == 0: # si AIR en diagonale droite
                    self.y_pos -= 1
                    self.x_pos -= 1


    class weapons:
        def __init__(self, radius_range=100, radius_explosion=10, radius_break=15, damage=1):
            self.radius_range = radius_range
            self.radius_explosion = radius_explosion
            self.radius_break = radius_break
            self.damage = damage

        def launch_trajectory(self, target_x, target_y, x_pos, y_pos):
            # eq trajectory : y = -g/2 (x-x_target)*(x-x_pos) + ((y_target-y_pos)/(x_target - x_pos))*(x-x_pos) + y_pos
            X = np.linspace(x_pos, x_target, 20) # 20 points
            Y = -4 * (X-x_target)*(X - x_pos) + ((y_target - y_pos)/(x_target - x_pos))*(X - x_pos) + y_pos
            return(X, Y)




