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
    Loads a sprite sheet with rows = directions and columns = frames
    Returns: dict[direction] -> list[Surface]
    """
    sheet = pygame.image.load(path).convert_alpha()
    animations = {}

    for row, direction in enumerate(DIRECTIONS):
        frames = []
        for col in range(frames_per_dir):
            frame = pygame.Surface((FRAME_W, FRAME_H), pygame.SRCALPHA)

            frame.blit(
                sheet,
                (0, 0),
                (col * FRAME_W, row * FRAME_H, FRAME_W, FRAME_H)
            )

            frame = pygame.transform.scale(
                frame,
                (FRAME_W * SCALE, FRAME_H * SCALE)
            )

            frames.append(frame)

        animations[direction] = frames

    return animations


# ---------- ANIMATOR ----------
class Animator:
    def __init__(self, assets_path):
        self.state = "idle"
        self.direction = "front"
        self.frame_index = 0.0

        self.animations = {
            "idle": load_sheet_anim(os.path.join("RAD ZONE\current version\Graphics\Idle.png"), 1),
            "walk": load_sheet_anim(os.path.join("RAD ZONE\current version\Graphics\Walk.png"), 3),
        }

        self.image = self.animations["idle"]["front"][0]

    def update(self, velocity: pygame.Vector2, dt: float):
        """
        Updates animation based on movement direction and speed.
        """
        # ----- STATE & DIRECTION -----
        if velocity.length() > 0:
            self.state = "walk"
            if abs(velocity.x) > abs(velocity.y):
                self.direction = "right" if velocity.x > 0 else "left"
            else:
                self.direction = "front" if velocity.y > 0 else "back"
        else:
            self.state = "idle"
            self.frame_index = 0  # snap to first idle frame

        # ----- FRAME ADVANCE -----
        frames = self.animations[self.state][self.direction]
        self.frame_index = (self.frame_index + ANIM_FPS * dt) % len(frames)
        self.image = frames[int(self.frame_index)]

    def get_image(self) -> pygame.Surface:
        return self.image
