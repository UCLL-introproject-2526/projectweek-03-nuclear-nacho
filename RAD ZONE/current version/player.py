import pygame
from weapon import Weapon


class Player:
    def __init__(self, surf, rect, sound):
        self._surf = surf
        self._rect = rect
        self.sound = sound

        self._was_mouse_pressed = False  # tracks mouse state for single-shot
        self.available_weapons = [
            "pistol",
            "rifle",
            "revolver",
            "shotgun",
            "knife"
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

    # -------- LOGIC --------
    def update(self, keys, dt, current_time):
        # ---- movement / stamina ----
        moving = keys[pygame.K_z] or keys[pygame.K_q] or keys[pygame.K_s] or keys[pygame.K_d]
        sprinting = keys[pygame.K_LSHIFT] and moving

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





    def draw(self, screen):
        screen.blit(self._surf, self._rect)

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
    
