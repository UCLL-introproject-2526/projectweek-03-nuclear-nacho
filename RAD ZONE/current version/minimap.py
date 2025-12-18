import pygame

class Minimap:
    def __init__(self, map_surf, buildings, screen_size):
        self._size = 220
        self._zoom = 0.1

        self._surf = pygame.Surface((self._size, self._size))
        self._rect = self._surf.get_rect(topright=(screen_size[0] - 20, 20))

        self._map = pygame.transform.smoothscale(
            map_surf,
            (int(map_surf.get_width() * self._zoom),
             int(map_surf.get_height() * self._zoom))
        )

        self._buildings = [
            (
                pygame.transform.smoothscale(
                    surf,
                    (int(surf.get_width() * self._zoom),
                    int(surf.get_height() * self._zoom))
                ),
                pygame.Vector2(pos)   # <-- FIX
            )
            for surf, pos in buildings
        ]


    def draw(self, screen, player_world_pos):
        self._surf.fill((0, 0, 0))

        player_mm = player_world_pos * self._zoom
        offset = pygame.Vector2(
            self._size // 2 - player_mm.x,
            self._size // 2 - player_mm.y
        )

        self._surf.blit(self._map, offset)

        for surf, pos in self._buildings:
            self._surf.blit(surf, pos * self._zoom + offset)

        pygame.draw.circle(
            self._surf, (0, 255, 0),
            (self._size // 2, self._size // 2), 3
        )

        pygame.draw.rect(self._surf, (200, 200, 200), self._surf.get_rect(), 2)
        screen.blit(self._surf, self._rect)
