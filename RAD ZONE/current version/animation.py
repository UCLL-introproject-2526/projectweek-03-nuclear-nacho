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
        """
        assets_path wordt momenteel niet gebruikt (legacy), maar behouden voor compatibiliteit.
        Idle, Walk en Stab sheets worden hard-coded geladen.
        """
        self.state = "idle"
        self.direction = "front"
        self.frame_index = 0.0

        try:
            self.animations = {
                "idle": load_sheet_anim(
                    os.path.join("RAD ZONE", "current version", "Graphics", "Idle.png"), 
                    frames_per_dir=1
                ),
                "walk": load_sheet_anim(
                    os.path.join("RAD ZONE", "current version", "Graphics", "Walk.png"), 
                    frames_per_dir=3
                ),
                "stab": load_sheet_anim(
                    os.path.join("RAD ZONE", "current version", "Graphics", "Stab.png"), 
                    frames_per_dir=4
                ),
            }
            print("[OK] Idle, Walk en Stab animaties geladen")
        except Exception as e:
            print(f"[FOUT] Kon Idle/Walk/Stab sheets niet laden: {e}")
            # Fallback: lege afbeelding zodat game niet crasht
            empty = pygame.Surface((FRAME_W * SCALE, FRAME_H * SCALE), pygame.SRCALPHA)
            self.animations = {
                "idle": {"front": [empty]},
                "walk": {"front": [empty]},
                "stab": {"front": [empty]}
            }

        self.image = self.animations["idle"]["front"][0]
        self.stab_end_time = 0  # When stab animation ends

    def update(self, velocity: pygame.Vector2, dt: float, current_time: float = 0):
        """
        Update animatie op basis van beweging.
        """
        # Check if stab animation is still playing
        if self.state == "stab" and current_time < self.stab_end_time:
            # Continue stab animation
            frames = self.animations[self.state][self.direction]
            self.frame_index = (self.frame_index + ANIM_FPS * dt) % len(frames)
            self.image = frames[int(self.frame_index)]
            return
        
        # Stab animation finished, return to normal animation
        if self.state == "stab":
            self.state = "idle"
            self.frame_index = 0
        
        if velocity.length() > 0:
            self.state = "walk"
            # Bepaal richting
            if abs(velocity.x) > abs(velocity.y):
                self.direction = "right" if velocity.x > 0 else "left"
            else:
                self.direction = "front" if velocity.y > 0 else "back"
        else:
            self.state = "idle"
            self.frame_index = 0  # altijd eerste idle frame

        # Frame vooruitspoelen
        frames = self.animations[self.state][self.direction]
        self.frame_index = (self.frame_index + ANIM_FPS * dt) % len(frames)
        self.image = frames[int(self.frame_index)]

    def play_stab(self, current_time: float, duration: float = 1.0):
        """
        Start playing the stab animation.
        current_time: current game time in seconds
        duration: how long the stab animation should play
        """
        self.state = "stab"
        self.frame_index = 0
        self.stab_end_time = current_time + duration

    def get_image(self) -> pygame.Surface:
        return self.image
