import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random
from game.utils import load_obj, draw_model
from game.conejo import Conejo
from game.gnomo import Gnomo
from game.piedra import Piedra

# -----------------------
# Config pantalla
# -----------------------
DISPLAY_W, DISPLAY_H = 800, 600

# -----------------------
# Utils 2D: paneles y texto con sombra/contorno
# -----------------------

def _push_2d():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, DISPLAY_W, 0, DISPLAY_H, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

def _pop_2d():
    glDisable(GL_BLEND)
    glEnable(GL_DEPTH_TEST)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_panel(x, y, w, h, alpha=0.35):
    _push_2d()
    glColor4f(0.0, 0.0, 0.0, alpha)
    glBegin(GL_QUADS)
    glVertex2f(x,   y)
    glVertex2f(x+w, y)
    glVertex2f(x+w, y+h)
    glVertex2f(x,   y+h)
    glEnd()
    _pop_2d()

def draw_text(x, y, text, font, color=(255,255,255), shadow=True, outline=True):
    surf = font.render(text, True, color).convert_alpha()
    w, h = surf.get_size()

    _push_2d()

    def blit_surface(s, px, py):
        data = pygame.image.tostring(s, "RGBA", True)
        glRasterPos2f(px, py)
        glDrawPixels(s.get_width(), s.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, data)

    if shadow:
        sh = font.render(text, True, (0, 0, 0)).convert_alpha()
        sh.set_alpha(140)
        blit_surface(sh, x+2, y-2)

    if outline:
        ol = font.render(text, True, (0, 0, 0)).convert_alpha()
        ol.set_alpha(200)
        for dx, dy in ((-1,0), (1,0), (0,-1), (0,1)):
            blit_surface(ol, x+dx, y+dy)

    blit_surface(surf, x, y)

    _pop_2d()
    return w, h

# -----------------------
# Partículas & Barra de vida
# -----------------------

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
    percent = max(0.0, min(1.0, health / max_health))
    _push_2d()
    glBegin(GL_QUADS)
    glColor4f(0.1, 0.05, 0.05, 0.9)
    glVertex2f(x, y)
    glVertex2f(x + width, y)
    glVertex2f(x + width, y + height)
    glVertex2f(x, y + height)
    glColor4f(0.0, 0.8, 0.2, 0.95)
    glVertex2f(x, y)
    glVertex2f(x + width * percent, y)
    glVertex2f(x + width * percent, y + height)
    glVertex2f(x, y + height)
    glEnd()
    _pop_2d()

# -----------------------
# Texturas: fondo y helpers
# -----------------------

def load_texture(path, repeat=False):
    surf = pygame.image.load(path).convert_alpha()
    img_data = pygame.image.tostring(surf, "RGBA", True)
    width, height = surf.get_size()

    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT if repeat else GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT if repeat else GL_CLAMP_TO_EDGE)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
                 GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    glBindTexture(GL_TEXTURE_2D, 0)
    return tex_id, (width, height)

def draw_background(tex_id):
    glDisable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex_id)

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, DISPLAY_W, 0, DISPLAY_H, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0); glVertex2f(0,            0)
    glTexCoord2f(1.0, 0.0); glVertex2f(DISPLAY_W,    0)
    glTexCoord2f(1.0, 1.0); glVertex2f(DISPLAY_W, DISPLAY_H)
    glTexCoord2f(0.0, 1.0); glVertex2f(0,         DISPLAY_H)
    glEnd()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    glBindTexture(GL_TEXTURE_2D, 0)
    glDisable(GL_TEXTURE_2D)
    glEnable(GL_DEPTH_TEST)

# --- UV auto para modelos sin UV (conejo) ---

def enable_auto_texgen():
    """Genera coordenadas de textura automáticamente (sphere map)."""
    glEnable(GL_TEXTURE_GEN_S)
    glEnable(GL_TEXTURE_GEN_T)
    glTexGeni(GL_S, GL_TEXTURE_GEN_MODE, GL_SPHERE_MAP)
    glTexGeni(GL_T, GL_TEXTURE_GEN_MODE, GL_SPHERE_MAP)

def disable_auto_texgen():
    glDisable(GL_TEXTURE_GEN_S)
    glDisable(GL_TEXTURE_GEN_T)

def draw_ground_textured(tex_id, width=6.0, depth=80.0, repeats_x=6.0, repeats_z=40.0):
    """Suelo plano texturizado desde z=+2 (delante de la cámara) hacia z negativo."""
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glColor3f(1.0, 1.0, 1.0)

    w = width / 2.0
    z_front = 2.0
    z_far = -depth

    glBegin(GL_QUADS)
    glTexCoord2f(0.0,        0.0);         glVertex3f(-w, 0.0,  z_front)
    glTexCoord2f(repeats_x,  0.0);         glVertex3f( w, 0.0,  z_front)
    glTexCoord2f(repeats_x,  repeats_z);   glVertex3f( w, 0.0,  z_far)
    glTexCoord2f(0.0,        repeats_z);   glVertex3f(-w, 0.0,  z_far)
    glEnd()

    glBindTexture(GL_TEXTURE_2D, 0)
    glDisable(GL_TEXTURE_2D)

# -----------------------
# Spawner
# -----------------------

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

# -----------------------
# Main
# -----------------------

def main_loop():
    pygame.init()
    display = (DISPLAY_W, DISPLAY_H)
    screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("LawnMayhem 3D")

    # Audio
    pygame.mixer.init()
    pygame.mixer.music.load("sound/C418 - Haggstrom - Minecraft Volume Alpha.mp3")
    pygame.mixer.music.play(-1)
    music_paused = False

    # Fuentes
    pygame.font.init()
    font = pygame.font.SysFont("Arial", 24)
    big_font = pygame.font.SysFont("Arial", 36)

    # OpenGL base
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.0, 0.0, 0.0, 1.0)

    def set_3d_view():
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (display[0] / display[1]), 0.1, 120.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, -1.3, -5)   # un poco más alto que -1.5

    # Modelos
    grass_model  = load_obj("models/grass.obj")
    conejo_model = load_obj("models/Bunny_lowpoly.obj")
    gnomo_model  = load_obj("models/gnomo.obj")
    piedra_model = load_obj("models/cube.obj")
    player_model = load_obj("models/lawnmower.obj")

    # Texturas
    sky_tex, _    = load_texture("textures/sky.png")
    grass_tex, _  = load_texture("textures/grass.png", repeat=True)
    rabbit_tex, _ = load_texture("textures/rabbit.png")

    clock = pygame.time.Clock()
    state = "menu"
    paused = False

    def render_menu():
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        draw_background(sky_tex)

        title = "LawnMayhem 3D"
        hint  = "ENTER: Iniciar   ESC: Salir   M: Música"

        tW, tH = big_font.size(title)
        hW, hH = font.size(hint)

        draw_panel((DISPLAY_W - (tW+40))//2, 400-5, tW+40, tH+20, alpha=0.35)
        draw_panel((DISPLAY_W - (hW+40))//2, 320-5, hW+40, hH+20, alpha=0.35)

        draw_text((DISPLAY_W - tW)//2, 400, title, big_font)
        draw_text((DISPLAY_W - hW)//2, 320, hint, font)

        pygame.display.flip()

    def render_game_over(score):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        draw_background(sky_tex)

        line1 = "GAME OVER"
        line2 = f"Puntaje final: {score}"
        line3 = "R: Reiniciar   ESC: Salir   M: Música"

        w1, h1 = big_font.size(line1)
        w2, h2 = font.size(line2)
        w3, h3 = font.size(line3)

        draw_panel((DISPLAY_W - (w1+60))//2, 420-5, w1+60, h1+20, 0.35)
        draw_panel((DISPLAY_W - (w2+60))//2, 360-5, w2+60, h2+20, 0.35)
        draw_panel((DISPLAY_W - (w3+60))//2, 300-5, w3+60, h3+20, 0.35)

        draw_text((DISPLAY_W - w1)//2, 420, line1, big_font)
        draw_text((DISPLAY_W - w2)//2, 360, line2, font)
        draw_text((DISPLAY_W - w3)//2, 300, line3, font)

        pygame.display.flip()

    def juego():
        nonlocal state, music_paused, paused
        player_x = 0
        score = 0
        base_speed = 2.0
        health = 100
        max_health = 100
        particles = []
        conejos, gnomos, piedras = [], [], []

        next_wave_z = -10
        move_cooldown = 0
        running = True

        while running:
            dt_ms = clock.tick(60)
            dt_scale = dt_ms / 16.6667
            now = pygame.time.get_ticks()

            for e in pygame.event.get():
                if e.type == QUIT:
                    running = False
                    state = "salir"
                elif e.type == KEYDOWN:
                    if e.key == K_m:
                        if music_paused:
                            pygame.mixer.music.unpause()
                            music_paused = False
                        else:
                            pygame.mixer.music.pause()
                            music_paused = True
                    elif e.key == K_p:
                        paused = not paused

            if paused:
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
                draw_background(sky_tex)

                txt1 = "PAUSA"
                txt2 = "P: Reanudar   ESC: Salir a menú"
                w1, h1 = big_font.size(txt1)
                w2, h2 = font.size(txt2)

                draw_panel((DISPLAY_W - (w1+60))//2, 330-5, w1+60, h1+20, 0.35)
                draw_panel((DISPLAY_W - (w2+60))//2, 280-5, w2+60, h2+20, 0.35)
                draw_text((DISPLAY_W - w1)//2, 330, txt1, big_font)
                draw_text((DISPLAY_W - w2)//2, 280, txt2, font)

                pygame.display.flip()

                for e in pygame.event.get():
                    if e.type == QUIT:
                        running = False
                        state = "salir"
                    elif e.type == KEYDOWN:
                        if e.key == K_p:
                            paused = False
                        elif e.key == K_ESCAPE:
                            running = False
                            state = "menu"
                continue

            keys = pygame.key.get_pressed()
            if keys[K_LEFT] and player_x > -2 and now - move_cooldown > 120:
                player_x -= 2
                move_cooldown = now
            if keys[K_RIGHT] and player_x < 2 and now - move_cooldown > 120:
                player_x += 2
                move_cooldown = now

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # Fondo 2D
            draw_background(sky_tex)

            # Escena 3D
            set_3d_view()

            # Spawner
            if all(c.z > -30 for c in conejos + gnomos + piedras):
                wc, wg, wp = generate_wave(next_wave_z)
                conejos += wc
                gnomos += wg
                piedras += wp
                next_wave_z -= 6

            speed = base_speed * dt_scale

            # Actualizar & colisiones
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

            # Suelo texturizado (más grande y un poco elevado)
            glPushMatrix()
            glTranslatef(0.0, -0.25, 0.0)
            draw_ground_textured(
                grass_tex,
                width=12.0,
                depth=140.0,
                repeats_x=12.0,
                repeats_z=70.0
            )
            glPopMatrix()

            # Conejos (textura con UV auto si no existen)
            for c in conejos:
                glPushMatrix()
                glTranslatef(c.x, 0.1, c.z)
                glRotatef(180, 0, 1, 0)
                glRotatef(-90, 1, 0, 0)
                glScalef(5, 5, 5)

                glEnable(GL_TEXTURE_2D)
                glBindTexture(GL_TEXTURE_2D, rabbit_tex)
                glColor3f(1.0, 1.0, 1.0)

                enable_auto_texgen()
                draw_model(*conejo_model)
                disable_auto_texgen()

                glBindTexture(GL_TEXTURE_2D, 0)
                glDisable(GL_TEXTURE_2D)
                glPopMatrix()

            # Otros
            for g in gnomos:
                g.draw(gnomo_model)
            for p in piedras:
                p.draw(piedra_model)

            # Jugador
            glPushMatrix()
            glTranslatef(player_x, 0, -1)
            glColor3f(1.0, 0.0, 0.0)
            draw_model(*player_model)
            glPopMatrix()

            # Partículas
            for particle in particles[:]:
                particle.update()
                particle.draw()
                if not particle.particles:
                    particles.remove(particle)

            # HUD
            draw_panel(14, 564, 212, 30, alpha=0.25)
            draw_health_bar(health, max_health, 20, 570, 200, 20)

            puntos_txt = f"Puntos: {score}"
            pw, ph = big_font.size(puntos_txt)
            draw_panel(DISPLAY_W - (pw+30) - 20, 560, pw+30, ph+16, alpha=0.25)
            draw_text(DISPLAY_W - (pw) - 28, 570, puntos_txt, big_font)

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
