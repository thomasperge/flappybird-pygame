import pygame
import sys

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
    pygame.Rect(0, HEIGHT - 10, WIDTH, 10)  # Sol
]

# Timer plateforme
PLATFORM_TIME_LIMIT = 1000  # ms

# Joueur - état initial
player_x = WIDTH // 2 - PLAYER_WIDTH // 2
player_y = HEIGHT - PLAYER_HEIGHT - 10
player_vel_x = 0
player_vel_y = 0
on_ground = False
platform_timer = 0

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

    # Déplacement horizontal
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
    landed_this_frame = False
    for plat in platforms:
        if (player_y + PLAYER_HEIGHT > plat.y and
            player_y + PLAYER_HEIGHT - player_vel_y <= plat.y and
            player_x + PLAYER_WIDTH > plat.x and
            player_x < plat.x + plat.width and
            player_vel_y >= 0):
            # Atterrissage sur la plateforme
            player_y = plat.y - PLAYER_HEIGHT
            player_vel_y = 0
            on_ground = True
            landed_this_frame = True
            break  # On ne gère qu'une plateforme à la fois

    # Timer plateforme
    if landed_this_frame:
        platform_timer = 0
    if on_ground:
        platform_timer += dt
        if platform_timer > PLATFORM_TIME_LIMIT:
            on_ground = False
            player_vel_y = 1
    else:
        platform_timer = 0

    # Saut
    if jump_request and on_ground:
        player_vel_y = JUMP_POWER
        on_ground = False
        platform_timer = 0

    # Limite bas de l'écran (sol)
    if player_y + PLAYER_HEIGHT > HEIGHT - 10:
        player_y = HEIGHT - 10 - PLAYER_HEIGHT
        player_vel_y = 0
        on_ground = True
        platform_timer = 0

    # Affichage
    screen.fill(BACKGROUND_COLOR)
    for plat in platforms:
        pygame.draw.rect(screen, PLATFORM_COLOR, plat)
    player_rect = pygame.Rect(player_x, player_y, PLAYER_WIDTH, PLAYER_HEIGHT)
    pygame.draw.rect(screen, PLAYER_BORDER, player_rect, 3)
    pygame.draw.rect(screen, PLAYER_COLOR, player_rect)
    pygame.display.flip()

pygame.quit()
sys.exit() 