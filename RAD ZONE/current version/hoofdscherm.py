import pygame
import sys


# -----------------------------
#   SCALE FUNCTION
# -----------------------------
def scale_image(img, width=None, height=None):
    """Schaalt een afbeelding met behoud van aspect ratio."""
    if width is not None and height is None:
        ratio = width / img.get_width()
        height = int(img.get_height() * ratio)

    if height is not None and width is None:
        ratio = height / img.get_height()
        width = int(img.get_width() * ratio)

    return pygame.transform.scale(img, (width, height))


# -----------------------------
#   IMAGE BUTTON (NO HOVER)
# -----------------------------
class ImageButton:
    def __init__(self, x, y, idle_img, pressed_img):
        self.idle = idle_img
        self.pressed = pressed_img

        self.current = self.idle
        self.rect = self.current.get_rect(center=(x, y))

        self.is_down = False

    def draw(self, screen):
        screen.blit(self.current, self.rect)

    def handle_event(self, event):
        # MOUSE DOWN
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.current = self.pressed
                self.is_down = True

        # MOUSE UP
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_down:
                self.current = self.idle
                self.is_down = False

                if self.rect.collidepoint(event.pos):
                    return True  # CLICKED

        return False


# -----------------------------
#            MENU
# -----------------------------
class Menu:
    def __init__(self, screen, items):
        self.screen = screen
        self.items = items  # ["Play", "Scoreboard", "Settings", "Credits", "Quit"]
        self.width, self.height = self.screen.get_size()

        # Achtergrond
        self.background = pygame.image.load(
            "RAD ZONE/UI/Menu/achtergrond menu.png"
        ).convert()
        self.background = pygame.transform.scale(self.background, (self.width, self.height))

        # -----------------------------
        #   LOAD & SCALE BUTTON IMAGES
        # -----------------------------
        base = "RAD ZONE/UI/Menu/"

        button_width = self.width // 4  # 25% van schermbreedte

        self.play_idle = scale_image(
            pygame.image.load(base + "play_idle.png").convert_alpha(),
            width=button_width
        )
        self.play_pressed = scale_image(
            pygame.image.load(base + "play_pressed.png").convert_alpha(),
            width=button_width
        )

        self.scoreboard_idle = scale_image(
            pygame.image.load(base + "scoreboard_idle.png").convert_alpha(),
            width=button_width
        )
        self.scoreboard_pressed = scale_image(
            pygame.image.load(base + "scoreboard_pressed.png").convert_alpha(),
            width=button_width
        )

        self.settings_idle = scale_image(
            pygame.image.load(base + "settings_idle.png").convert_alpha(),
            width=button_width
        )
        self.settings_pressed = scale_image(
            pygame.image.load(base + "settings_pressed.png").convert_alpha(),
            width=button_width
        )

        self.credits_idle = scale_image(
            pygame.image.load(base + "credits_idle.png").convert_alpha(),
            width=button_width
        )
        self.credits_pressed = scale_image(
            pygame.image.load(base + "credits_pressed.png").convert_alpha(),
            width=button_width
        )

        self.quit_idle = scale_image(
            pygame.image.load(base + "quit_idle.png").convert_alpha(),
            width=button_width
        )
        self.quit_pressed = scale_image(
            pygame.image.load(base + "quit_pressed.png").convert_alpha(),
            width=button_width
        )

        # -----------------------------
        #   CREATE BUTTON OBJECTS
        # -----------------------------
        center_x = self.width // 2
        start_y = 350
        spacing = int(self.height * 0.12)  # dynamische spacing

        self.buttons = {
            "Play": ImageButton(center_x, start_y + spacing * 0, self.play_idle, self.play_pressed),
            "Scoreboard": ImageButton(center_x, start_y + spacing * 1, self.scoreboard_idle, self.scoreboard_pressed),
            "Settings": ImageButton(center_x, start_y + spacing * 2, self.settings_idle, self.settings_pressed),
            "Credits": ImageButton(center_x, start_y + spacing * 3, self.credits_idle, self.credits_pressed),
            "Quit": ImageButton(center_x, start_y + spacing * 4, self.quit_idle, self.quit_pressed),
        }

    # -----------------------------
    #           DRAW MENU
    # -----------------------------
    def draw(self):
        self.screen.blit(self.background, (0, 0))

        # Draw all buttons
        for btn in self.buttons.values():
            btn.draw(self.screen)

        pygame.display.flip()

    # -----------------------------
    #           RUN LOOP
    # -----------------------------
    def run(self):
        while True:
            self.draw()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Check button clicks
                for name, btn in self.buttons.items():
                    if btn.handle_event(event):
                        return name
