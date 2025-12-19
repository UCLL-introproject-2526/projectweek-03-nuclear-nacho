import pygame
from hoofdscherm import ImageButton, scale_image

class PauseMenu:
    def __init__(self, screen):
        self.screen = screen
        w, h = self.screen.get_size()
        self.width, self.height = w, h

        # Knoppen laden
        base = "RAD ZONE/UI/Menu/"
        button_width = w // 4
        self.buttons = {}

        button_names = ["Resume", "Quit"]
        start_y = 250
        spacing = int(h * 0.12)
        center_x = w // 2

        for i, name in enumerate(button_names):
            idle = scale_image(pygame.image.load(base + f"{name.lower()}_idle.png").convert_alpha(), width=button_width)
            pressed = scale_image(pygame.image.load(base + f"{name.lower()}_pressed.png").convert_alpha(), width=button_width)
            self.buttons[name] = ImageButton(center_x, start_y + spacing * i, idle, pressed)

    def draw(self, game_surface):
        # Grijs overlay
        overlay = pygame.Surface(self.screen.get_size())
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        self.screen.blit(game_surface, (0, 0))
        self.screen.blit(overlay, (0, 0))

        for btn in self.buttons.values():
            btn.draw(self.screen)
        pygame.display.flip()

    def run(self, game_surface):
        while True:
            self.draw(game_surface)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                for name, btn in self.buttons.items():
                    if btn.handle_event(event):
                        return name
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return "Resume"
