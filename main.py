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
BONUS_PLATFORM_COLOR = (255, 223, 0)  # Jaune

# Joueur
PLAYER_WIDTH, PLAYER_HEIGHT = 50, 60
PLAYER_SPEED = 4
JUMP_POWER = -12
SUPER_JUMP_POWER = -20  # Super saut pour les plateformes bonus
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

# Plateformes bonus
bonus_platforms = []
BONUS_PLATFORM_CHANCE = 0.2  # 20% de chance de générer une plateforme bonus
BONUS_MIN_WIDTH = 60
BONUS_MAX_WIDTH = 100

# Timer plateforme
PLATFORM_TIME_LIMIT = 1300  # Temps en millisecondes avant de tomber d'une plateforme verte

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
MAX_JUMP_POWER = -28         # Puissance de saut max (plus négatif = plus haut)
MAX_SUPER_JUMP_POWER = -38   # Super saut max
MAX_PLATFORM_MIN_GAP_Y = 250 # Ecart vertical min max
MAX_PLATFORM_MAX_GAP_Y = 350 # Ecart vertical max max
MAX_JUMP_HEIGHT = max(150, int(-(JUMP_POWER ** 2) / (2 * GRAVITY)))  # Au moins 150 pixels de hauteur
PLATFORM_MIN_GAP_Y = 120  # Augmente l'écart vertical minimum
PLATFORM_MAX_GAP_Y = min(200, int(MAX_JUMP_HEIGHT * 0.9))  # Plus grand écart vertical
if PLATFORM_MAX_GAP_Y <= PLATFORM_MIN_GAP_Y:
    PLATFORM_MAX_GAP_Y = PLATFORM_MIN_GAP_Y + 30  # Assure un minimum de variation
max_platform_y = min(plat.y for plat in platforms if plat != platforms[-1])  # plus petite y hors sol

# Calcul de la portée de saut
jump_time = -2 * JUMP_POWER / GRAVITY
MAX_JUMP_DISTANCE = int(PLAYER_SPEED * jump_time * 0.9)  # 0.9 pour marge de sécurité

# Police pour affichage score et timer
FONT = pygame.font.SysFont('Arial', 28)

# Score et timer
score = 0
start_ticks = pygame.time.get_ticks()

clock = pygame.time.Clock()
running = True
highest_platform_index = 0  # Index de la plateforme la plus haute atteinte
death_message = None

dead = False  # Etat de mort

while running:
    dt = clock.tick(60)
    jump_request = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if dead:
            continue  # Ignore les autres entrées si mort
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_SPACE, pygame.K_UP]:
                jump_request = True

    if dead:
        # Affichage seulement, pas de physique ni de mouvement
        screen.fill(BACKGROUND_COLOR)
        for plat in platforms:
            pygame.draw.rect(screen, PLATFORM_COLOR, pygame.Rect(
                plat.x, plat.y - camera_offset_y, plat.width, plat.height
            ))
        for bonus_plat in bonus_platforms:
            pygame.draw.rect(screen, BONUS_PLATFORM_COLOR, pygame.Rect(
                bonus_plat.x, bonus_plat.y - camera_offset_y, bonus_plat.width, bonus_plat.height
            ))
        player_rect = pygame.Rect(player_x, player_y - camera_offset_y, PLAYER_WIDTH, PLAYER_HEIGHT)
        pygame.draw.rect(screen, PLAYER_BORDER, player_rect, 3)
        pygame.draw.rect(screen, PLAYER_COLOR, player_rect)
        score_text = FONT.render(f"Score : {score}", True, (0, 0, 0))
        timer_text = FONT.render(f"Temps : {elapsed_seconds}s", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))
        screen.blit(timer_text, (10, 40))
        # Affiche le message de mort
        death_message = FONT.render("Vous êtes mort !", True, (200, 0, 0))
        msg_rect = death_message.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(death_message, msg_rect)
        pygame.display.flip()
        continue

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

    # --- Difficulté évolutive selon la hauteur ---
    progress = max(0, -int(player_y) // 1000)  # 1 tous les 1000 pixels montés
    current_jump_power = JUMP_POWER - progress * 2
    current_super_jump_power = SUPER_JUMP_POWER - progress * 2
    current_min_gap_y = PLATFORM_MIN_GAP_Y + progress * 20
    current_max_gap_y = PLATFORM_MAX_GAP_Y + progress * 30
    # Limites sur la puissance de saut
    current_jump_power = max(current_jump_power, MAX_JUMP_POWER)
    current_super_jump_power = max(current_super_jump_power, MAX_SUPER_JUMP_POWER)
    # Limites sur l'écart vertical
    current_min_gap_y = min(current_min_gap_y, MAX_PLATFORM_MIN_GAP_Y)
    current_max_gap_y = min(current_max_gap_y, MAX_PLATFORM_MAX_GAP_Y)
    if current_max_gap_y < current_min_gap_y:
        current_max_gap_y = current_min_gap_y + 10

    # --- Génération dynamique de plateformes ---
    # On génère si le joueur s'approche à moins de 2 hauteurs d'écran du haut généré
    while player_y - 2 * HEIGHT < max_platform_y:
        if len(platforms) < 2:
            break
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
        
        gap_y = random.randint(current_min_gap_y, current_max_gap_y)
        plat_y = max_platform_y - gap_y
        platforms.insert(-1, pygame.Rect(plat_x, plat_y, plat_width, PLATFORM_HEIGHT))
        max_platform_y = plat_y

        # Génération possible d'une plateforme bonus
        if random.random() < BONUS_PLATFORM_CHANCE:
            bonus_width = random.randint(BONUS_MIN_WIDTH, BONUS_MAX_WIDTH)
            # Essaie de placer la plateforme bonus dans une zone libre
            attempts = 10  # Nombre maximum de tentatives
            while attempts > 0:
                # Choisis une zone différente de la plateforme normale
                bonus_zone = random.choice([i for i in range(3) if i != new_zone])
                bonus_x = random.randint(
                    bonus_zone * zone_width,
                    (bonus_zone + 1) * zone_width - bonus_width
                )
                # Vérifie qu'il n'y a pas de collision horizontale avec d'autres plateformes
                collision = False
                for p in platforms:
                    if (bonus_x < p.x + p.width and
                        bonus_x + bonus_width > p.x and
                        abs(plat_y - p.y) < PLATFORM_HEIGHT):
                        collision = True
                        break
                if not collision:
                    bonus_platforms.append(pygame.Rect(bonus_x, plat_y, bonus_width, PLATFORM_HEIGHT))
                    break
                attempts -= 1

    # Supprime les plateformes trop basses (plus de 20 en dessous de la plus haute atteinte)
    # On garde toujours le sol (dernière plateforme)
    min_index = max(0, highest_platform_index - 20)
    platforms = platforms[min_index:] + [platforms[-1]] if len(platforms) > 1 else platforms
    # Ajuste highest_platform_index après suppression
    if highest_platform_index >= 20:
        highest_platform_index = 20
    else:
        highest_platform_index = highest_platform_index
    # Supprime aussi les plateformes bonus trop basses
    if len(platforms) > 1:
        min_y = platforms[0].y
        bonus_platforms = [b for b in bonus_platforms if b.y <= min_y or b.y > min_y]

    # Détection de collision plateforme (par le dessous du joueur)
    on_ground = False
    new_platform_index = None
    is_bonus_jump = False
    
    # Vérification des plateformes normales
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
            # Met à jour la plateforme la plus haute atteinte (hors sol)
            if idx < len(platforms) - 1 and idx > highest_platform_index:
                highest_platform_index = idx
            break
    
    # Vérification des plateformes bonus
    if not on_ground:
        for bonus_plat in bonus_platforms:
            if (player_y + PLAYER_HEIGHT > bonus_plat.y and
                player_y + PLAYER_HEIGHT - player_vel_y <= bonus_plat.y and
                player_x + PLAYER_WIDTH > bonus_plat.x and
                player_x < bonus_plat.x + bonus_plat.width and
                player_vel_y >= 0):
                player_y = bonus_plat.y - PLAYER_HEIGHT
                player_vel_y = 0
                on_ground = True
                is_bonus_jump = True
                break

    sol_index = len(platforms) - 1

    # Timer plateforme : seulement si on est sur une plateforme verte autre que le sol
    if on_ground and new_platform_index is not None and new_platform_index != sol_index and not is_bonus_jump:
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
        player_vel_y = current_super_jump_power if is_bonus_jump else current_jump_power
        on_ground = False
        platform_timer = 0
        current_platform_index = None

    # Limite bas de l'écran (sol)
    if player_y + PLAYER_HEIGHT > HEIGHT - 10:
        player_y = HEIGHT - 10 - PLAYER_HEIGHT
        player_vel_y = 0
        on_ground = True
        platform_timer = 0
        current_platform_index = len(platforms) - 1

    # --- Camera ---
    if current_platform_index == len(platforms) - 1:
        camera_offset_y = 0
    else:
        camera_offset_y = player_y - CAMERA_TARGET_Y
    # Limite la caméra pour que le sol reste en bas de l'écran
    max_camera_offset = platforms[-1].y - (HEIGHT - platforms[-1].height)
    if camera_offset_y > max_camera_offset:
        camera_offset_y = max_camera_offset

    # --- Score ---
    # Le score est la hauteur maximale atteinte depuis le sol, divisé par 20 pour ralentir la progression
    score = max(score, int((HEIGHT - player_y) // 20))
    elapsed_seconds = (pygame.time.get_ticks() - start_ticks) // 1000

    # --- Mort si le joueur tombe trop bas ---
    # Si le joueur tombe sous la dernière plateforme restante (hors sol), il meurt
    if len(platforms) > 1:
        lowest_platform_y = platforms[0].y
        if player_y > lowest_platform_y + 100:  # Marge de 100 pixels
            dead = True
            continue  # Passe directement à l'affichage de mort

    # Affichage
    screen.fill(BACKGROUND_COLOR)
    # Dessine les plateformes normales
    for plat in platforms:
        pygame.draw.rect(screen, PLATFORM_COLOR, pygame.Rect(
            plat.x, plat.y - camera_offset_y, plat.width, plat.height
        ))
    # Dessine les plateformes bonus
    for bonus_plat in bonus_platforms:
        pygame.draw.rect(screen, BONUS_PLATFORM_COLOR, pygame.Rect(
            bonus_plat.x, bonus_plat.y - camera_offset_y, bonus_plat.width, bonus_plat.height
        ))
    player_rect = pygame.Rect(player_x, player_y - camera_offset_y, PLAYER_WIDTH, PLAYER_HEIGHT)
    pygame.draw.rect(screen, PLAYER_BORDER, player_rect, 3)
    pygame.draw.rect(screen, PLAYER_COLOR, player_rect)

    # Affichage du score et du timer
    score_text = FONT.render(f"Score : {score}", True, (0, 0, 0))
    timer_text = FONT.render(f"Temps : {elapsed_seconds}s", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))
    screen.blit(timer_text, (10, 40))

    pygame.display.flip()

pygame.quit()
sys.exit() 