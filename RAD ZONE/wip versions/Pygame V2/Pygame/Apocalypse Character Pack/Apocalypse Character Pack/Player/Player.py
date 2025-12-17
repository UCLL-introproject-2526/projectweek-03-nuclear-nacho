import pygame

pygame.init()

# ======================
# SCHERM
# ======================
SCREEN_W, SCREEN_H = 800, 600
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Camera Follow Player Demo")
clock = pygame.time.Clock()

# ======================
# INSTELLINGEN
# ======================
FRAME_W = 32
FRAME_H = 32
SCALE = 4
ANIM_FPS = 10
SPEED = 200

DIRECTIONS = ["front", "back", "right", "left"]

# ======================
# PAD
# ======================
PLAYER_PATH = r"C:\Users\woute\Desktop\Ucll\Pygame\Apocalypse Character Pack\Apocalypse Character Pack\Player"

# ======================
# FUNCTIE: ANIMATIES LADEN
# ======================
def load_animation(path, frames_per_row):
    sheet = pygame.image.load(path).convert_alpha()
    animations = {}

    for row, direction in enumerate(DIRECTIONS):
        frames = []
        for col in range(frames_per_row):
            frame = pygame.Surface((FRAME_W, FRAME_H), pygame.SRCALPHA)
            frame.blit(sheet, (0, 0),
                       (col * FRAME_W, row * FRAME_H, FRAME_W, FRAME_H))
            frame = pygame.transform.scale(
                frame, (FRAME_W * SCALE, FRAME_H * SCALE)
            )
            frames.append(frame)
        animations[direction] = frames

    return animations

# ======================
# ANIMATIES
# ======================
walk_animations  = load_animation(f"{PLAYER_PATH}\\walk.png", 3)
idle_animations  = load_animation(f"{PLAYER_PATH}\\idle.png", 1)
stab_animations  = load_animation(f"{PLAYER_PATH}\\stab.png", 3)
death_animations = load_animation(f"{PLAYER_PATH}\\Death.png", 4)

# ======================
# SPELER (WORLD POS)
# ======================
player_pos = pygame.Vector2(400, 300)
direction = "front"
state = "idle"
frame_index = 0.0

dead = False
paused = False
stabbing = False

# ======================
# CAMERA
# ======================
camera_offset = pygame.Vector2(0, 0)

# ======================
# WORLD OBJECT (MAP)
# ======================
death_block = pygame.Rect(300, 300, 60, 60)

# ======================
# FONTS
# ======================
font = pygame.font.SysFont(None, 72)
subfont = pygame.font.SysFont(None, 36)

# ======================
# GAME LOOP
# ======================
running = True
while running:
    dt = clock.tick(60) / 1000

    # ======================
    # EVENTS
    # ======================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                paused = not paused

            if dead and event.key == pygame.K_RETURN:
                dead = False
                state = "idle"
                frame_index = 0
                player_pos = pygame.Vector2(400, 300)

            if event.key == pygame.K_f and not dead and not paused and not stabbing:
                stabbing = True
                state = "stab"
                frame_index = 0

    # ======================
    # UPDATE PLAYER (WORLD)
    # ======================
    if not paused and not dead and not stabbing:
        keys = pygame.key.get_pressed()
        velocity = pygame.Vector2(0, 0)
        moving = False

        if keys[pygame.K_q] or keys[pygame.K_LEFT]:
            velocity.x -= SPEED
            direction = "left"
            moving = True
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            velocity.x += SPEED
            direction = "right"
            moving = True
        if keys[pygame.K_z] or keys[pygame.K_UP]:
            velocity.y -= SPEED
            direction = "back"
            moving = True
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            velocity.y += SPEED
            direction = "front"
            moving = True

        player_pos += velocity * dt
        state = "walk" if moving else "idle"

    # ======================
    # COLLISION (WORLD)
    # ======================
    player_rect = pygame.Rect(
        player_pos.x - FRAME_W * SCALE // 2,
        player_pos.y - FRAME_H * SCALE,
        FRAME_W * SCALE,
        FRAME_H * SCALE
    )

    if player_rect.colliderect(death_block):
        dead = True
        state = "death"
        frame_index = 0

    # ======================
    # CAMERA UPDATE
    # ======================
    camera_offset.x = player_pos.x - SCREEN_W // 2
    camera_offset.y = player_pos.y - SCREEN_H // 2

    # ======================
    # ANIMATIES
    # ======================
    if state == "walk":
        frames = walk_animations[direction]
        frame_index = (frame_index + ANIM_FPS * dt) % len(frames)

    elif state == "idle":
        frames = idle_animations[direction]
        frame_index = 0

    elif state == "stab":
        frames = stab_animations[direction]
        frame_index += ANIM_FPS * dt
        if frame_index >= len(frames):
            stabbing = False
            state = "idle"
            frame_index = 0

    elif state == "death":
        frames = death_animations["front"]
        frame_index = min(frame_index + ANIM_FPS * dt, len(frames) - 1)

    image = frames[int(frame_index)]

    # ======================
    # TEKENEN
    # ======================
    screen.fill((230, 230, 230))

    # Death block (WORLD → SCREEN)
    screen_block = pygame.Rect(
        death_block.x - camera_offset.x,
        death_block.y - camera_offset.y,
        death_block.width,
        death_block.height
    )
    pygame.draw.rect(screen, (255, 0, 0), screen_block)

    # Player (ALTIJD MIDDEN)
    screen.blit(
        image,
        (SCREEN_W // 2 - image.get_width() // 2,
         SCREEN_H // 2 - image.get_height())
    )

    # ======================
    # UI
    # ======================
    if paused:
        txt = font.render("PAUSED", True, (0, 0, 0))
        screen.blit(txt, (SCREEN_W//2 - txt.get_width()//2, SCREEN_H//2))

    if dead:
        txt = font.render("YOU DIED", True, (200, 0, 0))
        sub = subfont.render("Press ENTER to restart", True, (200, 0, 0))
        screen.blit(txt, (SCREEN_W//2 - txt.get_width()//2, SCREEN_H//2 - 40))
        screen.blit(sub, (SCREEN_W//2 - sub.get_width()//2, SCREEN_H//2 + 20))

    pygame.display.flip()

pygame.quit()
