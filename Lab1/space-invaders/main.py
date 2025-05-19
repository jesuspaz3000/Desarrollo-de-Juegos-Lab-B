import pygame
import math
import random
from pygame import mixer

# inicializacion de pygame
pygame.init()

# creacion de la pantalla
info = pygame.display.Info()
screen_width = info.current_w - 200
screen_height = info.current_h - 200
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)

# funcion para escalar una imagen y cubrir el area objetivo sin distorsion
def scale_image_to_fit(image, target_width, target_height):
    img_width, img_height = image.get_size()

    # Calcula las proporciones
    width_ratio = target_width / img_width
    height_ratio = target_height / img_height

    # Usa la mayor proporción para cubrir la pantalla
    scale_ratio = max(width_ratio, height_ratio)

    # Calcula las nuevas dimensiones
    new_width = int(img_width * scale_ratio)
    new_height = int(img_height * scale_ratio)

    # Escala la imagen
    scaled_image = pygame.transform.scale(image, (new_width, new_height))
    return scaled_image

# background
background_original = pygame.image.load('background.jpg')
background = scale_image_to_fit(background_original, screen_width, screen_height)

# sonido
mixer.music.load('background-music.mp3')
mixer.music.play(-1)

# titulo y icono
pygame.display.set_caption("Space Invaders")
icon = pygame.image.load('ufo.png')
pygame.display.set_icon(icon)

# jugador
playerImg_original = pygame.image.load('player.png')
playerImg = pygame.transform.scale(playerImg_original, (64, 64))
playerX = (screen_width - 64) // 2  # Centrar horizontalmente
playerY = screen_height - 100  # Posicionar en la parte inferior
playerX_change = 0
playerY_change = 0  # Nueva variable para el movimiento vertical
player_speed = 3  # Velocidad aumentada del jugador

# Diccionario para rastrear las teclas presionadas
keys_pressed = {"left": False, "right": False, "up": False, "down": False}

# enemigos
enemyImg = []
enemyX = []
enemyY = []
enemyX_change = []
enemyY_change = []
num_of_enemies = 6

for i in range(num_of_enemies):
    enemy_original = pygame.image.load('enemy.png')
    enemyImg.append(pygame.transform.scale(enemy_original, (64, 64)))
    enemyX.append(random.randint(0, screen_width - 64))
    enemyY.append(random.randint(50, 150))
    enemyX_change.append(1)
    enemyY_change.append(40)

# bala
bulletImg_original = pygame.image.load('bullet.png')
bulletImg = pygame.transform.scale(bulletImg_original, (32, 32))
bulletY_change = 10
bullets = []  # Lista para almacenar múltiples balas
bullet_cooldown = 0  # Contador para el tiempo entre disparos
bullet_cooldown_rate = 7  # Frames entre disparos (ajustar según necesidad)

def fire_bullet(x, y):
    bullets.append({"x": x + 16, "y": y, "active": True})
    # Crear nuevo sonido cada vez
    bullet_sound = mixer.Sound('laser-gun-shot.mp3')
    bullet_sound.set_volume(0.4)  # Reducir volumen del disparo
    bullet_sound.play()

# puntaje
score_value = 0
font = pygame.font.Font('freesansbold.ttf', 32)

textX = 10
testY = 10

# Game Over text
over_font = pygame.font.Font('freesansbold.ttf', 64)

def show_score(x, y):
    score = font.render("Score : " + str(score_value), True, (0, 255, 0))
    screen.blit(score, (x, y))

def game_over_text():
    over_text = over_font.render("GAME OVER", True, (0, 255, 0))
    text_rect = over_text.get_rect(center=(screen_width / 2, screen_height / 2))
    screen.blit(over_text, text_rect)

def player(x, y):
    screen.blit(playerImg, (x, y))

def enemy(x, y, i):
    screen.blit(enemyImg[i], (x, y))

def isCollision(enemyX, enemyY, bulletX, bulletY):
    distance = math.sqrt((math.pow(enemyX - bulletX, 2)) + (math.pow(enemyY - bulletY, 2)))
    if distance < 27:
        return True
    else:
        return False

# juego
running = True
clock = pygame.time.Clock()  # Añadir un reloj para controlar la velocidad del juego
while running:

    # RGB
    screen.fill((0, 0, 0))
    # fondo
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # manejo del cambio de tamaño de la ventana
        elif event.type == pygame.VIDEORESIZE:
            # Actualiza el tamaño de la pantalla
            screen_width, screen_height = event.size
            screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)

            # Vuelve a escalar todas las imagenes
            background = scale_image_to_fit(background_original, screen_width, screen_height)
            playerImg = pygame.transform.scale(playerImg_original,(64, 64))
            bulletImg = pygame.transform.scale(bulletImg_original, (32, 32))

            for i in range(num_of_enemies):
                enemyImg[i] = pygame.transform.scale(enemy_original, (64, 64))

        # teclas
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:  # Direccional izquierda o A
                keys_pressed["left"] = True
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:  # Direccional derecha o D
                keys_pressed["right"] = True
            if event.key == pygame.K_UP or event.key == pygame.K_w:  # Direccional arriba o W
                keys_pressed["up"] = True
            if event.key == pygame.K_DOWN or event.key == pygame.K_s:  # Direccional abajo o S
                keys_pressed["down"] = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                keys_pressed["left"] = False
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                keys_pressed["right"] = False
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                keys_pressed["up"] = False
            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                keys_pressed["down"] = False

    # Comprobar si se está presionando el espacio para disparar continuamente
    keys = pygame.key.get_pressed()
    
    # Reducir el cooldown si es mayor que cero
    if bullet_cooldown > 0:
        bullet_cooldown -= 1
    
    # Disparar si se presiona espacio y no hay cooldown
    if keys[pygame.K_SPACE] and bullet_cooldown == 0:
        fire_bullet(playerX, playerY)
        bullet_cooldown = bullet_cooldown_rate  # Establecer el tiempo hasta el próximo disparo
    
    # Actualizar el movimiento basado en las teclas presionadas
    playerX_change = 0
    playerY_change = 0
    
    if keys_pressed["left"]:
        playerX_change = -player_speed
    if keys_pressed["right"]:
        playerX_change = player_speed
    if keys_pressed["up"]:
        playerY_change = -player_speed
    if keys_pressed["down"]:
        playerY_change = player_speed

    # jugador
    playerX += playerX_change
    playerY += playerY_change

    # Límites horizontales
    if playerX <= 0:
        playerX = 0
    elif playerX >= screen_width - 64:
        playerX = screen_width - 64
    
    # Límites verticales
    if playerY <= 0:
        playerY = 0
    elif playerY >= screen_height - 64:
        playerY = screen_height - 64

    # Mostrar y mover balas
    for bullet in bullets[:]:
        # Mover la bala
        bullet["y"] -= bulletY_change
        
        # Mostrar la bala
        screen.blit(bulletImg, (bullet["x"], bullet["y"]))
        
        # Comprobar colisiones
        for i in range(num_of_enemies):
            if isCollision(enemyX[i], enemyY[i], bullet["x"], bullet["y"]):
                # Usar el mismo sonido de colisión que ya está funcionando
                collision_sound = mixer.Sound('large-explosion.mp3')
                collision_sound.set_volume(1.0)
                collision_sound.play()
                
                # Eliminar la bala
                if bullet in bullets:
                    bullets.remove(bullet)
                
                # Incrementar el puntaje
                score_value += 1
                
                # Reposicionar el enemigo
                enemyX[i] = random.randint(0, screen_width - 64)
                enemyY[i] = random.randint(50, 150)
                break
                
        # Eliminar la bala si sale de la pantalla
        if bullet["y"] < 0 and bullet in bullets:
            bullets.remove(bullet)

    # enemigos
    for i in range(num_of_enemies):

        # game over
        if enemyY[i] > playerY - 10:
            for j in range(num_of_enemies):
                enemyY[j] = 2000
            game_over_text()
            break

        enemyX[i] += enemyX_change[i]

        if enemyX[i] <= 0:
            enemyX_change[i] = 1
            enemyY[i] += enemyY_change[i]
        elif enemyX[i] >= screen_width - 64:
            enemyX_change[i] = -1
            enemyY[i] += enemyY_change[i]

        enemy(enemyX[i], enemyY[i], i)

    player(playerX, playerY)
    show_score(textX, testY)
    pygame.display.update()
    clock.tick(60)  # Limitar la velocidad del juego a 60 FPS