import pygame

class Camera:
    def __init__(self, screen_w, screen_h):
        self._offset = pygame.Vector2()
        self._screen_center = pygame.Vector2(screen_w // 2, screen_h // 2)
        self._screen_w = screen_w
        self._screen_h = screen_h

    def update(self, target_pos: pygame.Vector2):
        # Camera offset = target - center
        self._offset.x = target_pos.x - self._screen_center.x
        self._offset.y = target_pos.y - self._screen_center.y

        # Clamp offset to map boundaries (7680x6400)
        self._offset.x = max(0, min(self._offset.x, 7680 - self._screen_w))
        self._offset.y = max(0, min(self._offset.y, 6400 - self._screen_h))

    def apply(self, rect: pygame.Rect) -> pygame.Rect:
        return rect.move(-self._offset.x, -self._offset.y)

    def get_position(self):
        return self._offset
