import pygame
from sys import exit
from hoofdscherm import ImageButton, scale_image

class CreditsScreen:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.clock = pygame.time.Clock()

        # Achtergrond zwart
        self.background = pygame.Surface((self.width, self.height))
        self.background.fill((0, 0, 0))

        # Fonts
        self.title_font = pygame.font.Font("RAD ZONE/UI/Menu/edit-undo.brk.ttf", 50)  # Tussentitels
        self.text_font = pygame.font.Font("RAD ZONE/UI/Menu/edit-undo.brk.ttf", 40)   # Normale tekst

        # Credits tekst (type, line)
        self.credits = [
            ("title", "The team behind Rad zone:"),
            ("text", "Keanu Aleart"),
            ("text", "Manu De Smedt"),
            ("text", "Esper Merckx"),
            ("text", "Michiel Vanmossevelde"),
            ("text", "Wouter Wingels"),
            ("title", "Verdeling taken from projectweek:"),
            ("text", "Graphic Design: Michiel, Esper, Keanu"),
            ("text", "Programming: Wouter, Keanu, Manu, Esper, Michiel"),
            ("text", "Soundtrack Design: Manu, Michiel"),
            ("text", "Sound Design: Manu"),
            ("text", "Voice Acting: Esper, Wouter, Keanu, Manu, Michiel"),
            ("title", "Websites that helped us:"),
            ("title", "Sound effects:"),
            ("text", "pixabay.com"),
            ("title", "Sprites: (Itch.io)"),
            ("text", "Goncharov_Denis"),
            ("text", "ArcadeIsland"),
            ("text", "RanitayaStudio"),
            ("text", "JackBurton84"),
            ("text", "CraftPix.net"),
            ("title", "Gen AI"),
            ("text", "ChatGPT"),
            ("text", "Gemini AI"),
            ("text", "Microsoft copilot"),
        ]

        # Scroll instellingen
        self.start_y = self.height
        self.scroll_speed = 1  # pixels per frame
        self.line_spacing_title = 60
        self.line_spacing_text = 40
        self.line_spacing_section = 100

        # Quit-knop PNG
        base_path = "RAD ZONE/UI/Menu/"
        button_width = self.width // 6
        idle_img = scale_image(pygame.image.load(base_path + "return_idle.png").convert_alpha(), width=button_width)
        pressed_img = scale_image(pygame.image.load(base_path + "return_pressed.png").convert_alpha(), width=button_width)
        self.quit_btn = ImageButton(self.width // 2, self.height - 50, idle_img, pressed_img)

        # Soundtrack starten vanaf bepaald punt, loopend
        pygame.mixer.init()
        pygame.mixer.music.load("RAD ZONE\current version\MP3\RAD_ZONE_SOUNDTRACK.mp3")
        pygame.mixer.music.play(loops=-1, start=30)  # start op 30 seconden, herhaling oneindig

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        y = self.start_y
        prev_type = None

        # Tekst tekenen
        for typ, line in self.credits:
            # Extra spatie tussen secties
            if typ == "title" and prev_type == "text":
                y += self.line_spacing_section

            # Renderen
            if typ == "title":
                surf = self.title_font.render(line, True, (255, 255, 255))
                y += self.line_spacing_title
            else:
                surf = self.text_font.render(line, True, (200, 200, 200))
                y += self.line_spacing_text

            rect = surf.get_rect(center=(self.width // 2, y))
            self.screen.blit(surf, rect)
            prev_type = typ

        # Scroll positie update
        self.start_y -= self.scroll_speed

        # Reset scroll wanneer alles voorbij is
        total_height = y + 100  # extra marge onderaan
        if total_height < 0:
            self.start_y = self.height

        # Quit-knop tekenen
        self.quit_btn.draw(self.screen)
        pygame.display.flip()

    def run(self):
        while True:
            dt = self.clock.tick(60)
            self.draw()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.mixer.music.stop()
                    pygame.quit()
                    exit()
                if self.quit_btn.handle_event(event):
                    pygame.mixer.music.stop()
                    return
