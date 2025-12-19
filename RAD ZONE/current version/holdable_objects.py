import pygame
from sound_manager import SoundManager

# ------------------ WEAPON ------------------
class WeaponItem:
    def __init__(self, item_id, sound_manager=None, icon_surf=None, weapon_surf=None, char_weapon_surf=None):
        self._id = item_id
        self.icon_surf = icon_surf          # hotbar/inventory icon
        self.weapon_surf = weapon_surf      # full weapon image for world/pickup
        self.char_weapon_surf = char_weapon_surf  # player-held weapon image
        self._sound_manager = sound_manager
        self._position = pygame.Vector2(0, 0)





    # ------------------ INVENTORY / SLOT ------------------
    def get_char_weapon_surface(self):
        return self.char_weapon_surf

    def get_icon(self):
        return self.icon_surf

    def get_id(self):
        return self._id

    def is_stackable(self):
        return False  # Weapons are not stackable

    def get_amount(self):
        return 1  # Always 1 for weapons

    # ------------------ DRAG & DROP ------------------
    def set_position(self, pos):
        self._position = pygame.Vector2(pos)

    def get_position(self):
        return self._position

    # ------------------ WEAPON LOGIC ------------------
    def get_weapon(self):
        from weapon import Weapon
        return Weapon(self._id, self._sound_manager)

    def play_equip_sound(self):
        if self._sound_manager:
            self._sound_manager.play_weapon(self._id, "equip")


# ------------------ CONSUMABLE ITEM ------------------
class ConsumableItem:
    def __init__(self, item_id, *, sound_manager=None, icon_surf=None, stackable=True, amount=1, max_stack=1):
        self._id = item_id
        self._sound_manager = sound_manager
        self.icon_surf = icon_surf
        self.stackable = stackable
        self.amount = amount
        self.max_stack = max_stack
        self._position = pygame.Vector2(0, 0)

    # ------------------ INVENTORY / SLOT ------------------
    def get_icon(self):
        return self.icon_surf

    def get_id(self):
        return self._id

    def is_stackable(self):
        return self.stackable

    def get_amount(self):
        return self.amount

    # ------------------ DRAG & DROP ------------------
    def set_position(self, pos):
        self._position = pygame.Vector2(pos)

    def get_position(self):
        return self._position

    # ------------------ ITEM LOGIC ------------------
    def use(self, player):
        pass

    def play_pickup_sound(self):
        if self._sound_manager:
            self._sound_manager.play_item(f"pickup_{self._id}")
