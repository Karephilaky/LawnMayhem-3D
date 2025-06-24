from OpenGL.GL import *
from game.utils import draw_model

class Piedra:
    def __init__(self, x, z):
        self.x = x
        self.z = z
        self.hit = False

    def update(self, speed):
        self.z += speed

    def draw(self, model):
        if not self.hit:
            glPushMatrix()
            glTranslatef(self.x, 0.5, self.z)
            glColor3f(0.5, 0.5, 0.5)
            draw_model(*model)
            glPopMatrix()

    def check_collision(self, player_x, z_limit=-1, x_range=0.5):
        if not self.hit and self.z >= z_limit:
            if abs(self.x - player_x) < x_range:
                self.hit = True
                return True
        return False
