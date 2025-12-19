import pygame
from holdable_objects import WeaponItem, ConsumableItem
from animation import Animator
from zombie import Zombie

class Player:
    def __init__(self, surf, rect, sound):
        self._surf = surf
        self._rect = rect
        self._pos = pygame.Vector2(self._rect.center)
        self.sound = sound
        self.animator = Animator("RAD ZONE/current version/Graphics/player")

        # Movement
        self._move_dir = pygame.Vector2()
        self._walk_speed = 400
        self._run_speed = 600
        self._speed = self._walk_speed

        # Health
        self._max_health = 100
        self._health = self._max_health
        self._is_dead = False

        # Stamina
        self._max_stamina = 100
        self._stamina = self._max_stamina
        self._display_stamina = self._stamina / self._max_stamina
        self._stamina_drain = 40
        self._stamina_regen = 15
        self._regen_delay = 1.0
        self._exhaust_at = 0
        self._recover_at = 20
        self._exhausted = False
        self._last_run_time = 0

        # Input tracking
        self._was_mouse_pressed = False

        # Equipped item
        self._equipped_item = None
        self.weapon = None  # only if equipped item is WeaponItem

        # Melee
        self._is_stabbing = False
        self._stab_end_time = 0
        self._attack_last_time = 0
        self._attack_targets_hit = set()

        # Inventory reference (will be set externally)
        self._inventory = None

        # Mouse
        self._mouse_screen = pygame.Vector2(0, 0)
        self._mouse_world = pygame.Vector2(0, 0)

    def get_rect(self):
        return self._rect

    # ---------- SETTERS ----------
    def set_inventory(self, inventory):
        self._inventory = inventory

    def set_equipped_item(self, item, play_sound=True):
        if item is self._equipped_item:
            return  # Already equipped, do nothing

        self._equipped_item = item
        if isinstance(item, WeaponItem):
            self.weapon = item.get_weapon()
            if play_sound:
                item.play_equip_sound()
        else:
            self.weapon = None
            if play_sound and isinstance(item, ConsumableItem):
                item.play_pickup_sound()


    # ---------- HEALTH ----------
    def get_health(self): return self._health
    def get_max_health(self): return self._max_health

    def take_damage(self, damage):
        if self._is_dead: return
        self._health -= damage
        self._health = max(0, self._health)
        if self.sound:
            if self._health > 0:
                self.sound.play_player_hurt()
            else:
                self.sound.play_player_death()
                self._is_dead = True

    # ---------- STAMINA ----------
    def get_stamina(self): return self._stamina
    def get_max_stamina(self): return self._max_stamina
    def is_exhausted(self): return self._exhausted

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
        target_ratio = self._stamina / self._max_stamina
        lerp_speed = 8
        self._display_stamina += (target_ratio - self._display_stamina) * min(lerp_speed * dt, 1)

    # ---------- UPDATE ----------
    def update(self, keys, dt, current_time, mouse_world):
        self._mouse_world = pygame.Vector2(mouse_world)
        self._mouse_screen = pygame.Vector2(pygame.mouse.get_pos())

        # Movement
        dx = keys[pygame.K_d] - keys[pygame.K_q]
        dy = keys[pygame.K_s] - keys[pygame.K_z]
        velocity = pygame.Vector2(dx, dy)
        moving = velocity.length_squared() > 0
        running = keys[pygame.K_LSHIFT] and moving and not self._exhausted
        if moving:
            velocity = velocity.normalize()
        self._move_dir = velocity
        self._update_stamina(running, dt, current_time)
        self._pos += velocity * self._speed * dt

        # Clamp player position to map
        self._pos.x = max(self._rect.width//2, min(self._pos.x, 7680 - self._rect.width//2))
        self._pos.y = max(self._rect.height//2, min(self._pos.y, 6400 - self._rect.height//2))
        self._rect.center = self._pos

        # Animation
        self.animator.update(self._move_dir, dt, current_time, override_stab=self._is_stabbing)

        # Weapon & Mouse Input
        mouse_pressed = pygame.mouse.get_pressed()[0]
        if self._equipped_item:
            if isinstance(self._equipped_item, WeaponItem):
                self._handle_weapon_attack(mouse_pressed, current_time)
            elif isinstance(self._equipped_item, ConsumableItem):
                if mouse_pressed and not self._was_mouse_pressed:
                    self._equipped_item.use(self)

        self._was_mouse_pressed = mouse_pressed

    # ---------- MELEE & GUN ----------
    def _handle_weapon_attack(self, mouse_pressed, current_time):
        weapon_type = self._equipped_item.get_id()
        if weapon_type == "knife":
            if mouse_pressed and not self._was_mouse_pressed:
                if self.weapon.shoot(current_time):
                    self._is_stabbing = True
                    self._stab_end_time = current_time + 0.4
                    self.animator.play_stab()
                    self._attack_last_time = current_time
                    self._attack_targets_hit = set()
                    self._apply_knife_damage()
            if self._is_stabbing and current_time >= self._stab_end_time:
                self._is_stabbing = False
        else:
            if self.weapon.full_auto:
                if mouse_pressed and self.weapon.shoot(current_time):
                    self._apply_gun_damage()
            else:
                if mouse_pressed and not self._was_mouse_pressed:
                    if self.weapon.shoot(current_time):
                        self._apply_gun_damage()

    # ---------- MELEE DAMAGE ----------
    def _apply_knife_damage(self):
        if not hasattr(self, "_zombie_spawner") or self._zombie_spawner is None:
            return
        for zombie in self._zombie_spawner.get_zombies():
            if zombie.is_dead() or zombie in self._attack_targets_hit:
                continue
            distance = (zombie.get_position() - self._pos).length()
            if distance <= 100:
                knockback_dir = zombie.get_position() - self._pos
                knockback_dir = knockback_dir.normalize() if knockback_dir.length_squared() > 0 else pygame.Vector2(0, -1)
                zombie.take_damage(50, knockback_dir, current_time=pygame.time.get_ticks()/1000)
                self._attack_targets_hit.add(zombie)

    # ---------- GUN DAMAGE ----------
    def _apply_gun_damage(self):
        if not hasattr(self, "_zombie_spawner") or self._zombie_spawner is None:
            return
        player_pos = self._pos
        shot_dir = self._mouse_world - player_pos
        if shot_dir.length_squared() == 0:
            return
        shot_dir = shot_dir.normalize()
        for zombie in self._zombie_spawner.get_zombies():
            if zombie.is_dead():
                continue
            to_zombie = zombie.get_position() - player_pos
            distance_along_shot = to_zombie.dot(shot_dir)
            if 0 <= distance_along_shot <= self.weapon.range:
                perp_dist_vec = to_zombie - shot_dir * distance_along_shot
                if perp_dist_vec.length_squared() <= (self.weapon.width / 2) ** 2:
                    knockback_dir = perp_dist_vec if perp_dist_vec.length_squared() > 0 else shot_dir
                    zombie.take_damage(self.weapon.damage, knockback_dir, current_time=pygame.time.get_ticks()/1000)

    # ---------- DRAW ----------
    def draw(self, screen):
        image = self.animator.get_image()
        rect = image.get_rect(center=screen.get_rect().center)
        if self._move_dir.y < 0:
            self.draw_weapon(screen)
        screen.blit(image, rect)
        if self._move_dir.y >= 0:
            self.draw_weapon(screen)

    def draw_weapon(self, screen):
        if not self._equipped_item: return
        weapon_surf = getattr(self._equipped_item, "get_char_weapon_surface", lambda: None)()
        if not weapon_surf: return

        SCALE = 0.6
        w, h = weapon_surf.get_size()
        weapon_surf = pygame.transform.smoothscale(weapon_surf, (int(w*SCALE), int(h*SCALE)))

        player_center = pygame.Vector2(screen.get_rect().center)
        mouse_pos = self._mouse_screen
        direction = mouse_pos - player_center
        if direction.length() == 0: return
        angle = direction.angle_to(pygame.Vector2(1, 0))
        weapon = weapon_surf
        if direction.x < 0:
            weapon = pygame.transform.flip(weapon, True, False)
            angle += 180
        rotated = pygame.transform.rotate(weapon, angle)
        offset = pygame.Vector2(20,20) if direction.x >=0 else pygame.Vector2(-20,20)
        rect = rotated.get_rect(center=player_center + offset)
        screen.blit(rotated, rect)
