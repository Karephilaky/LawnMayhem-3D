import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random
from game.utils import load_obj, draw_model
from game.conejo import Conejo
from game.gnomo import Gnomo
from game.piedra import Piedra

class Particle:
    def __init__(self, x, y, z, color):
        self.color = color
        self.particles = [
            [x, y, z, random.uniform(-0.1, 0.1), random.uniform(0.05, 0.2), random.uniform(-0.1, 0.1), 30]
            for _ in range(20)
        ]

    def update(self):
        for p in self.particles:
            p[0] += p[3]
            p[1] += p[4]
            p[2] += p[5]
            p[4] -= 0.01
            p[6] -= 1
        self.particles = [p for p in self.particles if p[6] > 0]

    def draw(self):
        glColor3fv(self.color)
        glPointSize(4)
        glBegin(GL_POINTS)
        for p in self.particles:
            glVertex3f(p[0], p[1], p[2])
        glEnd()

def draw_health_bar(health, max_health, x, y, width, height):
    percent = max(0, health / max_health)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, 800, 0, 600, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glDisable(GL_DEPTH_TEST)
    glBegin(GL_QUADS)
    glColor3f(1, 0, 0)
    glVertex2f(x, y)
    glVertex2f(x + width, y)
    glVertex2f(x + width, y + height)
    glVertex2f(x, y + height)

    glColor3f(0, 1, 0)
    glVertex2f(x, y)
    glVertex2f(x + width * percent, y)
    glVertex2f(x + width * percent, y + height)
    glVertex2f(x, y + height)
    glEnd()
    glEnable(GL_DEPTH_TEST)

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_text(x, y, text, font, color=(255, 255, 255), bg_color=(0, 0, 0)):
    text_surface = font.render(text, True, color, bg_color)
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    width, height = text_surface.get_size()

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, 800, 0, 600, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glRasterPos2f(x, y)
    glDrawPixels(width, height, GL_RGBA, GL_UNSIGNED_BYTE, text_data)

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def generate_wave(z_pos):
    options = ["conejo", "gnomo", "piedra"]
    lanes = [-2, 0, 2]
    random.shuffle(lanes)

    conejos, gnomos, piedras = [], [], []

    for _ in range(3):
        obj_type = random.choice(options)
        options.remove(obj_type)
        lane = lanes.pop()
        if obj_type == "conejo":
            conejos.append(Conejo(lane, z_pos))
        elif obj_type == "gnomo":
            gnomos.append(Gnomo(lane, z_pos))
        elif obj_type == "piedra":
            piedras.append(Piedra(lane, z_pos))

    return conejos, gnomos, piedras

def main_loop():
    pygame.init()
    display = (800, 600)
    screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("LawnMayhem 3D")

    pygame.mixer.init()
    pygame.mixer.music.load("sound/C418 - Haggstrom - Minecraft Volume Alpha.mp3")
    pygame.mixer.music.play(-1)
    music_paused = False

    font = pygame.font.SysFont("Arial", 24)
    big_font = pygame.font.SysFont("Arial", 36)

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.0, 0.0, 0.0, 1.0)

    def set_3d_view():
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (display[0] / display[1]), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, -1.5, -5)

    grass_model = load_obj("models/grass.obj")
    conejo_model = load_obj("models/Bunny_lowpoly.obj")
    gnomo_model = load_obj("models/gnomo.obj")
    piedra_model = load_obj("models/cube.obj")
    player_model = load_obj("models/lawnmower.obj")

    clock = pygame.time.Clock()
    state = "menu"

    def render_menu():
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        draw_text(300, 400, "LawnMayhem 3D", big_font)
        draw_text(320, 300, "Presiona ENTER para Iniciar", font)
        draw_text(320, 260, "Presiona ESC para Salir", font)
        draw_text(320, 220, "Presiona M para Pausar/Reanudar Música", font)
        pygame.display.flip()

    def render_game_over(score):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        draw_text(310, 400, "GAME OVER", big_font)
        draw_text(300, 340, f"Puntaje final: {score}", font)
        draw_text(280, 280, "Presiona R para Reiniciar", font)
        draw_text(280, 240, "Presiona ESC para Salir", font)
        pygame.display.flip()

    def juego():
        nonlocal state
        player_x = 0
        score = 0
        speed = 2
        health = 100
        max_health = 100
        particles = []
        conejos, gnomos, piedras = [], [], []

        next_wave_z = -10
        move_cooldown = 0
        running = True

        while running:
            dt = clock.tick(60)
            now = pygame.time.get_ticks()

            for e in pygame.event.get():
                if e.type == QUIT:
                    running = False
                    state = "salir"
                elif e.type == KEYDOWN:
                    if e.key == K_m:
                        nonlocal music_paused
                        if music_paused:
                            pygame.mixer.music.unpause()
                            music_paused = False
                        else:
                            pygame.mixer.music.pause()
                            music_paused = True

            keys = pygame.key.get_pressed()
            if keys[K_LEFT] and player_x > -2 and now - move_cooldown > 120:
                player_x -= 2
                move_cooldown = now
            if keys[K_RIGHT] and player_x < 2 and now - move_cooldown > 120:
                player_x += 2
                move_cooldown = now

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            set_3d_view()

            if all(c.z > -30 for c in conejos + gnomos + piedras):
                wc, wg, wp = generate_wave(next_wave_z)
                conejos += wc
                gnomos += wg
                piedras += wp
                next_wave_z -= 6

            for c in conejos:
                c.update(speed)
                if c.check_collision(player_x):
                    score += 10
                    particles.append(Particle(c.x, 0.5, c.z, (1, 0, 0)))
            for g in gnomos:
                g.update(speed)
                if g.check_collision(player_x):
                    score -= 5
                    particles.append(Particle(g.x, 0.5, g.z, (1, 0.5, 1)))
            for p in piedras:
                p.update(speed)
                if p.check_collision(player_x):
                    health -= 10
                    particles.append(Particle(p.x, 0.5, p.z, (1, 1, 0)))

            conejos[:] = [c for c in conejos if c.z < 5]
            gnomos[:] = [g for g in gnomos if g.z < 5]
            piedras[:] = [p for p in piedras if p.z < 5]

            glPushMatrix()
            glTranslatef(0, 0, -40)
            glScalef(1, 1, 20)
            draw_model(*grass_model)
            glPopMatrix()

            for c in conejos:
                glPushMatrix()
                glTranslatef(c.x, 0.1, c.z)
                glRotatef(180, 0, 1, 0)
                glRotatef(-90, 1, 0, 0)
                glScalef(5, 5, 5)
                glDisable(GL_LIGHTING)
                glColor3f(1.0, 1.0, 1.0)  # Blanco fijo
                draw_model(*conejo_model)
                #glEnable(GL_LIGHTING)
                glPopMatrix()
            for g in gnomos:
                g.draw(gnomo_model)
            for p in piedras:
                p.draw(piedra_model)

            glPushMatrix()
            glTranslatef(player_x, 0, -1)
            glColor3f(1.0, 0.0, 0.0)
            draw_model(*player_model)
            glPopMatrix()

            for particle in particles[:]:
                particle.update()
                particle.draw()
                if not particle.particles:
                    particles.remove(particle)

            draw_health_bar(health, max_health, 20, 570, 200, 20)
            draw_text(600, 570, f"Puntos: {score}", big_font)

            if health <= 0:
                state = "game_over"
                return score

            pygame.display.flip()

    score_final = 0
    while state != "salir":
        if state == "menu":
            render_menu()
            for event in pygame.event.get():
                if event.type == QUIT:
                    state = "salir"
                elif event.type == KEYDOWN:
                    if event.key == K_RETURN:
                        state = "juego"
                    elif event.key == K_ESCAPE:
                        state = "salir"
                    elif event.key == K_m:
                        if music_paused:
                            pygame.mixer.music.unpause()
                            music_paused = False
                        else:
                            pygame.mixer.music.pause()
                            music_paused = True

        elif state == "juego":
            score_final = juego()

        elif state == "game_over":
            render_game_over(score_final)
            for event in pygame.event.get():
                if event.type == QUIT:
                    state = "salir"
                elif event.type == KEYDOWN:
                    if event.key == K_r:
                        state = "juego"
                    elif event.key == K_ESCAPE:
                        state = "salir"
                    elif event.key == K_m:
                        if music_paused:
                            pygame.mixer.music.unpause()
                            music_paused = False
                        else:
                            pygame.mixer.music.pause()
                            music_paused = True

    pygame.quit()

if __name__ == "__main__":
    main_loop()
