import pygame
import random
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
        self._tracers = []  # List of dicts: {'pos', 'dir', 'speed', 'distance', 'start'}


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
            return

        self._equipped_item = item

        if isinstance(item, WeaponItem):
            self.weapon = item.get_weapon()   # ✅ ONLY ONCE
            if play_sound:
                item.play_equip_sound()
        else:
            self.weapon = None



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

        # Update projectile tracers
        for i in range(len(self._tracers) - 1, -1, -1):
            tracer = self._tracers[i]
            prev_pos = tracer['pos'].copy()
            tracer['pos'] += tracer['dir'] * tracer['speed'] * dt

            hit_something = False
            for zombie in self._zombie_spawner.get_zombies():
                if zombie._is_dead:
                    continue

                rect = zombie.get_rect()
                if rect.clipline(prev_pos, tracer['pos']):
                    # Deal damage
                    if self.weapon:
                        zombie.take_damage(
                            self.weapon.damage,
                            tracer['dir'],
                            pygame.time.get_ticks() / 1000
                        )
                    # Remove tracer immediately
                    self._tracers.pop(i)
                    hit_something = True
                    break  # stop checking other zombies for this tracer

            # Remove tracer if it reached max distance and didn't hit anything
            if not hit_something and (tracer['pos'] - tracer['start']).length() >= tracer['distance']:
                self._tracers.pop(i)



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
        if not self.weapon:
            return

        weapon = self.weapon
        weapon_id = weapon.id

        # ---------------- KNIFE ----------------
        if weapon_id == "knife":
            if mouse_pressed and not self._was_mouse_pressed:
                if not self._is_stabbing:
                    self._start_stab(current_time)
                    if self.sound:
                        self.sound.play_weapon("knife", "shoot")

            # Stop stab after duration
            if self._is_stabbing and current_time >= self._stab_end_time:
                self._is_stabbing = False

            return


        # ---------------- GUNS ----------------
        fired = False

        if weapon.full_auto:
            if mouse_pressed and weapon.shoot(current_time):
                fired = True
        else:
            if mouse_pressed and not self._was_mouse_pressed:
                if weapon.shoot(current_time):
                    fired = True

        if fired:
            self._apply_gun_damage()
            if self.sound:
                self.sound.play_weapon(weapon_id, "shoot")




    # ---------------- KNIFE STAB ----------------
    def _start_stab(self, current_time):
        """Initiates a knife stab attack."""
        self._is_stabbing = True
        self._stab_end_time = current_time + 0.4
        self._attack_last_time = current_time
        self._attack_targets_hit = set()
        self.animator.play_stab()
        self._apply_knife_damage()


    # ---------------- APPLY DAMAGE ----------------
    def _apply_knife_damage(self):
        """Deals damage to zombies near the player for a knife attack."""
        player_pos = pygame.Vector2(self.get_rect().center)
        for zombie in self._zombie_spawner.get_zombies():
            if zombie not in self._attack_targets_hit and not zombie._is_dead:
                if (zombie.get_position() - player_pos).length() < 100:
                    zombie.take_damage(
                        50,
                        zombie.get_position() - player_pos,
                        pygame.time.get_ticks() / 1000
                    )
                    self._attack_targets_hit.add(zombie)

    def _apply_gun_damage(self):
        if not self._zombie_spawner or not self.weapon:
            return

        player_pos = pygame.Vector2(self.get_rect().center)
        direction = (self._mouse_world - player_pos)

        if direction.length() == 0:
            return

        direction = direction.normalize()
        max_range = self.weapon.range

        # SHOTGUN
        if self.weapon.id == "shotgun":
            pellets = self.weapon.pellets
            spread = self.weapon.spread

            for _ in range(pellets):
                angle = random.uniform(-spread, spread)
                pellet_dir = direction.rotate(angle)
                end_pos = player_pos + pellet_dir * self.weapon.range

                self._raycast_and_damage(player_pos, end_pos)
                self._spawn_tracer(player_pos, end_pos)

        # NORMAL GUNS
        else:
            end_pos = player_pos + direction * self.weapon.range
            self._raycast_and_damage(player_pos, end_pos)
            self._spawn_tracer(player_pos, end_pos)

    def _raycast_and_damage(self, start, end):
        closest_zombie = None
        closest_dist = float("inf")

        for zombie in self._zombie_spawner.get_zombies():
            if zombie._is_dead:
                continue

            rect = zombie.get_rect()
            hit = rect.clipline(start, end)

            if hit:
                hit_point = pygame.Vector2(hit[0])
                dist = hit_point.distance_to(start)

                if dist < closest_dist:
                    closest_dist = dist
                    closest_zombie = zombie

        if closest_zombie:
            closest_zombie.take_damage(
                self.weapon.damage,
                (end - start).normalize(),
                pygame.time.get_ticks() / 1000
            )

    def _spawn_tracer(self, start, end):
        direction = (end - start)
        if direction.length() == 0:
            return
        direction = direction.normalize()
        distance = (end - start).length()
        speed = 1200  # pixels per second, tweak as needed

        self._tracers.append({
            'pos': start.copy(),
            'dir': direction,
            'speed': speed,
            'distance': distance,
            'start': start.copy()
        })


            

    # ---------- DRAW ----------
    def draw(self, screen, camera):
        image = self.animator.get_image()
        rect = image.get_rect(center=screen.get_rect().center)

        if self._move_dir.y < 0:
            self.draw_weapon(screen)

        screen.blit(image, rect)

        if self._move_dir.y >= 0:
            self.draw_weapon(screen)

        # -------- DRAW TRACERS --------
        cam_offset = camera.get_position()
        for tracer in self._tracers:
            tracer_pos = tracer['pos'] - cam_offset
            pygame.draw.circle(
                screen,
                (255, 240, 150),  # pale yellow
                (int(tracer_pos.x), int(tracer_pos.y)),
                3
            )


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