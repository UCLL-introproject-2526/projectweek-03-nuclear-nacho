import pygame
from weapon import Weapon
from animation import Animator


class Player:
    def __init__(self, surf, rect, sound):



        self._surf = surf
        self._rect = rect
        
        self._pos = pygame.Vector2(self._rect.center)

        self.sound = sound
        self.animator = Animator("RAD ZONE/current version/Graphics/player")

        self._was_mouse_pressed = False  # tracks mouse state for single-shot
        self._f_was_pressed = False  # tracks F key state for single-shot stab
        self.available_weapons = [
            "knife",
            "pistol",
            "rifle",
            "revolver",
            "shotgun"
        ]

        self.current_weapon_index = 0
        self.weapon = Weapon(
            self.available_weapons[self.current_weapon_index],
            self.sound
        )

        self.weapon.equip()

        self._max_stamina = 100
        self._stamina = self._max_stamina

        self._drain = 40
        self._regen = 15

        self._exhaust_at = 0
        self._recover_at = 20
        self._exhausted = False
        
        # Health system
        self._max_health = 100
        self._health = self._max_health

        self._base_speed = 400
        self._sprint_speed = 600
        self._speed = self._base_speed

    # -------- GETTERS --------
    def get_rect(self):
        return self._rect

    def get_surface(self):
        return self._surf

    def get_speed(self):
        return self._speed

    def get_stamina(self):
        return self._stamina

    def is_exhausted(self):
        return self._exhausted
    
    def get_health(self):
        return self._health
    
    def get_max_health(self):
        return self._max_health
    
    def take_damage(self, damage):
        self._health -= damage
        self._health = max(0, self._health)

    # -------- LOGIC --------
    def update(self, keys, dt, current_time):
        # ---- movement / stamina ----
        moving = keys[pygame.K_z] or keys[pygame.K_q] or keys[pygame.K_s] or keys[pygame.K_d]
        sprinting = keys[pygame.K_LSHIFT] and moving

        dx = keys[pygame.K_d] - keys[pygame.K_q]
        dy = keys[pygame.K_s] - keys[pygame.K_z]
        velocity = pygame.Vector2(dx, dy)

        # Normalize diagonal movement
        if velocity.length() > 0:
            velocity = velocity.normalize()

        # Move player
        # Move in WORLD space
        self._pos += velocity * self._speed * dt
        self._rect.center = self._pos


        # Update animation
        self.animator.update(velocity, dt, current_time)




        if self._stamina <= self._exhaust_at:
            self._exhausted = True
        elif self._stamina >= self._recover_at:
            self._exhausted = False

        if sprinting and not self._exhausted:
            self._stamina -= self._drain * dt
            self._speed = self._sprint_speed
        else:
            self._stamina += self._regen * dt
            self._speed = self._base_speed

        self._stamina = max(0, min(self._stamina, self._max_stamina))

        # ---- MOUSE SHOOTING ----
        mouse_buttons = pygame.mouse.get_pressed()
        mouse_pressed = mouse_buttons[0]  # Left click

        # Single-shot for all weapons, full-auto for rifle
        if mouse_pressed:
            if self.weapon.full_auto or not self._was_mouse_pressed:
                self.shoot_weapon(current_time)

        self._was_mouse_pressed = mouse_pressed

        # ---- Reload with R ----
        if keys[pygame.K_r]:
            self.reload_weapon()

        # ---- STAB with F ----
        f_pressed = keys[pygame.K_f]
        if f_pressed and not self._f_was_pressed:
            self.animator.play_stab(current_time, duration=0.4)
        self._f_was_pressed = f_pressed





    def draw(self, screen):
        image = self.animator.get_image()
        rect = image.get_rect(center=screen.get_rect().center)
        screen.blit(image, rect)


    def next_weapon(self):
        if not self.available_weapons:
            return
        self.current_weapon_index += 1
        if self.current_weapon_index >= len(self.available_weapons):
            self.current_weapon_index = 0
        self.weapon = Weapon(
            self.available_weapons[self.current_weapon_index],
            self.sound
        )
        self.weapon.equip()


    def previous_weapon(self):
        if not self.available_weapons:
            return
        self.current_weapon_index -= 1
        if self.current_weapon_index < 0:
            self.current_weapon_index = len(self.available_weapons) - 1
        self.weapon = Weapon(
            self.available_weapons[self.current_weapon_index],
            self.sound
        )
        self.weapon.equip()


    def shoot_weapon(self, current_time):
        self.weapon.shoot(current_time)

    def reload_weapon(self):
        self.weapon.reload()
    
