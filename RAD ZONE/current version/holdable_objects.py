import pygame
from weapon import Weapon

# ------------------------------
#       BASE CLASS
# ------------------------------
class Holdable:
    """Base class for anything the player can hold/equip."""
    def __init__(self, item_id, icon_surf=None, char_weapon_surf=None):
        self._id = item_id
        self._icon = icon_surf
        self._char_weapon = char_weapon_surf
        self._rect = None
        if icon_surf:
            self._rect = icon_surf.get_rect()



    def get_id(self):
        return self._id

    def get_icon(self):
        return self._icon

    def get_char_weapon_surface(self):
        return self._char_weapon
    
        # -------------------------
    # Added for drag & drop support
    # -------------------------
    def set_position(self, pos):
        if self._rect:
            self._rect.center = pos

    def get_position(self):
        if self._rect:
            return self._rect.center
        return None
    
    def is_stackable(self):
        return False
    
    def get_amount(self):
        return 1

# ------------------------------
#       WEAPON ITEM
# ------------------------------
class WeaponItem(Holdable):
    """Wraps a Weapon so it can be equipped in inventory/hotbar."""
    def __init__(self, weapon_id, sound_manager, icon_surf=None, char_weapon_surf=None):
        super().__init__(weapon_id, icon_surf, char_weapon_surf)
        self._weapon = Weapon(weapon_id, sound_manager)
        self._sound_manager = sound_manager

    def get_weapon(self):
        return self._weapon

    def equip(self):
        """Play equip sound via Weapon class."""
        if self._weapon:
            self._weapon.equip()

    def play_equip_sound(self):
        """Play equip sound from sound manager."""
        if self._sound_manager:
            self._sound_manager.play_weapon(self._id, "equip")

# ------------------------------
#     CONSUMABLE ITEM
# ------------------------------
class ConsumableItem(Holdable):
    def __init__(self, item_id, sound_manager, icon_surf=None,
                 stackable=False, amount=1, max_stack=1):
        super().__init__(item_id, icon_surf)
        self._sound_manager = sound_manager
        self._stackable = stackable
        self._amount = amount
        self._max_stack = max_stack

    # Stack logic
    def can_stack_with(self, other):
        return (
            other
            and self._stackable
            and other.get_id() == self._id
            and other.get_amount() < other.get_max_stack()
        )

    def add_to_stack(self, amount):
        space = self._max_stack - self._amount
        added = min(space, amount)
        self._amount += added
        return added

    def remove_from_stack(self, amount):
        self._amount -= amount
        return self._amount <= 0

    def get_amount(self):
        return self._amount

    def get_max_stack(self):
        return self._max_stack

    def is_stackable(self):
        return self._stackable
