import pygame
import math

pygame.init()

# ======================
# SCHERM
# ======================
SCREEN_W, SCREEN_H = 800, 600
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Apocalypse Player Demo")
clock = pygame.time.Clock()

# ======================
# INSTELLINGEN
# ======================
FRAME_W = 32
FRAME_H = 32
SCALE = 4
ANIM_FPS = 10
SPEED = 200
ARROW_SPEED = 500

# ======================
# PAD
# ======================
PLAYER_PATH = r"C:\Users\woute\Desktop\Ucll\Pygame\Apocalypse Character Pack\Apocalypse Character Pack\Player"

# ======================
# LOAD FUNCTIES
# ======================
def load_directional(path, frames_per_row):
    sheet = pygame.image.load(path).convert_alpha()
    animations = {}
    directions = ["front", "back", "right", "left"]
    for row, direction in enumerate(directions):
        frames = []
        for col in range(frames_per_row):
            frame = pygame.Surface((FRAME_W, FRAME_H), pygame.SRCALPHA)
            frame.blit(sheet, (0, 0),
                       (col * FRAME_W, row * FRAME_H, FRAME_W, FRAME_H))
            frame = pygame.transform.scale(frame, (FRAME_W * SCALE, FRAME_H * SCALE))
            frames.append(frame)
        animations[direction] = frames
    return animations

# ======================
# SPELER ANIMATIES
# ======================
walk_animations     = load_directional(f"{PLAYER_PATH}\\walk.png", 3)
idle_animations     = load_directional(f"{PLAYER_PATH}\\idle.png", 1)
death_animations    = load_directional(f"{PLAYER_PATH}\\Death.png", 4)
stab_animations     = load_directional(f"{PLAYER_PATH}\\stab.png", 3)
crossbow_animations = load_directional(f"{PLAYER_PATH}\\crossbow.png", 3)

# ======================
# ARROW IMAGE
# ======================
arrow_image = pygame.image.load(f"{PLAYER_PATH}\\arrow.png").convert_alpha()
arrow_image = arrow_image.subsurface((0, 0, FRAME_W, FRAME_H))
arrow_image = pygame.transform.scale(arrow_image, (FRAME_W*SCALE, FRAME_H*SCALE))

# ======================
# SPELER START
# ======================
player_pos = pygame.Vector2(SCREEN_W//2, SCREEN_H//2)
direction = "front"
state = "idle"
frame_index = 0.0
dead = False
paused = False
arrow_fired = False

# ======================
# DEATH BLOCK
# ======================
death_block = pygame.Rect(300, 300, 60, 60)

# ======================
# PIJL SPAWN OFFSET
# ======================
ARROW_OFFSET = pygame.Vector2(0, -20)

# ======================
# ARROW CLASS
# ======================
class Arrow:
    def __init__(self, start_pos, target_pos):
        self.pos = pygame.Vector2(start_pos)
        direction_vec = target_pos - start_pos

        if direction_vec.length() == 0:
            direction_vec = pygame.Vector2(0, -1)
        self.direction = direction_vec.normalize()
        self.velocity = self.direction * ARROW_SPEED

        # Bereken hoek voor sprite (wijst standaard omhoog)
        self.rotation = math.degrees(math.atan2(-self.direction.y, self.direction.x)) - 90
        self.image = pygame.transform.rotate(arrow_image, self.rotation)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, dt):
        self.pos += self.velocity * dt
        self.rect.center = self.pos

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

    def offscreen(self):
        return (
            self.pos.x < -100 or self.pos.x > SCREEN_W + 100 or
            self.pos.y < -100 or self.pos.y > SCREEN_H + 100
        )

arrows = []

# ======================
# FONTS
# ======================
font = pygame.font.SysFont(None, 72)
subfont = pygame.font.SysFont(None, 36)

# ======================
# HOOFDLOOP
# ======================
running = True
while running:
    dt = clock.tick(60)/1000

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
                player_pos = pygame.Vector2(SCREEN_W//2, SCREEN_H//2)
                arrows.clear()

            if event.key == pygame.K_f and not dead and state == "idle":
                state = "stab"
                frame_index = 0

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and not dead and state == "idle":
                state = "crossbow"
                frame_index = 0
                arrow_fired = False

    if not paused and not dead:
        # ======================
        # QZSD BEWEGING
        # ======================
        keys = pygame.key.get_pressed()
        vel = pygame.Vector2(0,0)
        moving = False
        if keys[pygame.K_q]:
            vel.x -= SPEED
            direction = "left"
            moving = True
        if keys[pygame.K_d]:
            vel.x += SPEED
            direction = "right"
            moving = True
        if keys[pygame.K_z]:
            vel.y -= SPEED
            direction = "back"
            moving = True
        if keys[pygame.K_s]:
            vel.y += SPEED
            direction = "front"
            moving = True

        if state in ("walk","idle"):
            player_pos += vel*dt
            state = "walk" if moving else "idle"

        # ======================
        # COLLISIE DEATH BLOCK
        # ======================
        player_rect = pygame.Rect(
            player_pos.x - FRAME_W*SCALE//2,
            player_pos.y - FRAME_H*SCALE,
            FRAME_W*SCALE,
            FRAME_H*SCALE
        )
        if player_rect.colliderect(death_block):
            dead = True
            state = "death"
            frame_index = 0

    # ======================
    # UPDATE PIJLEN
    # ======================
    for arrow in arrows[:]:
        arrow.update(dt)
        if arrow.offscreen():
            arrows.remove(arrow)

    # ======================
    # ANIMATIES
    # ======================
    if state == "walk":
        frames = walk_animations[direction]
        frame_index = (frame_index + ANIM_FPS*dt)%len(frames)
    elif state == "idle":
        frames = idle_animations[direction]
        frame_index = 0
    elif state == "stab":
        frames = stab_animations[direction]
        frame_index += ANIM_FPS*dt
        if frame_index >= len(frames):
            state = "idle"
            frame_index = 0
    elif state == "crossbow":
        frames = crossbow_animations[direction]
        frame_index += ANIM_FPS*dt
        # spawn arrow op frame 2
        if not arrow_fired and int(frame_index) == 2:
            mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
            spawn_pos = player_pos + ARROW_OFFSET
            arrows.append(Arrow(spawn_pos, mouse_pos))
            arrow_fired = True
        if frame_index >= len(frames):
            state = "idle"
            frame_index = 0
    elif state == "death":
        frames = death_animations["front"]
        frame_index = min(frame_index + ANIM_FPS*dt, len(frames)-1)

    image = frames[int(frame_index)]

    # ======================
    # TEKENEN
    # ======================
    screen.fill((230,230,230))
    pygame.draw.rect(screen,(255,0,0),death_block)
    for arrow in arrows:
        arrow.draw(screen)
    screen.blit(image,(player_pos.x-image.get_width()//2, player_pos.y-image.get_height()))

    if dead:
        txt = font.render("YOU DIED",True,(200,0,0))
        sub = subfont.render("Press ENTER to restart",True,(200,0,0))
        screen.blit(txt,(SCREEN_W//2-txt.get_width()//2,SCREEN_H//2-40))
        screen.blit(sub,(SCREEN_W//2-sub.get_width()//2,SCREEN_H//2+20))

    pygame.display.flip()

pygame.quit()
