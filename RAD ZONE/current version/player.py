import pygame
from weapon import Weapon
from animation import Animator

class Player:
    def __init__(self, surf, rect, sound):

        self._move_dir = pygame.Vector2()

        self._equipped_item = None

        self._surf = surf
        self._rect = rect

        self._pos = pygame.Vector2(self._rect.center)

        self.sound = sound
        self.animator = Animator("RAD ZONE/current version/Graphics/player")

        # ---------- INPUT TRACKING ----------
        self._was_mouse_pressed = False
        self._f_was_pressed = False

        # ---------- WEAPONS ----------
        self.available_weapons = ["knife", "pistol", "rifle", "revolver", "shotgun"]
        self.current_weapon_index = 0
        self.weapon = Weapon(self.available_weapons[self.current_weapon_index], self.sound)
        self.weapon.equip()

        # ---------- HEALTH ----------
        self._max_health = 100
        self._health = self._max_health

        # ---------- MOVEMENT ----------
        self._walk_speed = 400
        self._run_speed = 600
        self._speed = self._walk_speed

        # ---------- STAMINA ----------
        self._max_stamina = 100
        self._stamina = self._max_stamina
        self._display_stamina = self._stamina / self._max_stamina  # ratio 0-1

        self._stamina_drain = 40
        self._stamina_regen = 15
        self._regen_delay = 1.0
        self._exhaust_at = 0
        self._recover_at = 20
        self._exhausted = False
        self._last_run_time = 0

        # ---------- ATTACK STATE ----------
        self._attack_last_time = 0
        self._attack_targets_hit = set()  # For melee hits
        self._attack_key_was_pressed = False


    # ------------------- GETTERS -------------------
    def get_rect(self): return self._rect
    def get_surface(self): return self._surf
    def get_speed(self): return self._speed
    def get_health(self): return self._health
    def get_max_health(self): return self._max_health
    def is_exhausted(self): return self._exhausted

    def is_exhausted(self):
        return self._exhausted
    
    def set_equipped_item(self, item):
        self._equipped_item = item
        if item and hasattr(item, "name"):  # this might fail because inventory items don't have "name"
            weapon_name = getattr(item, "name", None)
            if not weapon_name and hasattr(item, "weapon_surf"):  # fallback: use item key as weapon name
                weapon_name = item.key  # assuming your item object has 'key' (like "pistol")
            if weapon_name:
                self.weapon = Weapon(weapon_name, self.sound)
                self.weapon.equip()
    
    def get_health(self):
        return self._health
    
    def get_max_health(self):
        return self._max_health
    
    def take_damage(self, damage):
        self._health -= damage
        self._health = max(0, self._health)
        
    def get_stamina(self):
        return self._stamina

    def get_max_stamina(self):
        return self._max_stamina

    # ------------------- STAMINA -------------------
    def restore_stamina(self, amount):
        self._stamina = min(self._stamina + amount, self._max_stamina)

    def _update_stamina(self, running, dt, current_time):
        if self._stamina <= self._exhaust_at:
            self._exhausted = True
        elif self._stamina >= self._recover_at:
            self._exhausted = False

        if running:
            self._speed = self._run_speed
            self._stamina -= self._stamina_drain * dt
            self._last_run_time = current_time
        else:
            self._speed = self._walk_speed
            if current_time - self._last_run_time >= self._regen_delay:
                self._stamina += self._stamina_regen * dt

        self._stamina = max(0, min(self._stamina, self._max_stamina))

        # Smooth display as ratio 0-1
        target_ratio = self._stamina / self._max_stamina
        lerp_speed = 8
        self._display_stamina += (target_ratio - self._display_stamina) * min(lerp_speed * dt, 1)

    # ------------------- UPDATE -------------------
    def update(self, keys, dt, current_time):
        dx = keys[pygame.K_d] - keys[pygame.K_q]
        dy = keys[pygame.K_s] - keys[pygame.K_z]
        velocity = pygame.Vector2(dx, dy)

        moving = velocity.length_squared() > 0
        running = keys[pygame.K_LSHIFT] and moving and not self._exhausted
        if moving:
            velocity = velocity.normalize()
        
        self._move_dir = velocity


        # ---------- STAMINA UPDATE ----------
        self._update_stamina(running, dt, current_time)

        # ---------- MOVEMENT ----------
        self._pos += velocity * self._speed * dt
        self._rect.center = self._pos

        # ---------- ANIMATION ----------
        self.animator.update(velocity, dt, current_time)

        # ---------- SHOOTING ----------
        mouse_pressed = pygame.mouse.get_pressed()[0]
        if mouse_pressed:
            if self.weapon.full_auto or not self._was_mouse_pressed:
                self.weapon.shoot(current_time)
        self._was_mouse_pressed = mouse_pressed

        # ---------- RELOAD ----------
        if keys[pygame.K_r]:
            self.weapon.reload()

        # ---------- ATTACK ANIMATION----------
        mouse_pressed = pygame.mouse.get_pressed()[0]
        if mouse_pressed:
            if self.weapon.name == "knife":
                # knife slash animation & damage
                if pygame.time.get_ticks() / 1000 - self._attack_last_time > 0.5:
                    self.animator.play_stab(current_time, duration=0.4)
                    self._attack_last_time = current_time
                    self._attack_targets_hit = set()
            else:
                # guns
                if self.weapon.full_auto or not self._was_mouse_pressed:
                    self.weapon.shoot(current_time)
        self._was_mouse_pressed = mouse_pressed


    # ------------------- DRAW -------------------
    def draw(self, screen):
        image = self.animator.get_image()
        rect = image.get_rect(center=screen.get_rect().center)

        # Weapon behind player when moving up
        if self._move_dir.y < 0:
            self.draw_weapon(screen)

        screen.blit(image, rect)

        # Weapon in front otherwise
        if self._move_dir.y >= 0:
            self.draw_weapon(screen)




    def next_weapon(self):
        if not self.available_weapons: return
        self.current_weapon_index = (self.current_weapon_index + 1) % len(self.available_weapons)
        self.weapon = Weapon(self.available_weapons[self.current_weapon_index], self.sound)
        self.weapon.equip()
        self.reset_stab_state()

    def previous_weapon(self):
        if not self.available_weapons: return
        self.current_weapon_index = (self.current_weapon_index - 1) % len(self.available_weapons)
        self.weapon = Weapon(self.available_weapons[self.current_weapon_index], self.sound)
        self.weapon.equip()
        self.reset_stab_state()


    def shoot_weapon(self, current_time):
        self.weapon.shoot(current_time)

    def reload_weapon(self):
        self.weapon.reload()

    def draw_weapon(self, screen):
        if not self._equipped_item:
            return

        weapon_surf = self._equipped_item.get_char_weapon_surface()
        if not weapon_surf:
            return

        # 🔽 SCALE WEAPON
        SCALE = 0.6
        w, h = weapon_surf.get_size()
        weapon_surf = pygame.transform.smoothscale(
            weapon_surf,
            (int(w * SCALE), int(h * SCALE))
        )

        player_center = pygame.Vector2(screen.get_rect().center)
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        direction = mouse_pos - player_center

        if direction.length() == 0:
            return

        angle = direction.angle_to(pygame.Vector2(1, 0))
        weapon = weapon_surf

        # Flip when aiming left
        if direction.x < 0:
            weapon = pygame.transform.flip(weapon, True, False)
            angle += 180

        rotated = pygame.transform.rotate(weapon, angle)

        # Hand-side offset based on cursor position
        if direction.x >= 0:
            offset = pygame.Vector2(20, 20)    # right side
        else:
            offset = pygame.Vector2(-20, 20)   # left side

        rect = rotated.get_rect(center=player_center + offset)

        screen.blit(rotated, rect)



    
