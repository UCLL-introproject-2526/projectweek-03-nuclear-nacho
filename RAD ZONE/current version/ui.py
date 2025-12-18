import pygame

class UI:
    def __init__(self, health, stamina, outline):
        self._health = health
        self._stamina = stamina
        self._outline = outline

        # Smooth display values (0-1)
        self._display_health = 1.0
        self._display_stamina = 1.0
        self._lerp_speed = 8  # snelheid van smooth lerp

    # -------- HEALTH BAR --------
    def draw_health(self, screen, health_value, dt=0):
        self._display_health += (health_value - self._display_health) * min(self._lerp_speed * dt, 1)
        ratio = max(0, min(self._display_health, 1))
        bar_pos = self._health[1].topleft

        screen.blit(self._health[0], bar_pos)
        if ratio > 0:
            width = int(self._health[0].get_width() * ratio)
            part = self._health[0].subsurface((0, 0, width, self._health[0].get_height()))
            screen.blit(part, bar_pos)
        screen.blit(self._outline[0], bar_pos)

    # -------- STAMINA BAR --------
    def draw_stamina(self, screen, stamina_value, dt=0):
        self._display_stamina += (stamina_value - self._display_stamina) * min(self._lerp_speed * dt, 1)
        ratio = max(0, min(self._display_stamina, 1))
        bar_pos = self._stamina[1].topleft

        screen.blit(self._stamina[0], bar_pos)
        if ratio > 0:
            width = int(self._stamina[0].get_width() * ratio)
            part = self._stamina[0].subsurface((0, 0, width, self._stamina[0].get_height()))
            screen.blit(part, bar_pos)
        screen.blit(self._outline[0], bar_pos)

    # -------- COMBINED DRAW --------
    def draw(self, screen, health_value, stamina_value, dt=0):
        self.draw_health(screen, health_value, dt=dt)
        self.draw_stamina(screen, stamina_value, dt=dt)
