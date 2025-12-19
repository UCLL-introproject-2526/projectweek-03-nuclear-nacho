import pygame
import sys
import json
import os


class Scoreboard:
    def __init__(self, screen, score_file="scores.json"):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.score_file = score_file

        # Achtergrond
        self.background = pygame.image.load(
            "RAD ZONE/UI/Menu/achtergrond_scoreboard.png"
        ).convert()
        self.background = pygame.transform.scale(self.background, (self.width, self.height))

        # Font
        pygame.font.init()
        self.font = pygame.font.Font("RAD ZONE/UI/Menu/edit-undo.brk.ttf", 60)

        # Return knop afbeeldingen
        self.return_idle = pygame.image.load("RAD ZONE/UI/Menu/return_idle.png").convert_alpha()
        self.return_pressed = pygame.image.load("RAD ZONE/UI/Menu/return_pressed.png").convert_alpha()

        # Schaal zoals je menu-knoppen (1/6 van schermbreedte)
        button_width = self.width // 6

        def scale_button(img):
            ratio = button_width / img.get_width()
            new_height = int(img.get_height() * ratio)
            return pygame.transform.scale(img, (button_width, new_height))

        self.return_idle = scale_button(self.return_idle)
        self.return_pressed = scale_button(self.return_pressed)

        self.return_btn = {
            "idle": self.return_idle,
            "pressed": self.return_pressed,
            "current": self.return_idle,
            "rect": self.return_idle.get_rect(center=(self.width // 2, self.height - 120)),
            "down": False
        }

        # Laad scores
        self.load_scores()

    def load_scores(self):
        if not os.path.exists(self.score_file):
            self.scores = []
            return

        with open(self.score_file, "r") as f:
            try:
                self.scores = json.load(f)
            except json.JSONDecodeError:
                self.scores = []

        # Sorteer aflopend op score
        self.scores.sort(key=lambda x: x["score"], reverse=True)
        # Beperk tot top 10
        self.scores = self.scores[:10]

    # -----------------------------
    #   BUTTON HANDLING
    # -----------------------------
    def draw_button(self, btn):
        self.screen.blit(btn["current"], btn["rect"])

    def handle_button(self, btn, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if btn["rect"].collidepoint(event.pos):
                btn["current"] = btn["pressed"]
                btn["down"] = True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if btn["down"]:
                btn["current"] = btn["idle"]
                btn["down"] = False

                if btn["rect"].collidepoint(event.pos):
                    return True
        return False

    # -----------------------------
    #   DRAW
    # -----------------------------
    def draw(self):
        self.screen.blit(self.background, (0, 0))

        # Scores
        start_y = 300
        spacing = 70

        for i, entry in enumerate(self.scores):
            name = entry.get("name", "Unknown")
            score = entry.get("score", 0)
            text = f"{i+1}. {name} - {score}"
            label = self.font.render(text, True, (255, 255, 255))
            rect = label.get_rect(center=(self.width // 2, start_y + i * spacing))
            self.screen.blit(label, rect)

        # Return knop
        self.draw_button(self.return_btn)

        pygame.display.flip()

    # -----------------------------
    #   RUN LOOP
    # -----------------------------
    def run(self):
        while True:
            self.draw()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if self.handle_button(self.return_btn, event):
                    return  # terug naar hoofdmenu
