import pygame
from sys import exit
from hoofdscherm import ImageButton, scale_image  # hergebruik van jouw ImageButton class

class DeathScreen:
    def __init__(self, screen, zombies_killed):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.kills = zombies_killed
        self.width, self.height = screen.get_size()

        # ----------------------------
        # Achtergrond overlay
        # ----------------------------
        self.overlay = pygame.Surface((self.width, self.height))
        self.overlay.set_alpha(150)  # doorzichtige overlay
        self.overlay.fill((0, 0, 0))  # zwart met transparantie

        # ----------------------------
        # Buttons
        # ----------------------------
        base = "RAD ZONE/UI/Menu/"
        button_width = self.width // 4
        start_y = 350
        spacing = int(self.height * 0.12)
        center_x = self.width // 2

        # Knoppen
        self.buttons = {}
        button_names = ["Play", "CommitScore", "Quit"]

        for i, name in enumerate(button_names):
            idle = scale_image(pygame.image.load(base + f"{name.lower()}_idle.png").convert_alpha(), width=button_width)
            pressed = scale_image(pygame.image.load(base + f"{name.lower()}_pressed.png").convert_alpha(), width=button_width)
            self.buttons[name] = ImageButton(center_x, start_y + spacing * i, idle, pressed)

        # Fonts
        self.font_big =  pygame.font.Font("RAD ZONE/UI/Menu/edit-undo.brk.ttf", 80)
        self.font_small = pygame.font.Font("RAD ZONE/UI/Menu/edit-undo.brk.ttf", 40)

    def draw(self, game_surface):
        # Achtergrond overlay
        self.screen.blit(game_surface, (0, 0))
        self.screen.blit(self.overlay, (0, 0))

        # Titel en score
        title = self.font_big.render("YOU DIED", True, (200, 0, 0))
        score = self.font_small.render(f"Zombies killed: {self.kills}", True, (255, 255, 255))

        self.screen.blit(title, title.get_rect(center=(self.width // 2, 150)))
        self.screen.blit(score, score.get_rect(center=(self.width // 2, 250)))

        # Draw buttons
        for name, btn in self.buttons.items():
            btn.draw(self.screen)

        pygame.display.flip()

    def run(self, game_surface):
        while True:
            self.clock.tick(60)
            self.draw(game_surface)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                for name, btn in self.buttons.items():
                    if btn.handle_event(event):
                        return name

                # Escape terug naar hoofdmenu (optioneel)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return "Quit"
