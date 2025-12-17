import pygame

class ImageLoader:
    @staticmethod
    def load(path, size=None, center=None):
        surf = pygame.image.load(path).convert_alpha()
        if size:
            surf = pygame.transform.scale(surf, size)
        rect = surf.get_rect()
        if center:
            rect.center = center
        return surf, rect
