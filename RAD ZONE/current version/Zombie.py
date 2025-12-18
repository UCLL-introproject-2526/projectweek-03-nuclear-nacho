import pygame
import os
import math
from animation import load_sheet_anim, DIRECTIONS

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
            print("[OK] Zombie animaties geladen")
        except Exception as e:
            print(f"[FOUT] Kon zombie sheets niet laden: {e}")
            empty = pygame.Surface((self.FRAME_W * self.SCALE, self.FRAME_H * self.SCALE), pygame.SRCALPHA)
            self.animations = {
                "walk": {"front": [empty]},
                "attack": {"front": [empty]},
                "death": {"front": [empty]}
            }
        
        self.image = self.animations["walk"]["front"][0]
        self.attack_end_time = 0
        self.death_end_time = 0
    
    def update(self, state, direction, dt, current_time):
        """Update zombie animation"""
        self.state = state
        self.direction = direction
        
        # Check if death animation is finished
        if self.state == "death" and current_time >= self.death_end_time:
            return False  # Signal that zombie is dead
        
        # Update frame
        if self.state in self.animations:
            frames = self.animations[self.state][self.direction]
            self.frame_index = (self.frame_index + self.ANIM_FPS * dt) % len(frames)
            self.image = frames[int(self.frame_index)]
        
        return True
    
    def set_attack(self, current_time, duration=0.6):
        """Start attack animation"""
        self.state = "attack"
        self.frame_index = 0
        self.attack_end_time = current_time + duration
    
    def set_death(self, current_time, duration=1.2):
        """Start death animation"""
        self.state = "death"
        self.frame_index = 0
        self.death_end_time = current_time + duration
    
    def get_image(self):
        return self.image


class Zombie:
    """Zombie enemy that walks towards player and can attack"""
    
    def __init__(self, x, y):
        # Position and movement
        self._pos = pygame.Vector2(x, y)
        self._rect = pygame.Rect(x, y, 128, 128)
        
        # Health
        self._max_health = 100
        self._health = self._max_health
        
        # Animation
        self.animator = ZombieAnimator()
        
        # State management
        self.state = "walk"  # walk, attack, death
        self.direction = "front"
        self.current_time = 0
        
        # Movement
        self._speed = 150
        self._attack_range = 80
        self._attack_cooldown = 1.5
        self._last_attack_time = -self._attack_cooldown
        self._attack_duration = 0.6
        self._is_attacking = False
        self._attack_end_time = 0
        self._damage_per_second = 15  # Damage zombies deal to player
        
        # Death
        self._is_dead = False
        self._death_time = 0
        
        # Knockback
        self._knockback_velocity = pygame.Vector2(0, 0)
        self._knockback_duration = 0.2
        self._knockback_end_time = 0
    
    def take_damage(self, damage, knockback_dir=None, current_time=0):
        """Zombie takes damage"""
        if self._is_dead:
            return
        
        self._health -= damage
        
        # Apply knockback if direction provided
        if knockback_dir:
            knockback_force = 300
            self._knockback_velocity = knockback_dir.normalize() * knockback_force
            self._knockback_end_time = current_time + self._knockback_duration
        
        # Check if zombie dies
        if self._health <= 0:
            self._health = 0
            self._is_dead = True
            self.state = "death"
            self.animator.set_death(current_time)
            self._death_time = current_time
    
    def update(self, player_pos, dt, current_time):
        """Update zombie behavior and animation"""
        self.current_time = current_time
        
        # Update animation
        if not self.animator.update(self.state, self.direction, dt, current_time):
            # Animation finished, death complete
            return False  # Signal to remove zombie
        
        # If dead, don't do anything else
        if self._is_dead:
            return True
        
        # Apply knockback
        if current_time < self._knockback_end_time:
            self._pos += self._knockback_velocity * dt
        else:
            self._knockback_velocity = pygame.Vector2(0, 0)
        
        # Calculate direction to player
        direction_to_player = player_pos - self._pos
        distance = direction_to_player.length()
        
        # Determine direction
        if distance > 0:
            direction_to_player = direction_to_player.normalize()
            
            # Set animation direction
            if abs(direction_to_player.x) > abs(direction_to_player.y):
                self.direction = "right" if direction_to_player.x > 0 else "left"
            else:
                self.direction = "front" if direction_to_player.y > 0 else "back"
        
        # Check if attack animation finished
        if self._is_attacking and current_time >= self._attack_end_time:
            self._is_attacking = False
            self.state = "walk"
        
        # Check if in attack range
        if distance < self._attack_range and not self._is_attacking:
            # Check if enough time passed since last attack
            if current_time - self._last_attack_time >= self._attack_cooldown:
                self.state = "attack"
                self._is_attacking = True
                self._last_attack_time = current_time
                self._attack_end_time = current_time + self._attack_duration
                self.animator.set_attack(current_time, self._attack_duration)

        elif not self._is_attacking and distance >= self._attack_range:
            # Move towards player
            self.state = "walk"
            self._pos += direction_to_player * self._speed * dt
        
        self._rect.center = self._pos
        return True
    
    def draw(self, screen, camera):
        """Draw zombie and health bar"""
        # Draw zombie sprite
        screen_pos = self._pos - camera.get_position()
        image = self.animator.get_image()
        rect = image.get_rect(center=screen_pos)
        screen.blit(image, rect)
        
        # Draw health bar
        self._draw_health_bar(screen, screen_pos)
    
    def _draw_health_bar(self, screen, screen_pos):
        """Draw zombie health bar above zombie"""
        # Make sure screen_pos is valid
        if screen_pos.x < -500 or screen_pos.x > screen.get_width() + 500:
            return  # Off screen
        if screen_pos.y < -500 or screen_pos.y > screen.get_height() + 500:
            return  # Off screen
        
        bar_width = 80
        bar_height = 8
        bar_x = screen_pos.x - bar_width // 2
        bar_y = screen_pos.y - 70
        
        # Background (red)
        pygame.draw.rect(screen, (200, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        
        # Health (green)
        health_width = (self._health / self._max_health) * bar_width
        pygame.draw.rect(screen, (0, 200, 0), (bar_x, bar_y, health_width, bar_height))
        
        # Border
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)
    
    def get_position(self):
        return self._pos
    
    def get_rect(self):
        return self._rect
    
    def is_dead(self):
        return self._is_dead
    
    def is_attacking(self):
        return self._is_attacking and self.state == "attack"
    
    def get_health(self):
        return self._health


class ZombieSpawner:
    """Manages zombie spawning and updates"""
    
    def __init__(self):
        self.zombies = []
        
        # Wave system
        self.current_wave = 0
        self.wave_cooldown = 10.0  # Seconds between waves (reduced from 30)
        self.last_wave_time = 0
        self.zombies_per_wave = 5
        self.max_zombies_per_wave = 15
        
        # Spawn control
        self.zombies_spawned_this_wave = 0
        self.wave_active = False
        self.max_zombies = 20
        self.spawn_delay = 0.3  # Delay between spawning individual zombies in a wave
        self.last_spawn_in_wave = 0
    
    def update(self, player_pos, dt, current_time):
        """Update all zombies"""
        # Wave management
        if not self.wave_active and current_time - self.last_wave_time >= self.wave_cooldown:
            self._start_new_wave(current_time)
        
        # Spawn zombies during wave with delay between each
        if self.wave_active and self.zombies_spawned_this_wave < self.zombies_per_wave and len(self.zombies) < self.max_zombies:
            if current_time - self.last_spawn_in_wave >= self.spawn_delay:
                self._spawn_zombie(player_pos)
                self.zombies_spawned_this_wave += 1
                self.last_spawn_in_wave = current_time
        
        # Check if wave is over
        if self.wave_active and len(self.zombies) == 0:
            self.wave_active = False
        
        # Update zombies
        dead_zombies = []
        for i, zombie in enumerate(self.zombies):
            if not zombie.update(player_pos, dt, current_time):
                dead_zombies.append(i)
        
        # Remove dead zombies
        for i in reversed(dead_zombies):
            self.zombies.pop(i)
    
    def _start_new_wave(self, current_time):
        """Start a new wave of zombies"""
        self.current_wave += 1
        self.wave_active = True
        self.zombies_spawned_this_wave = 0
        self.zombies_per_wave = min(5 + self.current_wave * 2, self.max_zombies_per_wave)
        self.last_wave_time = current_time
        print(f"[WAVE {self.current_wave}] Starting with {self.zombies_per_wave} zombies")
    
    def _spawn_zombie(self, player_pos):
        """Spawn zombie at random location away from player"""
        import random
        
        # Spawn around player at random direction
        angle = random.uniform(0, 2 * math.pi)
        distance = 400
        
        spawn_x = player_pos.x + math.cos(angle) * distance
        spawn_y = player_pos.y + math.sin(angle) * distance
        
        zombie = Zombie(spawn_x, spawn_y)
        self.zombies.append(zombie)
    
    def draw(self, screen, camera):
        """Draw all zombies with proper z-ordering"""
        # Sort zombies by y-position (bottom = drawn last = on top)
        sorted_zombies = sorted(self.zombies, key=lambda z: z.get_position().y)
        for zombie in sorted_zombies:
            zombie.draw(screen, camera)
    
    def get_zombies(self):
        return self.zombies
    
    def damage_zombies_in_range(self, pos, damage_range, damage, direction, current_time=0):
        """Damage all zombies within range (for melee weapon)"""
        for zombie in self.zombies:
            if not zombie.is_dead():
                zombie_pos = zombie.get_position()
                distance = (zombie_pos - pos).length()
                
                if distance < damage_range:
                    knockback_dir = (zombie_pos - pos)
                    zombie.take_damage(damage, knockback_dir, current_time)
    
    def check_player_collision(self, player_pos, player_rect):
        """Check if any zombie is attacking and colliding with player"""
        damage = 0
        for zombie in self.zombies:
            if zombie.is_attacking():
                distance = (zombie.get_position() - player_pos).length()
                if distance < 60:
                    damage += 10
        return damage
