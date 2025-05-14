import pygame
import sys
import random

# Initialisation de Pygame
pygame.init()

# Dimensions de la fenêtre
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jeu de Plateforme Simple")

# Couleurs
BACKGROUND_COLOR = (135, 206, 235)
PLAYER_COLOR = (255, 100, 100)
PLAYER_BORDER = (0, 0, 0)
PLATFORM_COLOR = (50, 200, 50)

# Joueur
PLAYER_WIDTH, PLAYER_HEIGHT = 50, 60
PLAYER_SPEED = 4
JUMP_POWER = -12
GRAVITY = 0.5

# Plateformes
platforms = [
    pygame.Rect(150, 500, 200, 20),
    pygame.Rect(400, 400, 200, 20),
    pygame.Rect(100, 300, 150, 20),
    pygame.Rect(350, 200, 250, 20),
    pygame.Rect(200, 100, 150, 20),   # Nouvelle plateforme haute
    pygame.Rect(500, 50, 120, 20),    # Encore plus haut
    pygame.Rect(0, HEIGHT - 10, WIDTH, 10)  # Sol
]

# Timer plateforme
PLATFORM_TIME_LIMIT = 1300  # ms

# Joueur - état initial
player_x = WIDTH // 2 - PLAYER_WIDTH // 2
player_y = HEIGHT - PLAYER_HEIGHT - 10
player_vel_x = 0
player_vel_y = 0
on_ground = False
platform_timer = 0
current_platform_index = None  # Utiliser l'index de la plateforme

# Camera
camera_offset_y = 0
CAMERA_TARGET_Y = HEIGHT // 3

# Génération dynamique
PLATFORM_MIN_WIDTH = 80  # Plus petites plateformes
PLATFORM_MAX_WIDTH = 200
PLATFORM_HEIGHT = 20
MAX_JUMP_HEIGHT = max(150, int(-(JUMP_POWER ** 2) / (2 * GRAVITY)))  # Au moins 150 pixels de hauteur
PLATFORM_MIN_GAP_Y = 120  # Augmente l'écart vertical minimum
PLATFORM_MAX_GAP_Y = min(200, int(MAX_JUMP_HEIGHT * 0.9))  # Plus grand écart vertical
if PLATFORM_MAX_GAP_Y <= PLATFORM_MIN_GAP_Y:
    PLATFORM_MAX_GAP_Y = PLATFORM_MIN_GAP_Y + 30  # Assure un minimum de variation
max_platform_y = min(plat.y for plat in platforms if plat != platforms[-1])  # plus petite y hors sol

# Calcul de la portée de saut
jump_time = -2 * JUMP_POWER / GRAVITY
MAX_JUMP_DISTANCE = int(PLAYER_SPEED * jump_time * 0.9)  # 0.9 pour marge de sécurité

clock = pygame.time.Clock()
running = True

while running:
    dt = clock.tick(60)
    jump_request = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_SPACE, pygame.K_UP]:
                jump_request = True

    keys = pygame.key.get_pressed()
    player_vel_x = 0
    if keys[pygame.K_LEFT]:
        player_vel_x = -PLAYER_SPEED
    if keys[pygame.K_RIGHT]:
        player_vel_x = PLAYER_SPEED

    # Appliquer déplacement horizontal
    player_x += player_vel_x
    if player_x < 0:
        player_x = 0
    if player_x + PLAYER_WIDTH > WIDTH:
        player_x = WIDTH - PLAYER_WIDTH

    # Appliquer gravité
    player_vel_y += GRAVITY
    if player_vel_y > 20:
        player_vel_y = 20  # Limite la vitesse de chute
    player_y += player_vel_y

    # Détection de collision plateforme (par le dessous du joueur)
    on_ground = False
    new_platform_index = None
    for idx, plat in enumerate(platforms):
        if (player_y + PLAYER_HEIGHT > plat.y and
            player_y + PLAYER_HEIGHT - player_vel_y <= plat.y and
            player_x + PLAYER_WIDTH > plat.x and
            player_x < plat.x + plat.width and
            player_vel_y >= 0):
            player_y = plat.y - PLAYER_HEIGHT
            player_vel_y = 0
            on_ground = True
            new_platform_index = idx
            break
    sol_index = len(platforms) - 1

    # Timer plateforme : seulement si on est sur une plateforme autre que le sol
    if on_ground and new_platform_index is not None and new_platform_index != sol_index:
        if current_platform_index == new_platform_index:
            platform_timer += dt
        else:
            platform_timer = 0
            current_platform_index = new_platform_index
        if platform_timer > PLATFORM_TIME_LIMIT:
            on_ground = False
            player_y += 2  # Décale le joueur vers le bas pour sortir de la plateforme
            player_vel_y = 1
            platform_timer = 0
            current_platform_index = None
    elif on_ground and new_platform_index == sol_index:
        platform_timer = 0
        current_platform_index = sol_index
    else:
        platform_timer = 0
        current_platform_index = None

    # Saut
    if jump_request and on_ground:
        player_vel_y = JUMP_POWER
        on_ground = False
        platform_timer = 0
        current_platform_index = None

    # Limite bas de l'écran (sol)
    if player_y + PLAYER_HEIGHT > HEIGHT - 10:
        player_y = HEIGHT - 10 - PLAYER_HEIGHT
        player_vel_y = 0
        on_ground = True
        platform_timer = 0
        current_platform_index = sol_index

    # --- Camera ---
    if current_platform_index == sol_index:
        camera_offset_y = 0
    else:
        camera_offset_y = player_y - CAMERA_TARGET_Y
    # Limite la caméra pour que le sol reste en bas de l'écran
    max_camera_offset = platforms[-1].y - (HEIGHT - platforms[-1].height)
    if camera_offset_y > max_camera_offset:
        camera_offset_y = max_camera_offset

    # --- Génération dynamique de plateformes ---
    # On génère si le joueur s'approche à moins de 2 hauteurs d'écran du haut généré
    while player_y - 2 * HEIGHT < max_platform_y:
        plat_width = random.randint(PLATFORM_MIN_WIDTH, PLATFORM_MAX_WIDTH)
        # Récupère la plateforme la plus haute (hors sol)
        last_plat = platforms[-2]  # -1 = sol, -2 = dernière plateforme générée
        
        # Divise l'écran en trois zones
        zone_width = WIDTH // 3
        last_zone = last_plat.x // zone_width  # 0 = gauche, 1 = centre, 2 = droite
        
        # Force un changement de zone plus important
        available_zones = []
        if last_zone == 0:  # Si on était à gauche
            available_zones = [1, 2]  # Centre ou droite
        elif last_zone == 2:  # Si on était à droite
            available_zones = [0, 1]  # Gauche ou centre
        else:  # Si on était au centre
            available_zones = [0, 2]  # Force gauche ou droite
        
        new_zone = random.choice(available_zones)
        
        # Calcule la plage X dans la nouvelle zone avec marge
        zone_margin = zone_width // 4  # Marge pour éviter les bords de zone
        min_x = new_zone * zone_width + zone_margin
        max_x = (new_zone + 1) * zone_width - plat_width - zone_margin
        
        # Assure que la plateforme reste dans les limites de l'écran
        min_x = max(0, min_x)
        max_x = min(WIDTH - plat_width, max_x)
        
        # Si la plage est invalide à cause des marges, utilise la zone entière
        if min_x >= max_x:
            min_x = new_zone * zone_width
            max_x = (new_zone + 1) * zone_width - plat_width
            min_x = max(0, min_x)
            max_x = min(WIDTH - plat_width, max_x)
        
        plat_x = random.randint(min_x, max_x)
        
        # Vérifie si le saut est possible
        dx = abs(plat_x - (last_plat.x + last_plat.width // 2))
        if dx > MAX_JUMP_DISTANCE:
            # Si trop loin, rapproche la plateforme
            if plat_x > last_plat.x:
                plat_x = last_plat.x + MAX_JUMP_DISTANCE - plat_width // 2
            else:
                plat_x = last_plat.x - MAX_JUMP_DISTANCE + plat_width // 2
            plat_x = max(0, min(WIDTH - plat_width, plat_x))
        
        gap_y = random.randint(PLATFORM_MIN_GAP_Y, PLATFORM_MAX_GAP_Y)
        plat_y = max_platform_y - gap_y
        platforms.insert(-1, pygame.Rect(plat_x, plat_y, plat_width, PLATFORM_HEIGHT))
        max_platform_y = plat_y

    # Affichage
    screen.fill(BACKGROUND_COLOR)
    for plat in platforms:
        pygame.draw.rect(screen, PLATFORM_COLOR, pygame.Rect(
            plat.x, plat.y - camera_offset_y, plat.width, plat.height
        ))
    player_rect = pygame.Rect(player_x, player_y - camera_offset_y, PLAYER_WIDTH, PLAYER_HEIGHT)
    pygame.draw.rect(screen, PLAYER_BORDER, player_rect, 3)
    pygame.draw.rect(screen, PLAYER_COLOR, player_rect)
    pygame.display.flip()

pygame.quit()
sys.exit() 