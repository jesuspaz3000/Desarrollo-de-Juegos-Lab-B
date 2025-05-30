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
CYAN = (0, 255, 255)
DARKGRAY = (40, 40, 40)

# Mob properties
MOB_SIZE = 32
MAX_SPEED = 4
MAX_FORCE = 0.4
RAND_TARGET_TIME = 500
WANDER_RING_DISTANCE = 150
WANDER_RING_RADIUS = 50
WANDER_TYPE = 2

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
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        self.last_update = 0
        self.target = vec(randint(0, WIDTH), randint(0, HEIGHT))
        self.desired = vec(0, 0)
        self.displacement = vec(0, 0)

    def seek(self, target):
        self.desired = (target - self.pos).normalize() * MAX_SPEED
        steer = self.desired - self.vel
        if steer.length() > MAX_FORCE:
            steer.scale_to_length(MAX_FORCE)
        return steer

    def wander_improved(self):
        future = self.pos + self.vel.normalize() * WANDER_RING_DISTANCE
        target = future + vec(WANDER_RING_RADIUS, 0).rotate(uniform(0, 360))
        self.displacement = target
        return self.seek(target)

    def wander(self):
        # select random target every few sec
        now = pg.time.get_ticks()
        if now - self.last_update > RAND_TARGET_TIME:
            self.last_update = now
            self.target = vec(randint(0, WIDTH), randint(0, HEIGHT))
        return self.seek(self.target)

    def update(self):
        if WANDER_TYPE == 1:
            self.acc = self.wander()
        else:
            self.acc = self.wander_improved()
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
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def draw_vector(self):
        scale = 25
        # vel
        pg.draw.line(screen, GREEN, (int(self.pos.x), int(self.pos.y)), 
                     (int(self.pos.x + self.vel.x * scale), int(self.pos.y + self.vel.y * scale)), 5)
        # desired
        pg.draw.line(screen, RED, (int(self.pos.x), int(self.pos.y)), 
                     (int(self.pos.x + self.desired.x * scale), int(self.pos.y + self.desired.y * scale)), 5)
        # target
        if WANDER_TYPE == 1:
            pg.draw.circle(screen, CYAN, (int(self.target.x), int(self.target.y)), 8)
        else:
            center = self.pos + self.vel.normalize() * WANDER_RING_DISTANCE
            pg.draw.circle(screen, WHITE, (int(center.x), int(center.y)), WANDER_RING_RADIUS, 1)
            pg.draw.line(screen, CYAN, (int(center.x), int(center.y)), 
                         (int(self.displacement.x), int(self.displacement.y)), 5)

pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
clock = pg.time.Clock()

all_sprites = pg.sprite.Group()
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
            if event.key == pg.K_SPACE:
                running = False
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
            sprite.draw_vector()
    pg.display.flip()