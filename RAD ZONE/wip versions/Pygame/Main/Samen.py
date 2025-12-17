import pygame
import random
import math
import os

# ======================
# INIT
# ======================
pygame.init()
pygame.mixer.init()

SCREEN_W, SCREEN_H = 800, 600
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Apocalypse - Waves")
clock = pygame.time.Clock()

# ======================
# SETTINGS
# ======================
FRAME_W, FRAME_H = 32, 32
SCALE = 4
ANIM_FPS = 10

PLAYER_SPEED = 200
PLAYER_MAX_HP = 100

ZOMBIE_SPEED = 110
ZOMBIE_MAX_HP = 100
ZOMBIE_DAMAGE = 15
ZOMBIE_ATTACK_RANGE = 55
ZOMBIE_ATTACK_COOLDOWN = 1.0

ARROW_SPEED = 500
ARROW_DAMAGE = 50
STAB_DAMAGE = 50
STAB_RANGE = 55

DIRECTIONS = ["front", "back", "right", "left"]

# ======================
# PATHS (relatief aan script)
# ======================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PLAYER_PATH = os.path.join(BASE_DIR, "Player")
ZOMBIE_PATH = os.path.join(BASE_DIR, "Zombie")
SOUND_PATH  = os.path.join(BASE_DIR, "Sound")

# ======================
# HELPERS
# ======================
def load_anim(path, frames):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Animatiebestand niet gevonden: {path}")
    sheet = pygame.image.load(path).convert_alpha()
    anims = {}
    for row, d in enumerate(DIRECTIONS):
        anims[d] = []
        for col in range(frames):
            surf = pygame.Surface((FRAME_W, FRAME_H), pygame.SRCALPHA)
            surf.blit(sheet, (0,0), (col*FRAME_W, row*FRAME_H, FRAME_W, FRAME_H))
            surf = pygame.transform.scale(surf, (FRAME_W*SCALE, FRAME_H*SCALE))
            anims[d].append(surf)
    return anims

def load_sound(filename, volume=0.8):
    path = os.path.join(SOUND_PATH, filename)
    if os.path.exists(path):
        s = pygame.mixer.Sound(path)
        s.set_volume(volume)
        return s
    return None

# ======================
# LOAD ASSETS
# ======================
walk_anim     = load_anim(os.path.join(PLAYER_PATH, "walk.png"), 3)
idle_anim     = load_anim(os.path.join(PLAYER_PATH, "idle.png"), 1)
stab_anim     = load_anim(os.path.join(PLAYER_PATH, "stab.png"), 3)
crossbow_anim = load_anim(os.path.join(PLAYER_PATH, "crossbow.png"), 3)
death_anim    = load_anim(os.path.join(PLAYER_PATH, "Death.png"), 4)

arrow_img = pygame.image.load(os.path.join(PLAYER_PATH, "arrow.png")).convert_alpha()
arrow_img = pygame.transform.scale(arrow_img.subsurface((0,0,FRAME_W,FRAME_H)), (FRAME_W*SCALE, FRAME_H*SCALE))

knife_sound = load_sound("knife_slash.mp3", 0.8)
zombie_death_sound = load_sound("scream_wilhelm.mp3", 0.8)
crossbow_sound = load_sound("shoot_crossbow.mp3", 0.5)

# ======================
# PLAYER STATE
# ======================
player_pos = pygame.Vector2(0,0)
player_hp = PLAYER_MAX_HP
player_dead = False
game_over = False
direction = "front"
state = "idle"
frame_index = 0.0
arrow_fired = False
camera = pygame.Vector2(0,0)

shots_fired = shots_hit = zombies_killed = 0
current_wave = 1
wave_cooldown = 0
WAVE_COOLDOWN_TIME = 5

# ======================
# ARROW CLASS
# ======================
class Arrow:
    def __init__(self, start, target):
        self.pos = pygame.Vector2(start)
        d = target - start
        self.dir = d.normalize() if d.length() else pygame.Vector2(0,-1)
        self.vel = self.dir * ARROW_SPEED
        angle = math.degrees(math.atan2(-self.dir.y, self.dir.x)) - 90
        self.image = pygame.transform.rotate(arrow_img, angle)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, dt):
        self.pos += self.vel * dt
        self.rect.center = self.pos

    def draw(self):
        screen.blit(self.image, self.rect.topleft - camera)

arrows = []

# ======================
# ZOMBIE CLASS
# ======================
class Zombie:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.hp = ZOMBIE_MAX_HP
        self.alive = True
        self.state = "walk"
        self.direction = "front"
        self.frame = 0.0
        self.attack_timer = 0
        self.anim = {
            "walk": load_anim(os.path.join(ZOMBIE_PATH, "Walk.png"), 6),
            "attack": load_anim(os.path.join(ZOMBIE_PATH, "Attack.png"), 4),
            "death": load_anim(os.path.join(ZOMBIE_PATH, "Death.png"), 4)
        }
        self.image = self.anim["walk"]["front"][0]

    def feet_y(self):
        return self.pos.y

    def update(self, dt):
        global player_hp, player_dead, game_over

        if not self.alive:
            frames = self.anim["death"][self.direction]
            self.frame = min(self.frame + ANIM_FPS*dt, len(frames)-1)
            self.image = frames[int(self.frame)]
            return

        # richting naar speler
        diff = player_pos - self.pos
        dist = diff.length()

        # ----------------------
        # Zombie-zombie scheiding
        # ----------------------
        for other in zombies:
            if other is not self and other.alive:
                separation = self.pos - other.pos
                dist_sep = separation.length()
                if dist_sep < 40 and dist_sep > 0:  # minimale afstand
                    self.pos += separation.normalize() * (40 - dist_sep) * 0.5

        # richting bepalen
        if abs(diff.x) > abs(diff.y):
            self.direction = "right" if diff.x > 0 else "left"
        else:
            self.direction = "front" if diff.y > 0 else "back"

        self.attack_timer -= dt

        if dist <= ZOMBIE_ATTACK_RANGE and not player_dead:
            self.state = "attack"
            if int(self.frame) == 2 and self.attack_timer <= 0:
                player_hp -= ZOMBIE_DAMAGE
                self.attack_timer = ZOMBIE_ATTACK_COOLDOWN
                if player_hp <= 0:
                    player_dead = True
                    end_game()
        else:
            self.state = "walk"
            if dist > 0:
                diff.normalize_ip()
                self.pos += diff * ZOMBIE_SPEED * dt

        frames = self.anim[self.state][self.direction]
        self.frame = (self.frame + ANIM_FPS*dt) % len(frames)
        self.image = frames[int(self.frame)]

    def take_damage(self, dmg):
        global zombies_killed
        if not self.alive:
            return
        self.hp -= dmg
        if self.hp <= 0:
            self.alive = False
            self.frame = 0
            zombies_killed += 1
            if zombie_death_sound:
                zombie_death_sound.play()

    def draw(self):
        draw_pos = (self.pos.x - self.image.get_width()//2 - camera.x,
                    self.pos.y - self.image.get_height() - camera.y)
        screen.blit(self.image, draw_pos)

# ======================
# GAME FUNCTIONS
# ======================
def spawn_wave(wave):
    return [Zombie(random.randint(-400,400), random.randint(-400,400)) for _ in range(3+wave*2)]

def reset_game():
    global zombies, arrows, player_pos, player_hp, player_dead
    global current_wave, wave_cooldown, shots_fired, shots_hit, zombies_killed
    zombies = spawn_wave(1)
    arrows.clear()
    player_pos = pygame.Vector2(0,0)
    player_hp = PLAYER_MAX_HP
    player_dead=False
    current_wave=1
    wave_cooldown=0
    shots_fired=shots_hit=zombies_killed=0

def end_game():
    global game_over
    game_over=True

reset_game()
font = pygame.font.SysFont(None,36)
bigfont = pygame.font.SysFont(None,72)

# ======================
# GAME LOOP
# ======================
running=True
while running:
    dt = clock.tick(60)/1000
    for event in pygame.event.get():
        if event.type==pygame.QUIT: running=False
        if game_over and event.type==pygame.KEYDOWN and event.key==pygame.K_RETURN: game_over=False; reset_game()
        if not game_over:
            if event.type==pygame.KEYDOWN and state=="idle":
                if event.key==pygame.K_f:
                    state="stab"
                    frame_index=0
                    if knife_sound: knife_sound.play()
            if event.type==pygame.MOUSEBUTTONDOWN and state=="idle":
                state="crossbow"
                frame_index=0
                arrow_fired=False
                shots_fired+=1
                if crossbow_sound: crossbow_sound.play()

    # PLAYER MOVEMENT
    if not game_over:
        keys=pygame.key.get_pressed()
        vel=pygame.Vector2(0,0)
        if keys[pygame.K_q]: vel.x-=PLAYER_SPEED; direction="left"
        if keys[pygame.K_d]: vel.x+=PLAYER_SPEED; direction="right"
        if keys[pygame.K_z]: vel.y-=PLAYER_SPEED; direction="back"
        if keys[pygame.K_s]: vel.y+=PLAYER_SPEED; direction="front"
        if state in ("idle","walk"):
            player_pos+=vel*dt
            state="walk" if vel.length()>0 else "idle"

    camera = player_pos - pygame.Vector2(SCREEN_W//2, SCREEN_H//2)

    # PLAYER ANIMATIONS
    if game_over:
        frames=death_anim["front"]
        frame_index=min(frame_index+ANIM_FPS*dt,len(frames)-1)
    elif state=="walk":
        frames=walk_anim[direction]
        frame_index=(frame_index+ANIM_FPS*dt)%len(frames)
    elif state=="idle":
        frames=idle_anim[direction]
        frame_index=0
    elif state=="stab":
        frames=stab_anim[direction]
        frame_index+=ANIM_FPS*dt
        if int(frame_index)==1:
            for z in zombies:
                if z.alive and (z.pos-player_pos).length()<=STAB_RANGE:
                    z.take_damage(STAB_DAMAGE)
        if frame_index>=len(frames):
            state="idle"
            frame_index=0
    elif state=="crossbow":
        frames=crossbow_anim[direction]
        frame_index+=ANIM_FPS*dt
        if not arrow_fired and int(frame_index)==2:
            arrows.append(Arrow(player_pos,pygame.Vector2(pygame.mouse.get_pos())+camera))
            arrow_fired=True
        if frame_index>=len(frames):
            state="idle"
            frame_index=0

    player_image=frames[int(frame_index)]

    # UPDATE ARROWS
    for a in arrows[:]:
        a.update(dt)
        for z in zombies:
            if z.alive and a.rect.collidepoint(z.pos):
                z.take_damage(ARROW_DAMAGE)
                shots_hit+=1
                arrows.remove(a)
                break

    # UPDATE ZOMBIES
    for z in zombies:
        z.update(dt)

    # WAVES
    if all(not z.alive for z in zombies):
        wave_cooldown+=dt
        if wave_cooldown>=WAVE_COOLDOWN_TIME:
            current_wave+=1
            zombies=spawn_wave(current_wave)
            wave_cooldown=0

    # DRAW
    screen.fill((25,25,25))
    draw_list=[(z.feet_y(),z.draw) for z in zombies]
    draw_list.append((player_pos.y, lambda: screen.blit(player_image,(SCREEN_W//2-player_image.get_width()//2, SCREEN_H//2-player_image.get_height()))))
    draw_list.sort(key=lambda x:x[0])
    for _,draw in draw_list: draw()

    for a in arrows: a.draw()

    # PLAYER HP
    pygame.draw.rect(screen,(120,0,0),(20,20,200,16))
    pygame.draw.rect(screen,(0,200,0),(20,20,200*(player_hp/PLAYER_MAX_HP),16))

    # WAVE
    screen.blit(font.render(f"Wave {current_wave}",True,(255,255,255)),(SCREEN_W//2-60,20))

    # GAME OVER
    if game_over:
        acc=(shots_hit/shots_fired*100) if shots_fired>0 else 0
        screen.blit(bigfont.render("YOU DIED",True,(200,0,0)),(SCREEN_W//2-150,200))
        screen.blit(font.render(f"Zombies killed: {zombies_killed}",True,(255,255,255)),(280,300))
        screen.blit(font.render(f"Shots: {shots_fired}",True,(255,255,255)),(280,340))
        screen.blit(font.render(f"Accuracy: {acc:.1f}%",True,(255,255,255)),(280,380))
        screen.blit(font.render("Press ENTER to restart",True,(255,255,255)),(200,430))

    # ZOMBIE HP
    for z in zombies:
        if z.alive:
            bar_w=FRAME_W*SCALE
            bar_h=6
            bar_x=z.pos.x-bar_w//2-camera.x
            bar_y=z.pos.y-FRAME_H*SCALE-10-camera.y
            pygame.draw.rect(screen,(100,0,0),(bar_x,bar_y,bar_w,bar_h))
            pygame.draw.rect(screen,(0,200,0),(bar_x,bar_y,bar_w*(z.hp/ZOMBIE_MAX_HP),bar_h))
            pygame.draw.rect(screen,(255,255,255),(bar_x,bar_y,bar_w,bar_h),1)

    pygame.display.flip()

pygame.quit()
