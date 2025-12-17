import pygame
from sys import exit

# -------------------- INIT --------------------
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
clock = pygame.time.Clock()

SCREEN_W, SCREEN_H = screen.get_size()

# -------------------- HELPERS --------------------
def load_image(path, size=None, center=None):
    surf = pygame.image.load(path).convert_alpha()
    if size:
        surf = pygame.transform.scale(surf, size)
    rect = surf.get_rect()
    if center:
        rect.center = center
    return surf, rect


# -------------------- ASSETS --------------------
Map_surf, _ = load_image("Graphics/Game_building_test.png", size=(7680, 6400))

Char_surf, Char_rect = load_image(
    "Graphics/AChar.png",
    size=(150, 150),
    center=(SCREEN_W // 2, SCREEN_H //2)
)

Health_bar_surf, Health_bar_rect = load_image(
    "Graphics/Health_bar.png", size=(512, 58), center=(260, 30)
)
Stamina_bar_surf, Stamina_bar_rect = load_image(
    "Graphics/Stamina_bar.png", size=(512, 58), center=(260, 80)
)
Outline_bar_surf, _ = load_image(
    "Graphics/Outline_bar.png", size=(512, 58)
)

# Buildings (surface, world position)
buildings = [
    (load_image("Graphics/Building7.png", size=(400, 768))[0], pygame.Vector2(1722, 1068))

]

    # (load_image("Graphics/Building2.png", size=(700, 700))[0], pygame.Vector2(1950, 800)),
    # (load_image("Graphics/Building3.png", size=(700, 700))[0], pygame.Vector2(1250, 800)),
    # (load_image("Graphics/Building4.png", size=(700, 700))[0], pygame.Vector2(900, 800)),
    # (load_image("Graphics/Building5.png", size=(700, 700))[0], pygame.Vector2(550, 800)),
# -------------------- GAME STATE --------------------
camera_pos = pygame.Vector2(
    Map_surf.get_width() // 2 - Char_rect.centerx,
    Map_surf.get_height() // 2 - Char_rect.centery
)

BASE_SPEED = 1000
SPRINT_SPEED = 300

MAX_STAMINA = 100
stamina = MAX_STAMINA

STAMINA_DRAIN = 40
STAMINA_REGEN = 15

EXHAUST_AT = 0
RECOVER_AT = 20
exhausted = False

# -------------------- MINIMAP --------------------
MINIMAP_SIZE = 220
MINIMAP_ZOOM = 0.1

minimap_surf = pygame.Surface((MINIMAP_SIZE, MINIMAP_SIZE))
minimap_rect = minimap_surf.get_rect(topright=(SCREEN_W - 20, 20))

scaled_map = pygame.transform.smoothscale(
    Map_surf,
    (int(Map_surf.get_width() * MINIMAP_ZOOM),
     int(Map_surf.get_height() * MINIMAP_ZOOM))
)

scaled_buildings = [
    (
        pygame.transform.smoothscale(
            surf,
            (int(surf.get_width() * MINIMAP_ZOOM),
             int(surf.get_height() * MINIMAP_ZOOM))
        ),
        pos
    )
    for surf, pos in buildings
]

# -------------------- FUNCTIONS --------------------
def update_camera(camera, keys, speed, dt):
    if keys[pygame.K_z]:
        camera.y -= speed * dt
    if keys[pygame.K_s]:
        camera.y += speed * dt
    if keys[pygame.K_q]:
        camera.x -= speed * dt
    if keys[pygame.K_d]:
        camera.x += speed * dt


def update_stamina(stamina, exhausted, keys, dt):
    moving = keys[pygame.K_z] or keys[pygame.K_q] or keys[pygame.K_s] or keys[pygame.K_d]
    wants_sprint = keys[pygame.K_LSHIFT] and moving

    # Exhaustion logic
    if stamina <= EXHAUST_AT:
        exhausted = True
    elif stamina >= RECOVER_AT:
        exhausted = False

    # Drain / regen
    if wants_sprint and not exhausted:
        stamina -= STAMINA_DRAIN * dt
    else:
        stamina += STAMINA_REGEN * dt

    stamina = max(0, min(stamina, MAX_STAMINA))
    return stamina, exhausted


def draw_world(screen, camera):
    screen.blit(Map_surf, (-camera.x, -camera.y))
    for surf, pos in buildings:
        screen.blit(surf, pos - camera)


def draw_ui(screen, stamina, exhausted):
    ratio = max(0, min(stamina / MAX_STAMINA, 1))

    if ratio > 0:
        width = int(Stamina_bar_surf.get_width() * ratio)
        stamina_part = Stamina_bar_surf.subsurface(
            (0, 0, width, Stamina_bar_surf.get_height())
        )
        screen.blit(stamina_part, Stamina_bar_rect.topleft)

    screen.blit(Health_bar_surf, Health_bar_rect)
    screen.blit(Outline_bar_surf, Health_bar_rect)
    screen.blit(Outline_bar_surf, Stamina_bar_rect)

    # # Visual feedback when exhausted
    # if exhausted:
    #     pygame.draw.rect(
    #         screen,
    #         (255, 0, 0),
    #         Stamina_bar_rect.inflate(4, 4),
    #         2
    #     )


def draw_minimap(player_world_pos):
    minimap_surf.fill((0, 0, 0))

    player_mm = player_world_pos * MINIMAP_ZOOM
    offset = pygame.Vector2(
        MINIMAP_SIZE // 2 - player_mm.x,
        MINIMAP_SIZE // 2 - player_mm.y
    )

    minimap_surf.blit(scaled_map, offset)

    for surf, pos in scaled_buildings:
        minimap_surf.blit(surf, pos * MINIMAP_ZOOM + offset)

    pygame.draw.circle(
        minimap_surf,
        (0, 255, 0),
        (MINIMAP_SIZE // 2, MINIMAP_SIZE // 2),
        3
    )

    pygame.draw.rect(minimap_surf, (200, 200, 200), minimap_surf.get_rect(), 2)
    screen.blit(minimap_surf, minimap_rect)


# -------------------- MAIN LOOP --------------------
while True:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    keys = pygame.key.get_pressed()

    # Stamina & exhaustion
    stamina, exhausted = update_stamina(stamina, exhausted, keys, dt)

    # Speed logic
    if keys[pygame.K_LSHIFT] and not exhausted:
        speed = SPRINT_SPEED
    else:
        speed = BASE_SPEED

    # Camera movement
    update_camera(camera_pos, keys, speed, dt)

    # Draw
    screen.fill((0, 0, 0))

    draw_world(screen, camera_pos)
    screen.blit(Char_surf, Char_rect)

    draw_ui(screen, stamina, exhausted)

    player_world_pos = camera_pos + Char_rect.center
    draw_minimap(player_world_pos)

    pygame.display.flip()