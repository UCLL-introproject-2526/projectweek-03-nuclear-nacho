import pygame
import os

# ---------- CONSTANTS ----------
FRAME_W, FRAME_H = 32, 32
SCALE = 4
ANIM_FPS = 10

DIRECTIONS = ["front", "back", "right", "left"]


# ---------- HELPERS ----------
def load_sheet_anim(path, frames_per_dir):
    """
    Laadt een sprite sheet met:
    - rijen = richtingen (in volgorde van DIRECTIONS: front, back, right, left)
    - kolommen = frames per richting
    Retourneert: dict met direction -> list[scaled Surface]
    """
    # Controleer of het bestand bestaat
    if not os.path.exists(path):
        raise FileNotFoundError(f"Sprite sheet niet gevonden: {path}")

    sheet = pygame.image.load(path).convert_alpha()
    sheet_width, sheet_height = sheet.get_size()

    expected_width = frames_per_dir * FRAME_W
    expected_height = len(DIRECTIONS) * FRAME_H

    if sheet_width < expected_width or sheet_height < expected_height:
        raise ValueError(
            f"Sprite sheet te klein: {sheet_width}x{sheet_height}. "
            f"Verwacht minimaal {expected_width}x{expected_height} voor {frames_per_dir} frames per richting."
        )

    animations = {}

    for row, direction in enumerate(DIRECTIONS):
        frames = []
        for col in range(frames_per_dir):
            # Knip frame uit sheet
            frame = pygame.Surface((FRAME_W, FRAME_H), pygame.SRCALPHA)
            frame.blit(
                sheet,
                (0, 0),
                (col * FRAME_W, row * FRAME_H, FRAME_W, FRAME_H)
            )
            # Scale naar schermgrootte
            scaled_frame = pygame.transform.scale(
                frame,
                (FRAME_W * SCALE, FRAME_H * SCALE)
            )
            frames.append(scaled_frame)

        animations[direction] = frames

    return animations


# ---------- ANIMATOR CLASS ----------
class Animator:
    def __init__(self, assets_path):
        self.state = "idle"
        self.direction = "front"
        self.frame_index = 0.0

        self.animations = {
            "idle": load_sheet_anim("RAD ZONE/current version/Graphics/Idle.png", frames_per_dir=1),
            "walk": load_sheet_anim("RAD ZONE/current version/Graphics/Walk.png", frames_per_dir=3),
            "stab": load_sheet_anim("RAD ZONE/current version/Graphics/Stab.png", frames_per_dir=4),
        }

        self.image = self.animations["idle"]["front"][0]


    def update(self, velocity: pygame.Vector2, dt: float, current_time: float = 0, override_stab: bool = False):
        """Update animation frames"""

        # If Player is stabbing, keep stab animation
        if override_stab:
            self.state = "stab"
            frames = self.animations[self.state][self.direction]
            self.frame_index = (self.frame_index + ANIM_FPS * dt) % len(frames)
            self.image = frames[int(self.frame_index)]
            return

        # Normal movement/idle animation
        if velocity.length() > 0:
            self.state = "walk"
            if abs(velocity.x) > abs(velocity.y):
                self.direction = "right" if velocity.x > 0 else "left"
            else:
                self.direction = "front" if velocity.y > 0 else "back"
        else:
            self.state = "idle"
            self.frame_index = 0

        frames = self.animations[self.state][self.direction]
        self.frame_index = (self.frame_index + ANIM_FPS * dt) % len(frames)
        self.image = frames[int(self.frame_index)]

    def play_stab(self):
        self.state = "stab"
        self.frame_index = 0


    def get_image(self) -> pygame.Surface:
        return self.image
