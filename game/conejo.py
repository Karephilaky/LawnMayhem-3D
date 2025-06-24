from OpenGL.GL import *
from game.utils import draw_model

class Conejo:
    def __init__(self, x, z):
        self.x = x
        self.z = z
        self.alive = True

    def update(self, speed):
        self.z += speed

    def draw(self, model):
        if self.alive:
            glPushMatrix()
            glTranslatef(self.x, 0.5, self.z)
            glColor3f(1, 1, 1)  # blanco
            draw_model(*model)
            glPopMatrix()

    def check_collision(self, player_x, z_limit=-1, x_range=0.5):
        if self.alive and self.z >= z_limit:
            if abs(self.x - player_x) < x_range:
                self.alive = False
                return True
        return False
