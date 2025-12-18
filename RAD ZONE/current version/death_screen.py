import pygame
from sys import exit

class DeathScreen:
    def __init__(self, screen, zombies_killed):
        self.screen = screen
        self.zombies_killed = zombies_killed
        self.font = pygame.font.SysFont(None, 64)
        self.small_font = pygame.font.SysFont(None, 40)
        self.button_rect = pygame.Rect(0, 0, 200, 60)
        w, h = self.screen.get_size()
        self.button_rect.center = (w // 2, h // 2 + 100)

    def run(self):
        clock = pygame.time.Clock()
        while True:
            dt = clock.tick(60) / 1000
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()[0]

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            # Tekst
            self.screen.fill((0, 0, 0))
            title_text = self.font.render("You Died!", True, (255, 0, 0))
            score_text = self.small_font.render(f"Zombies killed: {self.zombies_killed}", True, (255, 255, 255))
            self.screen.blit(title_text, title_text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2 - 100)))
            self.screen.blit(score_text, score_text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2 - 30)))

            # Button
            pygame.draw.rect(self.screen, (200, 200, 200), self.button_rect)
            button_text = self.small_font.render("Return", True, (0, 0, 0))
            self.screen.blit(button_text, button_text.get_rect(center=self.button_rect.center))

            # Check klik
            if mouse_pressed and self.button_rect.collidepoint(mouse_pos):
                return "Return"

            pygame.display.flip()
