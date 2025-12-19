import pygame
from slot import Slot
from holdable_objects import WeaponItem, ConsumableItem

# Weapon IDs that go in the hotbar
WEAPON_IDS = ["knife", "pistol", "rifle", "revolver", "shotgun", "crossbow"]

class Inventory:
    def __init__(self, socket_surf, item_data, screen_size, inventory_bg, hotbar_bg, player):
        self._player = player
        self._selected_hotbar = 0
        w, h = screen_size

        # Open state
        self._open = False

        # Slots
        self._inventory_slots = []
        self._hotbar_slots = []

        # Drag & drop
        self._dragged_item = None
        self._drag_origin = None
        self._equipped_item = None
        self._mouse_down_prev = False

        # UI SCALE
        self._ui_scale = 1.35
        base_size, base_gap = 64, 10
        size = int(base_size * self._ui_scale)
        gap = int(base_gap * self._ui_scale)

        self._socket_surf = pygame.transform.scale(socket_surf, (size, size))

        # Inventory grid
        cols, rows = 4, 4
        inv_width = cols * size + (cols - 1) * gap
        inv_height = rows * size + (rows - 1) * gap
        start_x = (w - inv_width) // 2 + size // 2
        start_y = (h - inv_height) // 2 + size // 2

        # Hotbar
        hotbar_slots = 5
        hotbar_width = hotbar_slots * size + (hotbar_slots - 1) * gap
        hotbar_y = h - int(100 * self._ui_scale)
        hotbar_start_x = (w - hotbar_width) // 2 + size // 2

        # Backgrounds
        self._inventory_bg = pygame.transform.scale(
            inventory_bg, (inv_width + int(size*1.6), inv_height + int(size*1.6))
        )
        self._hotbar_bg = pygame.transform.scale(
            hotbar_bg, (hotbar_width + int(size*0.4), size + int(size*0.3))
        )

        self._inventory_bg_rect = self._inventory_bg.get_rect(center=(w//2 + int(size*0.3), h//2 + int(size*0.67)))
        self._hotbar_bg_rect = self._hotbar_bg.get_rect(center=(w//2, hotbar_y))

        # Create inventory slots
        for row in range(rows):
            for col in range(cols):
                pos = (start_x + col * (size + gap), start_y + row * (size + gap))
                self._inventory_slots.append(Slot(self._socket_surf, pos))

        # Create hotbar slots
        for i in range(hotbar_slots):
            pos = (hotbar_start_x + i * (size + gap), hotbar_y)
            self._hotbar_slots.append(Slot(self._socket_surf, pos))

        # ---------------- SPAWN ITEMS ----------------
        inventory_index = 0
        hotbar_index = 0

        for item_id, data in item_data.items():
            if item_id in WEAPON_IDS:
                # Create a WeaponItem
                item = WeaponItem(
                    item_id,
                    self._player.sound,
                    icon_surf=data["icon"],
                    char_weapon_surf=data.get("char_weapon")
                )
                # Fill hotbar first
                if hotbar_index < len(self._hotbar_slots):
                    self._hotbar_slots[hotbar_index].set_item(item)
                    if hotbar_index == 0:
                        # Auto-equip first weapon
                        self._equipped_item = item
                        self._player.set_equipped_item(item, play_sound=False)
                    hotbar_index += 1
            else:
                # Create a ConsumableItem
                item = ConsumableItem(
                    item_id,
                    self._player.sound,
                    icon_surf=data["icon"],
                    stackable=data.get("stackable", False),
                    amount=data.get("amount", 1),
                    max_stack=data.get("max_stack", 1)
                )
                # Fill inventory slots
                if inventory_index < len(self._inventory_slots):
                    self._inventory_slots[inventory_index].set_item(item)
                    inventory_index += 1

    # ---------- GETTERS ----------
    def get_equipped_item(self):
        return self._equipped_item

    # ---------- TOGGLE ----------
    def toggle(self):
        self._open = not self._open

    def select_next(self):
        self._selected_hotbar = (self._selected_hotbar + 1) % len(self._hotbar_slots)
        new_item = self._hotbar_slots[self._selected_hotbar].get_item()
        self._equipped_item = new_item
        self._player.set_equipped_item(new_item, play_sound=True)

    def select_previous(self):
        self._selected_hotbar = (self._selected_hotbar - 1) % len(self._hotbar_slots)
        new_item = self._hotbar_slots[self._selected_hotbar].get_item()
        self._equipped_item = new_item
        self._player.set_equipped_item(new_item, play_sound=True)

    # ---------- UPDATE ----------
    def update(self, mouse_pos, mouse_down, mouse_up):
        press = mouse_down and not self._mouse_down_prev
        release = (not mouse_down) and self._mouse_down_prev
        self._mouse_down_prev = mouse_down

        # Inventory slots drag & drop only inside inventory
        if self._open:
            slots = self._inventory_slots
        else:
            slots = []

        # Update hover states for inventory
        for slot in slots:
            slot.update(mouse_pos)

        # PICK UP ITEM (inventory only)
        if press and not self._dragged_item:
            for slot in slots:
                if slot.is_hovered() and slot.get_item():
                    self._dragged_item = slot.get_item()
                    self._drag_origin = slot
                    slot.clear_item()
                    break

        # DROP ITEM (inventory only)
        if release and self._dragged_item:
            target_slot = None
            for slot in slots:
                if slot.is_hovered():
                    target_slot = slot
                    break

            if target_slot is None:
                self._drag_origin.set_item(self._dragged_item)
            else:
                target_item = target_slot.get_item()
                if target_item is None:
                    target_slot.set_item(self._dragged_item)
                else:
                    # Swap items
                    temp = target_item
                    target_slot.set_item(self._dragged_item)
                    self._drag_origin.set_item(temp)

            self._dragged_item = None
            self._drag_origin = None

        # DRAGGED ITEM FOLLOWS MOUSE
        if self._dragged_item:
            self._dragged_item.set_position(mouse_pos)

    # ---------- DRAW ----------
    def draw(self, screen):
        if self._open:
            screen.blit(self._inventory_bg, self._inventory_bg_rect)
            for slot in self._inventory_slots:
                slot.draw(screen)

        screen.blit(self._hotbar_bg, self._hotbar_bg_rect)
        for i, slot in enumerate(self._hotbar_slots):
            slot.set_selected(i == self._selected_hotbar)
            slot.draw(screen)
