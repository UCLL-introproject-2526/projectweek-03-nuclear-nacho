import pygame
import json
from sys import exit

class CommitScoreScreen:
    def __init__(self, screen, score):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.width, self.height = screen.get_size()
        self.score = score

        # Letters en cijfers
        self.characters = [chr(i) for i in range(65, 91)]  # A-Z
        self.characters += [str(i) for i in range(10)]     # 0-9
        self.characters.append("OK")                        # Confirm button

        # Layout
        self.cols = 10
        self.rows = (len(self.characters) + self.cols - 1) // self.cols
        self.cell_width = self.width // self.cols
        self.cell_height = 60

        # Cursor positie
        self.cursor_x = 0
        self.cursor_y = 0

        # Naam die speler aan het invoeren is
        self.name = []

        # Font
        self.font = pygame.font.Font("RAD ZONE/UI/Menu/edit-undo.brk.ttf", 60)

    def draw(self):
        self.screen.fill((20, 20, 20))

        # Titel en score
        title = self.font.render("Enter your initials (MAX 3)", True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(center=(self.width // 2, 50)))

        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 0))
        self.screen.blit(score_text, score_text.get_rect(center=(self.width // 2, 100)))

        # Toon huidige naam
        name_text = self.font.render("".join(self.name), True, (0, 255, 0))
        self.screen.blit(name_text, name_text.get_rect(center=(self.width // 2, 150)))

        # Teken karakter raster
        for idx, char in enumerate(self.characters):
            col = idx % self.cols
            row = idx // self.cols
            x = col * self.cell_width + self.cell_width // 2
            y = 200 + row * self.cell_height
            color = (255, 255, 255)
            # Cursor highlight
            if col == self.cursor_x and row == self.cursor_y:
                color = (255, 0, 0)
            char_surf = self.font.render(char, True, color)
            self.screen.blit(char_surf, char_surf.get_rect(center=(x, y)))

        pygame.display.flip()

    def run(self):
        while True:
            self.clock.tick(60)
            self.draw()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if event.type == pygame.KEYDOWN:
                    # Navigatie
                    if event.key == pygame.K_LEFT:
                        self.cursor_x = (self.cursor_x - 1) % self.cols
                        self._clamp_cursor()
                    elif event.key == pygame.K_RIGHT:
                        self.cursor_x = (self.cursor_x + 1) % self.cols
                        self._clamp_cursor()
                    elif event.key == pygame.K_UP:
                        self.cursor_y = (self.cursor_y - 1) % self.rows
                        self._clamp_cursor()
                    elif event.key == pygame.K_DOWN:
                        self.cursor_y = (self.cursor_y + 1) % self.rows
                        self._clamp_cursor()

                    # Selecteer
                    elif event.key == pygame.K_RETURN:
                        idx = self.cursor_y * self.cols + self.cursor_x
                        if idx >= len(self.characters):
                            continue
                        char = self.characters[idx]

                        if char == "OK":
                            player_name = "".join(self.name)
                            self.save_score(player_name, self.score)
                            return player_name
                        else:
                            if len(self.name) < 3:  # Max 3 letters/cijfers
                                self.name.append(char)

                    # Verwijder laatste
                    elif event.key == pygame.K_BACKSPACE:
                        if self.name:
                            self.name.pop()

    def _clamp_cursor(self):
        """Zorg dat de cursor niet buiten het character grid komt."""
        idx = self.cursor_y * self.cols + self.cursor_x
        if idx >= len(self.characters):
            # Zet cursor op laatste karakter
            last_idx = len(self.characters) - 1
            self.cursor_y = last_idx // self.cols
            self.cursor_x = last_idx % self.cols

    def save_score(self, name, score):
        try:
            with open("RAD ZONE/current version/scores.json", "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = []
        except json.JSONDecodeError:
            data = []

        data.append({"name": name, "score": score})
        with open("scores.json", "w") as f:
            json.dump(data, f, indent=4)