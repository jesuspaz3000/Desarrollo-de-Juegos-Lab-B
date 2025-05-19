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

# Colores
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)

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
background_original = pygame.image.load('assets/background.jpg')
background = scale_image_to_fit(background_original, screen_width, screen_height)

# sonido
mixer.music.load('assets/background-music.mp3')
mixer.music.play(-1)

# titulo y icono
pygame.display.set_caption("Space Invaders")
icon = pygame.image.load('assets/ufo.png')
pygame.display.set_icon(icon)

# jugador
playerImg_original = pygame.image.load('assets/player.png')
playerImg = pygame.transform.scale(playerImg_original, (64, 64))
playerX = (screen_width - 64) // 2  # Centrar horizontalmente
playerY = screen_height - 100  # Posicionar en la parte inferior
playerX_change = 0
playerY_change = 0  # Nueva variable para el movimiento vertical
player_speed = 3  # Velocidad aumentada del jugador
player_lives = 3  # Vidas iniciales del jugador
player_max_lives = 5  # Máximo de vidas que puede tener el jugador
player_is_hit = False  # Bandera para indicar si el jugador fue golpeado
player_invulnerable = False  # Estado de invulnerabilidad tras ser golpeado
invulnerable_timer = 0  # Contador para la invulnerabilidad
invulnerable_duration = 120  # Duración de la invulnerabilidad (en frames)
shield_value = 100  # Valor inicial del escudo

# Varias imágenes para mostrar vidas
life_img_original = pygame.image.load('assets/player.png')
life_img = pygame.transform.scale(life_img_original, (32, 32))

# Diccionario para rastrear las teclas presionadas
keys_pressed = {"left": False, "right": False, "up": False, "down": False}

# Variables para el control del mouse
use_mouse_control = False  # Flag para determinar si se está usando el mouse
mouse_visible = True       # Flag para controlar la visibilidad del cursor
mouse_clicked = False      # Flag para detectar cuando se hace clic por primera vez

# Power-ups
powerup_types = ["health", "shield", "rapid_fire", "triple_shot", "multi_direction"]
powerups = []
powerup_chance = 0.1  # Aumentado de 0.01 a 0.1 para mayor probabilidad
powerup_size = (48, 48)  # Aumentado de 32x32 a 48x48 para mejor visibilidad
powerup_speed = 2

# Estado de power-ups activos
rapid_fire_active = False
rapid_fire_timer = 0
rapid_fire_duration = 300  # 5 segundos a 60 FPS
triple_shot_active = False
triple_shot_timer = 0
triple_shot_duration = 300  # 5 segundos a 60 FPS
multi_direction_active = False
multi_direction_timer = 0
multi_direction_duration = 300  # 5 segundos a 60 FPS

# Cargar imágenes de power-ups
powerup_imgs = {
    "health": pygame.transform.scale(pygame.image.load('assets/health.png'), powerup_size),
    "shield": pygame.transform.scale(pygame.image.load('assets/shield.png'), powerup_size),
    "rapid_fire": pygame.transform.scale(pygame.image.load('assets/flash.png'), powerup_size),
    "triple_shot": pygame.transform.scale(pygame.image.load('assets/triple_shot.png'), powerup_size),
    "multi_direction": pygame.transform.scale(pygame.image.load('assets/plus.png'), powerup_size)
}

# enemigos
enemyImg = []
enemyX = []
enemyY = []
enemyX_change = []
enemyY_change = []
num_of_enemies = 6

for i in range(num_of_enemies):
    enemy_original = pygame.image.load('assets/enemy.png')
    enemyImg.append(pygame.transform.scale(enemy_original, (64, 64)))
    enemyX.append(random.randint(0, screen_width - 64))
    enemyY.append(random.randint(50, 150))
    enemyX_change.append(1)
    enemyY_change.append(40)

# bala
bulletImg_original = pygame.image.load('assets/bullet.png')
bulletImg = pygame.transform.scale(bulletImg_original, (32, 32))
bulletY_change = 10
bullets = []  # Lista para almacenar múltiples balas
bullet_cooldown = 0  # Contador para el tiempo entre disparos
bullet_cooldown_rate = 7  # Frames entre disparos (ajustar según necesidad)

# Balas enemigas
enemy_bullets = []
enemy_bulletImg = pygame.transform.scale(pygame.image.load('assets/flames.png'), (32, 32))
enemy_bullet_speed = 5
enemy_shooting_chance = 0.002  # Probabilidad de que un enemigo dispare en cada frame

def fire_bullet(x, y):
    bullets.append({"x": x + 16, "y": y, "active": True, "direction": "up"})
    
    # Triple disparo si está activo
    if triple_shot_active:
        bullets.append({"x": x, "y": y, "active": True, "direction": "up"})
        bullets.append({"x": x + 32, "y": y, "active": True, "direction": "up"})
    
    # Multi-dirección si está activo
    if multi_direction_active:
        bullets.append({"x": x + 16, "y": y, "active": True, "direction": "up-left"})
        bullets.append({"x": x + 16, "y": y, "active": True, "direction": "up-right"})
        if triple_shot_active:  # Si ambos power-ups están activos
            bullets.append({"x": x, "y": y, "active": True, "direction": "up-left"})
            bullets.append({"x": x, "y": y, "active": True, "direction": "up-right"})
            bullets.append({"x": x + 32, "y": y, "active": True, "direction": "up-left"})
            bullets.append({"x": x + 32, "y": y, "active": True, "direction": "up-right"})
    
    # Crear nuevo sonido cada vez
    bullet_sound = mixer.Sound('assets/laser-gun-shot.mp3')
    bullet_sound.set_volume(0.4)  # Reducir volumen del disparo
    bullet_sound.play()

def enemy_fire_bullet(x, y):
    enemy_bullets.append({"x": x + 16, "y": y + 32, "active": True})

def spawn_powerup(x, y, specific_type=None):
    powerup_type = specific_type if specific_type else random.choice(powerup_types)
    # Debug de asignación de imágenes
    print(f"Creando powerup de tipo: {powerup_type}")
    
    # Asegurarse de que el tipo multi_direction siempre use plus.png
    if powerup_type == "multi_direction":
        img = pygame.transform.scale(pygame.image.load('assets/plus.png'), powerup_size)
    else:
        img = powerup_imgs[powerup_type]
        
    powerups.append({
        "type": powerup_type,
        "x": x,
        "y": y,
        "img": img
    })

def reset_game():
    global player_lives, shield_value, score_value, enemyX, enemyY, game_over_state
    player_lives = 3
    shield_value = 100
    score_value = 0
    game_over_state = False
    
    # Reposicionar enemigos
    for i in range(num_of_enemies):
        enemyX[i] = random.randint(0, screen_width - 64)
        enemyY[i] = random.randint(50, 150)

def isCollision(enemyX, enemyY, bulletX, bulletY):
    distance = math.sqrt((math.pow(enemyX - bulletX, 2)) + (math.pow(enemyY - bulletY, 2)))
    if distance < 27:
        return True
    else:
        return False

# Estado del juego
game_over_state = False

# puntaje
score_value = 0
font = pygame.font.Font('freesansbold.ttf', 32)

textX = 10
testY = 10

# Game Over text
over_font = pygame.font.Font('freesansbold.ttf', 64)

def show_score(x, y):
    score = font.render("Score : " + str(score_value), True, GREEN)
    screen.blit(score, (x, y))

def show_lives(x, y):
    # Texto de vidas
    lives_text = font.render("Lives: ", True, WHITE)
    screen.blit(lives_text, (x, y))
    
    # Dibujar iconos de vidas
    for i in range(player_lives):
        screen.blit(life_img, (x + 100 + i * 40, y))

def show_shield_bar(x, y, shield):
    bar_width = 200
    bar_height = 20
    fill_width = (shield / 100) * bar_width
    
    # Texto primero
    shield_text = font.render("Shield:", True, WHITE)
    screen.blit(shield_text, (x, y))
    
    # Borde de la barra
    bar_x = x + 125  # Alineado con el texto de Lives
    bar_y = y + 5
    pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
    
    # Determinar color basado en el valor del escudo
    if shield > 70:
        bar_color = GREEN
    elif shield > 30:
        bar_color = YELLOW
    else:
        bar_color = RED
    
    # Barra de escudo
    pygame.draw.rect(screen, bar_color, (bar_x, bar_y, fill_width, bar_height))

def show_powerup_timers(x, y):
    position_y = y
    
    if rapid_fire_active:
        rf_time = font.render("Rapid Fire: {:.1f}s".format(rapid_fire_timer / 60), True, YELLOW)
        screen.blit(rf_time, (x, position_y))
        position_y += 40
    
    if triple_shot_active:
        ts_time = font.render("Triple Shot: {:.1f}s".format(triple_shot_timer / 60), True, BLUE)
        screen.blit(ts_time, (x, position_y))
        position_y += 40
    
    if multi_direction_active:
        md_time = font.render("Multi-Direction: {:.1f}s".format(multi_direction_timer / 60), True, GREEN)
        md_width = md_time.get_width()
        # Ajustar posición para que quepa en la pantalla
        if x + md_width > screen_width:
            x_adjusted = screen_width - md_width - 10
        else:
            x_adjusted = x
        screen.blit(md_time, (x_adjusted, position_y))

def game_over_text():
    over_text = over_font.render("GAME OVER", True, (0, 255, 0))
    text_rect = over_text.get_rect(center=(screen_width / 2, screen_height / 2))
    screen.blit(over_text, text_rect)
    
    # Añadir texto para reiniciar
    restart_text = font.render("Presiona R para reiniciar", True, WHITE)
    restart_rect = restart_text.get_rect(center=(screen_width / 2, screen_height / 2 + 70))
    screen.blit(restart_text, restart_rect)

def player(x, y):
    # Si el jugador está invulnerable, hacerlo parpadear
    if player_invulnerable and (pygame.time.get_ticks() % 200) < 100:
        # No dibujar nada (efecto parpadeo)
        pass
    else:
        screen.blit(playerImg, (x, y))

def enemy(x, y, i):
    screen.blit(enemyImg[i], (x, y))

# juego
running = True
clock = pygame.time.Clock()  # Añadir un reloj para controlar la velocidad del juego

# Spawn inicialmente solo un power-up multi-direction
spawn_powerup(screen_width // 2, 100, "multi_direction")

# También crear un power-up de cada tipo para pruebas completas
for i, tipo in enumerate(powerup_types):
    spawn_powerup(screen_width // 4 + i * 80, 200, tipo)

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
            # Reiniciar el juego con R si está en game over
            if event.key == pygame.K_r and game_over_state:
                reset_game()

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
    
    # Calcular cooldown basado en si el power-up de disparo rápido está activo
    current_cooldown_rate = bullet_cooldown_rate // 3 if rapid_fire_active else bullet_cooldown_rate

    # Procesar control por mouse
    mouse_pos = pygame.mouse.get_pos()
    mouse_buttons = pygame.mouse.get_pressed()

    # Detectar el primer clic para activar el control por mouse permanentemente
    if mouse_buttons[0] and not use_mouse_control:  # Si hace clic y el modo mouse no está activo
        # Verificar que el clic está dentro de la ventana del juego
        if 0 <= mouse_pos[0] <= screen_width and 0 <= mouse_pos[1] <= screen_height:
            # Ocultar el cursor y activar control por mouse permanentemente
            pygame.mouse.set_visible(False)
            use_mouse_control = True
            print("Control por mouse activado")
    
    # Si el modo mouse está activo, disparar cuando se hace clic
    if use_mouse_control and mouse_buttons[0] and bullet_cooldown == 0 and not game_over_state:
        fire_bullet(playerX, playerY)
        bullet_cooldown = current_cooldown_rate
    
    # Disparar si se presiona espacio y no hay cooldown
    if keys[pygame.K_SPACE] and bullet_cooldown == 0 and not game_over_state:
        fire_bullet(playerX, playerY)
        bullet_cooldown = current_cooldown_rate  # Establecer el tiempo hasta el próximo disparo
    
    # Actualizar timers de power-ups
    if rapid_fire_active:
        rapid_fire_timer -= 1
        if rapid_fire_timer <= 0:
            rapid_fire_active = False
    
    if triple_shot_active:
        triple_shot_timer -= 1
        if triple_shot_timer <= 0:
            triple_shot_active = False
            
    if multi_direction_active:
        multi_direction_timer -= 1
        if multi_direction_timer <= 0:
            multi_direction_active = False
    
    # Actualizar timer de invulnerabilidad
    if player_invulnerable:
        invulnerable_timer -= 1
        if invulnerable_timer <= 0:
            player_invulnerable = False
            
    # Actualizar el movimiento basado en las teclas presionadas
    playerX_change = 0
    playerY_change = 0

    # Si se está usando el mouse para control, mover hacia la posición del cursor
    if use_mouse_control and not game_over_state:
        # El jugador sigue exactamente la posición del mouse en ambos ejes (X e Y)
        # Se resta 32 para centrar el sprite del jugador en el cursor
        target_x = mouse_pos[0] - 32
        target_y = mouse_pos[1] - 32
        
        # Mover directamente a la posición del mouse (movimiento fluido)
        playerX = target_x
        playerY = target_y
        
        # No permitir que el jugador se salga de los límites
        if playerX < 0:
            playerX = 0
        elif playerX > screen_width - 64:
            playerX = screen_width - 64
            
        if playerY < 0:
            playerY = 0
        elif playerY > screen_height - 64:
            playerY = screen_height - 64
        
        # Anular los cambios de velocidad para usar posicionamiento directo
        playerX_change = 0
        playerY_change = 0
    else:
        # Control normal por teclado
        if keys_pressed["left"]:
            playerX_change = -player_speed
        if keys_pressed["right"]:
            playerX_change = player_speed
        if keys_pressed["up"]:
            playerY_change = -player_speed
        if keys_pressed["down"]:
            playerY_change = player_speed

    # Jugador
    if not game_over_state:
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
            
    # Si se presiona cualquier tecla de movimiento, desactivar el control por mouse
    if keys_pressed["left"] or keys_pressed["right"] or keys_pressed["up"] or keys_pressed["down"]:
        if use_mouse_control:  # Solo si el control por mouse está activo
            pygame.mouse.set_visible(True)
            use_mouse_control = False
            print("Control por teclado activado")
            
    # Mostrar y mover balas
    for bullet in bullets[:]:
        # Mover la bala según su dirección
        if bullet.get("direction") == "up":
            bullet["y"] -= bulletY_change
        elif bullet.get("direction") == "up-left":
            bullet["y"] -= bulletY_change * 0.7
            bullet["x"] -= bulletY_change * 0.7
        elif bullet.get("direction") == "up-right":
            bullet["y"] -= bulletY_change * 0.7
            bullet["x"] += bulletY_change * 0.7
        else:  # Por defecto, mover hacia arriba
            bullet["y"] -= bulletY_change
        
        # Mostrar la bala
        screen.blit(bulletImg, (bullet["x"], bullet["y"]))
        
        # Comprobar colisiones con enemigos
        for i in range(num_of_enemies):
            if isCollision(enemyX[i], enemyY[i], bullet["x"], bullet["y"]):
                # Usar el mismo sonido de colisión que ya está funcionando
                collision_sound = mixer.Sound('assets/large-explosion.mp3')
                collision_sound.set_volume(1.0)
                collision_sound.play()
                
                # Eliminar la bala
                if bullet in bullets:
                    bullets.remove(bullet)
                
                # Incrementar el puntaje
                score_value += 1
                
                # Posibilidad de generar power-up
                if random.random() < powerup_chance:
                    spawn_powerup(enemyX[i], enemyY[i])
                
                # Reposicionar el enemigo
                enemyX[i] = random.randint(0, screen_width - 64)
                enemyY[i] = random.randint(50, 150)
                break
                
        # Eliminar la bala si sale de la pantalla
        if bullet["y"] < 0 or bullet["x"] < 0 or bullet["x"] > screen_width:
            if bullet in bullets:
                bullets.remove(bullet)
                
    # Mostrar y mover balas enemigas
    for enemy_bullet in enemy_bullets[:]:
        # Mover la bala
        enemy_bullet["y"] += enemy_bullet_speed
        
        # Mostrar la bala
        screen.blit(enemy_bulletImg, (enemy_bullet["x"], enemy_bullet["y"]))
        
        # Comprobar colisión con el jugador
        if not player_invulnerable:
            bullet_player_distance = math.sqrt((math.pow(enemy_bullet["x"] - playerX, 2)) + 
                                             (math.pow(enemy_bullet["y"] - playerY, 2)))
            if bullet_player_distance < 32:
                # Jugador golpeado
                if shield_value > 0:
                    shield_value -= 15  # El escudo absorbe el daño
                else:
                    player_lives -= 1  # Pierde una vida si no tiene escudo
                
                # Hacer al jugador invulnerable por un tiempo
                player_invulnerable = True
                invulnerable_timer = invulnerable_duration
                
                # Eliminar la bala
                if enemy_bullet in enemy_bullets:
                    enemy_bullets.remove(enemy_bullet)
                    continue
        
        # Eliminar la bala si sale de la pantalla
        if enemy_bullet["y"] > screen_height:
            if enemy_bullet in enemy_bullets:
                enemy_bullets.remove(enemy_bullet)

    # Actualizar y mostrar power-ups
    for powerup in powerups[:]:
        # Mover el power-up hacia abajo
        powerup["y"] += powerup_speed
        
        # Mostrar el power-up
        screen.blit(powerup["img"], (powerup["x"], powerup["y"]))
        
        # Comprobar colisión con el jugador
        distance = math.sqrt((math.pow(playerX + 32 - powerup["x"], 2)) + (math.pow(playerY + 32 - powerup["y"], 2)))
        if distance < 40 and not game_over_state:
            # Aplicar efecto del power-up
            if powerup["type"] == "health":
                if player_lives < player_max_lives:
                    player_lives += 1
            elif powerup["type"] == "shield":
                shield_value = min(100, shield_value + 50)
            elif powerup["type"] == "rapid_fire":
                rapid_fire_active = True
                rapid_fire_timer = rapid_fire_duration
            elif powerup["type"] == "triple_shot":
                triple_shot_active = True
                triple_shot_timer = triple_shot_duration
            elif powerup["type"] == "multi_direction":
                multi_direction_active = True
                multi_direction_timer = multi_direction_duration
            
            # Eliminar el power-up
            powerups.remove(powerup)
            continue
        
        # Eliminar el power-up si sale de la pantalla
        if powerup["y"] > screen_height:
            powerups.remove(powerup)

    # enemigos
    for i in range(num_of_enemies):
        if not game_over_state:
            enemyX[i] += enemyX_change[i]

            if enemyX[i] <= 0:
                enemyX_change[i] = 1
                enemyY[i] += enemyY_change[i]
            elif enemyX[i] >= screen_width - 64:
                enemyX_change[i] = -1
                enemyY[i] += enemyY_change[i]
            
            # Posibilidad de que el enemigo dispare
            if random.random() < enemy_shooting_chance:
                enemy_fire_bullet(enemyX[i], enemyY[i])
            
            # Colisión enemigo-jugador
            if not player_invulnerable:
                enemy_player_distance = math.sqrt((math.pow(enemyX[i] - playerX, 2)) + (math.pow(enemyY[i] - playerY, 2)))
                if enemy_player_distance < 50:
                    # Jugador golpeado
                    if shield_value > 0:
                        shield_value -= 25  # El escudo absorbe el daño
                    else:
                        player_lives -= 1  # Pierde una vida si no tiene escudo
                    
                    # Hacer al jugador invulnerable por un tiempo
                    player_invulnerable = True
                    invulnerable_timer = invulnerable_duration
                    
                    # Reposicionar el enemigo
                    enemyX[i] = random.randint(0, screen_width - 64)
                    enemyY[i] = random.randint(50, 150)
            
            # Game over si se quedan sin vidas o los enemigos llegan al fondo de la pantalla
            if player_lives <= 0 or enemyY[i] > screen_height - 100:
                game_over_state = True
                break

        enemy(enemyX[i], enemyY[i], i)

    # Dibujar al jugador
    player(playerX, playerY)
    
    # Mostrar UI
    show_score(textX, testY)
    show_lives(textX, testY + 40)
    show_shield_bar(textX, testY + 80, shield_value)  # Movido debajo de las vidas
    show_powerup_timers(screen_width - 300, 10)
    
    # Mostrar pantalla de game over si es necesario
    if game_over_state:
        game_over_text()

    pygame.display.update()
    clock.tick(60)  # Limitar la velocidad del juego a 60 FPS