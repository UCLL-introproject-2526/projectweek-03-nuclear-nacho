import pygame

class Slot:
    def __init__(self, socket_surf, center):
        self._base_surf = socket_surf
        self._surf = socket_surf
        self._rect = socket_surf.get_rect(center=center)
        self._item = None
        self._hovered = False

    # --- getters ---
    def get_item(self):
        return self._item

    def is_hovered(self):
        return self._hovered

    # --- setters ---
    def set_item(self, item):
        self._item = item
        if item:
            item.set_position(self._rect.center)

    def clear_item(self):
        self._item = None

    # --- logic ---
    def update(self, mouse_pos):
        self._hovered = self._rect.collidepoint(mouse_pos)

        scale = 1.1 if self._hovered else 1.0
        size = (
            int(self._base_surf.get_width() * scale),
            int(self._base_surf.get_height() * scale)
        )

        self._surf = pygame.transform.scale(self._base_surf, size)
        self._rect = self._surf.get_rect(center=self._rect.center)

    def draw(self, screen):
        screen.blit(self._surf, self._rect)

        if self._item:
            icon = self._item.get_icon()
            icon_rect = icon.get_rect(center=self._rect.center)
            screen.blit(icon, icon_rect)
