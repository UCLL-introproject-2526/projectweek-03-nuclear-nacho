import pygame
import os
import math
import random
from animation import load_sheet_anim, DIRECTIONS


# ==================================================
#                   ANIMATOR
# ==================================================
class ZombieAnimator:
    """Handles zombie animations (Walk, Attack, Death)"""

    def __init__(self):
        self.state = "walk"
        self.direction = "front"
        self.frame_index = 0.0
        self.ANIM_FPS = 10
        self.FRAME_W, self.FRAME_H = 32, 32
        self.SCALE = 4

        try:
            self.animations = {
                "walk": load_sheet_anim(
                    os.path.join("RAD ZONE", "current version", "Graphics", "ZWalk.png"),
                    frames_per_dir=4
                ),
                "attack": load_sheet_anim(
                    os.path.join("RAD ZONE", "current version", "Graphics", "ZAttack.png"),
                    frames_per_dir=3
                ),
                "death": load_sheet_anim(
                    os.path.join("RAD ZONE", "current version", "Graphics", "ZDeath.png"),
                    frames_per_dir=4
                ),
            }
        except Exception as e:
            print(f"[FOUT] Zombie animaties niet geladen: {e}")
            empty = pygame.Surface((self.FRAME_W * self.SCALE, self.FRAME_H * self.SCALE), pygame.SRCALPHA)
            self.animations = {
                "walk": {"front": [empty]},
                "attack": {"front": [empty]},
                "death": {"front": [empty]},
            }

        self.image = self.animations["walk"]["front"][0]
        self.attack_end_time = 0
        self.death_end_time = 0

    def update(self, state, direction, dt, current_time):
        self.state = state
        self.direction = direction

        if self.state == "death" and current_time >= self.death_end_time:
            return False  # death animation finished

        frames = self.animations[self.state][self.direction]
        self.frame_index = (self.frame_index + self.ANIM_FPS * dt) % len(frames)
        self.image = frames[int(self.frame_index)]

        return True

    def set_attack(self, current_time, duration=0.6):
        self.state = "attack"
        self.frame_index = 0
        self.attack_end_time = current_time + duration

    def set_death(self, current_time, duration=1.2):
        self.state = "death"
        self.frame_index = 0
        self.death_end_time = current_time + duration

    def get_image(self):
        return self.image


# ==================================================
#                     ZOMBIE
# ==================================================
class Zombie:
    def __init__(self, x, y):
        self._pos = pygame.Vector2(x, y)
        self._rect = pygame.Rect(0, 0, 128, 128)
        self._rect.center = self._pos

        self._max_health = 100
        self._health = self._max_health

        self.animator = ZombieAnimator()

        self.state = "walk"
        self.direction = "front"

        self._speed = 150
        self._attack_range = 80
        self._attack_cooldown = 1.5
        self._last_attack_time = -999
        self._attack_duration = 0.6
        self._is_attacking = False
        self._attack_end_time = 0
        self._damage_per_second = 15

        self._is_dead = False

        self._knockback_velocity = pygame.Vector2()
        self._knockback_end_time = 0

    def take_damage(self, damage, knockback_dir=None, current_time=0):
        if self._is_dead:
            return

        self._health -= damage

        if knockback_dir and knockback_dir.length() > 0:
            self._knockback_velocity = knockback_dir.normalize() * 300
            self._knockback_end_time = current_time + 0.2

        if self._health <= 0:
            self._health = 0
            self._is_dead = True
            self.state = "death"
            self.animator.set_death(current_time)

    def update(self, player_pos, dt, current_time):
        if not self.animator.update(self.state, self.direction, dt, current_time):
            return False  # remove zombie

        if self._is_dead:
            return True

        if current_time < self._knockback_end_time:
            self._pos += self._knockback_velocity * dt
        else:
            self._knockback_velocity = pygame.Vector2()

        direction = player_pos - self._pos
        distance = direction.length()

        if distance > 0:
            direction = direction.normalize()
            if abs(direction.x) > abs(direction.y):
                self.direction = "right" if direction.x > 0 else "left"
            else:
                self.direction = "front" if direction.y > 0 else "back"

        if self._is_attacking and current_time >= self._attack_end_time:
            self._is_attacking = False
            self.state = "walk"

        if distance < self._attack_range and not self._is_attacking:
            if current_time - self._last_attack_time >= self._attack_cooldown:
                self.state = "attack"
                self._is_attacking = True
                self._last_attack_time = current_time
                self._attack_end_time = current_time + self._attack_duration
                self.animator.set_attack(current_time)

        elif not self._is_attacking:
            self.state = "walk"
            self._pos += direction * self._speed * dt

        self._rect.center = self._pos
        return True

    def draw(self, screen, camera):
        screen_pos = self._pos - camera.get_position()
        image = self.animator.get_image()
        rect = image.get_rect(center=screen_pos)
        screen.blit(image, rect)
        self._draw_health_bar(screen, screen_pos)

    def _draw_health_bar(self, screen, pos):
        bar_w, bar_h = 80, 8
        x = pos.x - bar_w // 2
        y = pos.y - 70
        pygame.draw.rect(screen, (200, 0, 0), (x, y, bar_w, bar_h))
        pygame.draw.rect(
            screen,
            (0, 200, 0),
            (x, y, bar_w * (self._health / self._max_health), bar_h),
        )
        pygame.draw.rect(screen, (255, 255, 255), (x, y, bar_w, bar_h), 1)

    def get_position(self):
        return self._pos

    def is_attacking(self):
        return self._is_attacking and self.state == "attack"


# ==================================================
#                 ZOMBIE SPAWNER
# ==================================================
class ZombieSpawner:
    def __init__(self):
        self.zombies = []
        self.kill_count = 0

        self.current_wave = 0
        self.wave_cooldown = 10
        self.last_wave_time = 0
        self.zombies_per_wave = 5
        self.max_zombies_per_wave = 15

        self.zombies_spawned_this_wave = 0
        self.wave_active = False
        self.spawn_delay = 0.3
        self.last_spawn_time = 0
        self.max_zombies = 20

    def update(self, player_pos, dt, current_time):
        if not self.wave_active and current_time - self.last_wave_time >= self.wave_cooldown:
            self._start_wave(current_time)

        if self.wave_active and self.zombies_spawned_this_wave < self.zombies_per_wave:
            if current_time - self.last_spawn_time >= self.spawn_delay:
                if len(self.zombies) < self.max_zombies:
                    self._spawn_zombie(player_pos)
                    self.zombies_spawned_this_wave += 1
                    self.last_spawn_time = current_time

        dead = []
        for i, zombie in enumerate(self.zombies):
            if not zombie.update(player_pos, dt, current_time):
                dead.append(i)

        for i in reversed(dead):
            self.zombies.pop(i)
            self.kill_count += 1

        if self.wave_active and len(self.zombies) == 0:
            self.wave_active = False

    def _start_wave(self, current_time):
        self.current_wave += 1
        self.wave_active = True
        self.zombies_spawned_this_wave = 0
        self.zombies_per_wave = min(5 + self.current_wave * 2, self.max_zombies_per_wave)
        self.last_wave_time = current_time

    def _spawn_zombie(self, player_pos):
        angle = random.uniform(0, math.pi * 2)
        distance = 400
        x = player_pos.x + math.cos(angle) * distance
        y = player_pos.y + math.sin(angle) * distance
        self.zombies.append(Zombie(x, y))

    def draw(self, screen, camera):
        for zombie in sorted(self.zombies, key=lambda z: z.get_position().y):
            zombie.draw(screen, camera)

    def get_zombies(self):
        return self.zombies

    def get_kill_count(self):
        return self.kill_count
