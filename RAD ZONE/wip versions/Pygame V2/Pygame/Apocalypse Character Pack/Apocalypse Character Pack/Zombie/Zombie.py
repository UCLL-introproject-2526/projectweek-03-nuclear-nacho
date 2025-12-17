import pygame
import random

pygame.init()

# ======================
# SCHERM
# ======================
SCREEN_W, SCREEN_H = 800, 600
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Zombie Demo - Fixed Animations!")
clock = pygame.time.Clock()

# ======================
# INSTELLINGEN
# ======================
FRAME_W = 32
FRAME_H = 32
SCALE = 4
ANIM_FPS = 8  # Iets sneller voor smooth
ZOMBIE_SPEED = 100
ZOMBIE_HEALTH = 100
PLAYER_SPEED = 200
PLAYER_SIZE = 40

# ======================
# FUNCTIE: MULTI-DIRECTION ANIMATIE LADEN (4 rows: front/back/right/left)
# ======================
def load_sheet_anim(path, num_frames_per_dir):
    sheet = pygame.image.load(path).convert_alpha()
    # Print sheet size voor debug (verwijder later)
    print(f"{path}: {sheet.get_width()}x{sheet.get_height()} -> {num_frames_per_dir} frames/dir")
    directions = ["front", "back", "right", "left"]
    anims = {}
    for row, dir_name in enumerate(directions):
        frames = []
        for col in range(num_frames_per_dir):
            surf = pygame.Surface((FRAME_W, FRAME_H), pygame.SRCALPHA)
            src_rect = pygame.Rect(col * FRAME_W, row * FRAME_H, FRAME_W, FRAME_H)
            surf.blit(sheet, (0, 0), src_rect)
            surf = pygame.transform.scale(surf, (FRAME_W * SCALE, FRAME_H * SCALE))
            frames.append(surf)
        anims[dir_name] = frames
    return anims

# ======================
# ZOMBIE PATH
# ======================
ZOMBIE_PATH = r"C:\Users\woute\Desktop\Ucll\Pygame\Apocalypse Character Pack\Apocalypse Character Pack\Zombie"

# ======================
# ZOMBIE CLASS
# ======================
class Zombie:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.health = ZOMBIE_HEALTH
        self.state = "idle"
        self.direction = "front"
        self.frame_index = 0.0
        self.alive = True

        # Laad alle animaties (4 directions elk)
        self.animations = {}
        self.animations["idle"] = load_sheet_anim(f"{ZOMBIE_PATH}\\Idle.png", 6)
        self.animations["walk"] = load_sheet_anim(f"{ZOMBIE_PATH}\\Walk.png", 6)
        self.animations["attack"] = load_sheet_anim(f"{ZOMBIE_PATH}\\Attack.png", 4)
        self.animations["death"] = load_sheet_anim(f"{ZOMBIE_PATH}\\Death.png", 4)

    def choose_direction(self, player_pos):
        dir_vec = player_pos - self.pos
        if dir_vec.length() == 0:
            return "front"
        if abs(dir_vec.x) > abs(dir_vec.y):
            return "right" if dir_vec.x > 0 else "left"
        else:
            return "front" if dir_vec.y > 0 else "back"  # y>0 = player onder zombie = front/down

    def update(self, dt, player_pos):
        # Altijd direction updaten (ook voor death)
        self.direction = self.choose_direction(player_pos)

        # Health check
        if self.health <= 0:
            self.alive = False

        if not self.alive:
            self.state = "death"
            frames = self.animations["death"][self.direction]
            self.frame_index += ANIM_FPS * dt
            if self.frame_index >= len(frames):
                self.frame_index = len(frames) - 1
            self.image = frames[int(self.frame_index)]
            return

        # Leef: state bepalen
        dir_vec = player_pos - self.pos
        distance = dir_vec.length()

        if distance <= 50:
            self.state = "attack"
        elif distance > 10:
            self.state = "walk"
            dir_vec.normalize_ip()
            self.pos += dir_vec * ZOMBIE_SPEED * dt
        else:
            self.state = "idle"

        # Frames voor state + direction
        frames = self.animations[self.state][self.direction]

        self.frame_index += ANIM_FPS * dt
        self.frame_index %= len(frames)  # Loop voor alle behalve death

        self.image = frames[int(self.frame_index)]

    def draw(self, screen):
        # Teken zombie gecentreerd
        screen.blit(self.image, (self.pos.x - self.image.get_width() // 2,
                                 self.pos.y - self.image.get_height() // 2))
        # Health bar (alleen als nog health >0)
        if self.health > 0:
            bar_width = FRAME_W * SCALE
            bar_height = 8
            health_ratio = self.health / ZOMBIE_HEALTH
            bar_y = self.pos.y - self.image.get_height() // 2 - 15
            bg_rect = pygame.Rect(self.pos.x - bar_width // 2, bar_y, bar_width, bar_height)
            fg_rect = pygame.Rect(self.pos.x - bar_width // 2, bar_y, bar_width * health_ratio, bar_height)
            pygame.draw.rect(screen, (100, 0, 0), bg_rect)
            pygame.draw.rect(screen, (0, 200, 0), fg_rect)
            pygame.draw.rect(screen, (255, 255, 255), bg_rect, 2)

# ======================
# ZOMBIE SPAWN
# ======================
zombies = []
for _ in range(5):
    x = random.randint(100, SCREEN_W - 100)
    y = random.randint(100, SCREEN_H - 100)
    zombies.append(Zombie(x, y))

# ======================
# SPELER
# ======================
player_pos = pygame.Vector2(SCREEN_W // 2, SCREEN_H // 2)

# ======================
# HOOFDLOOP
# ======================
running = True
while running:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Player beweging (Q Z S D)
    keys = pygame.key.get_pressed()
    vel = pygame.Vector2(0, 0)
    if keys[pygame.K_q]: vel.x -= 1
    if keys[pygame.K_d]: vel.x += 1
    if keys[pygame.K_z]: vel.y -= 1
    if keys[pygame.K_s]: vel.y += 1
    if vel.length() > 0:
        vel.normalize_ip()
    player_pos += vel * PLAYER_SPEED * dt

    # SPACE: dood de eerste levende zombie (voor death anim demo)
    if keys[pygame.K_SPACE]:
        for zombie in zombies:
            if zombie.alive and zombie.health > 0:
                zombie.health = 0
                break

    # Update zombies
    for zombie in zombies:
        zombie.update(dt, player_pos)

    # Tekenen
    screen.fill((30, 30, 30))
    # Player (blauwe square)
    pygame.draw.rect(screen, (0, 150, 255), 
                     (player_pos.x - PLAYER_SIZE // 2, player_pos.y - PLAYER_SIZE // 2, PLAYER_SIZE, PLAYER_SIZE))

    # Zombies (achterste eerst voor depth, maar simple)
    for zombie in zombies:
        zombie.draw(screen)

    pygame.display.flip()

pygame.quit()