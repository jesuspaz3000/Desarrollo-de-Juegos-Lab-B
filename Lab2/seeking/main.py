import pygame as pg

from random import randint, uniform

vec = pg.math.Vector2

WIDTH = 800
HEIGHT = 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
DARKGRAY = (40, 40, 40)

# Mob properties
MOB_SIZE = 32
MOB_SPEED = 5
MAX_SPEED = 5
MAX_FORCE = 0.1
APPROACH_RADIUS = 120

pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
clock = pg.time.Clock()
all_sprites = pg.sprite.Group()

class Mob(pg.sprite.Sprite):
    def __init__(self):
        self.groups = all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.Surface((MOB_SIZE, MOB_SIZE))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.pos = vec(randint(0, WIDTH), randint(0, HEIGHT))
        self.vel = vec(MAX_SPEED, 0).rotate(uniform(0, 360))
        self.acc = vec(0, 0)
        self.desired = vec(0, 0)
        self.rect.center = (int(self.pos.x), int(self.pos.y))  # Convertir Vector2 a tupla

    def follow_mouse(self):
        mouse_pos = pg.mouse.get_pos()
        self.acc = (vec(mouse_pos) - self.pos).normalize() * 0.5

    def seek(self, target):
        self.desired = (vec(target) - self.pos).normalize() * MAX_SPEED
        steer = (self.desired - self.vel)
        if steer.length() > MAX_FORCE:
            steer.scale_to_length(MAX_FORCE)
        return steer

    def seek_with_approach(self, target):
        self.desired = (vec(target) - self.pos)
        dist = self.desired.length()
        self.desired.normalize_ip()
        if dist < APPROACH_RADIUS:
            self.desired *= dist / APPROACH_RADIUS * MAX_SPEED
        else:
            self.desired *= MAX_SPEED
        steer = (self.desired - self.vel)
        if steer.length() > MAX_FORCE:
            steer.scale_to_length(MAX_FORCE)
        return steer

    def update(self):
        # self.follow_mouse()
        self.acc = self.seek_with_approach(pg.mouse.get_pos())
        # equations of motion
        self.vel += self.acc
        if self.vel.length() > MAX_SPEED:
            self.vel.scale_to_length(MAX_SPEED)
        self.pos += self.vel
        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH
        if self.pos.y > HEIGHT:
            self.pos.y = 0
        if self.pos.y < 0:
            self.pos.y = HEIGHT
        self.rect.center = (int(self.pos.x), int(self.pos.y))  # Convertir Vector2 a tupla

    def draw_vectors(self):
        scale = 25
        # vel
        pg.draw.line(screen, GREEN, (int(self.pos.x), int(self.pos.y)), 
                    (int(self.pos.x + self.vel.x * scale), int(self.pos.y + self.vel.y * scale)), 5)
        # desired
        pg.draw.line(screen, RED, (int(self.pos.x), int(self.pos.y)), 
                    (int(self.pos.x + self.desired.x * scale), int(self.pos.y + self.desired.y * scale)), 5)
        # approach radius
        pg.draw.circle(screen, WHITE, pg.mouse.get_pos(), APPROACH_RADIUS, 1)

Mob()
paused = False
show_vectors = False
running = True
while running:
    clock.tick(FPS)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                running = False
            if event.key == pg.K_SPACE:
                paused = not paused
            if event.key == pg.K_v:
                show_vectors = not show_vectors
            if event.key == pg.K_m:
                Mob()

    if not paused:
        all_sprites.update()
    pg.display.set_caption("{:.2f}".format(clock.get_fps()))
    screen.fill(DARKGRAY)
    all_sprites.draw(screen)
    if show_vectors:
        for sprite in all_sprites:
            sprite.draw_vectors()
    pg.display.flip()