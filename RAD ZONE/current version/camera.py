import pygame

class Camera:
    def __init__(self, screen_w, screen_h):
        self._offset = pygame.Vector2()
        self._screen_center = pygame.Vector2(screen_w // 2, screen_h // 2)

    def update(self, target_pos: pygame.Vector2):
        # Camera offset = target - center
        self._offset.x = target_pos.x - self._screen_center.x
        self._offset.y = target_pos.y - self._screen_center.y

    def apply(self, rect: pygame.Rect) -> pygame.Rect:
        return rect.move(-self._offset.x, -self._offset.y)

    def get_position(self):
        return self._offset
