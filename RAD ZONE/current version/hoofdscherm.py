import pygame
import sys

class Menu:
    def __init__(self, screen, items):
        self.screen = screen
        self.items = items
        self.selected = 0

        self.width, self.height = self.screen.get_size()

        # Achtergrond
        self.background = pygame.image.load("RAD ZONE/current version/Graphics/menu_background.png").convert()
        self.background = pygame.transform.scale(self.background, (self.width, self.height))

        # Fonts
        self.title_font = pygame.font.SysFont(None, 120)
        self.item_font = pygame.font.SysFont(None, 70)

        # Colors
        self.text_color = (255, 255, 255)
        self.highlight_color = (255, 140, 0)

    def draw(self):
        # Achtergrond tekenen
        self.screen.blit(self.background, (0, 0))

        # Title
        title = self.title_font.render("RAD ZONE", True, self.highlight_color)
        title_rect = title.get_rect(center=(self.width // 2, 150))
        self.screen.blit(title, title_rect)

        # Menu items
        start_y = 300
        spacing = 90

        mouse_pos = pygame.mouse.get_pos()

        for i, text in enumerate(self.items):
            color = self.text_color

            item_rect = pygame.Rect(0, 0, 400, 70)
            item_rect.center = (self.width // 2, start_y + i * spacing)

            if item_rect.collidepoint(mouse_pos) or i == self.selected:
                color = self.highlight_color

            label = self.item_font.render(text, True, color)
            label_rect = label.get_rect(center=item_rect.center)

            self.screen.blit(label, label_rect)

        pygame.display.flip()

    def run(self):
        while True:
            self.draw()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected = (self.selected - 1) % len(self.items)
                    if event.key == pygame.K_DOWN:
                        self.selected = (self.selected + 1) % len(self.items)
                    if event.key == pygame.K_RETURN:
                        return self.items[self.selected]

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()

                    start_y = 300
                    spacing = 90

                    for i, text in enumerate(self.items):
                        item_rect = pygame.Rect(0, 0, 400, 70)
                        item_rect.center = (self.width // 2, start_y + i * spacing)

                        if item_rect.collidepoint(mouse_pos):
                            return text
