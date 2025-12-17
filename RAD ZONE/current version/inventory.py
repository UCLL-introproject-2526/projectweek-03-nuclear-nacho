import pygame
from slot import Slot
from item import Item

class Inventory:
    def __init__(self, socket_surf, item_data, screen_size):
        
        self._drop_success = False
        self._mouse_down_prev = False

        self._open = False
        self._slots = []
        self._hotbar = []

        self._dragged_item = None
        self._drag_origin = None
        self._equipped_item = None
        self._mouse_down_prev = False

        w, h = screen_size

        self._ui_scale = 1.35
        base_size, base_gap = 64, 10

        size = int(base_size * self._ui_scale)
        gap = int(base_gap * self._ui_scale)

        self._socket_surf = pygame.transform.scale(
            socket_surf,
            (size, size)
        )

        # --- Inventory grid (4x4) ---
        cols, rows = 4, 4

        inv_width = cols * size + (cols - 1) * gap
        inv_height = rows * size + (rows - 1) * gap

        start_x = (w - inv_width) // 2 + size // 2
        start_y = (h - inv_height) // 2 + size // 2


        for row in range(rows):
            for col in range(cols):
                pos = (
                    start_x + col * (size + gap),
                    start_y + row * (size + gap)
                )
                self._slots.append(Slot(self._socket_surf, pos))

        # --- Hotbar (5 slots) ---
        hotbar_slots = 5
        hotbar_width = hotbar_slots * size + (hotbar_slots - 1) * gap
        hotbar_y = h - int(100 * self._ui_scale)
        hotbar_start_x = (w - hotbar_width) // 2 + size // 2

        for i in range(hotbar_slots):
            pos = (
                hotbar_start_x + i * (size + gap),
                hotbar_y
            )
            self._hotbar.append(Slot(self._socket_surf, pos))

        # --- Spawn test weapons ---
        # --- Spawn ALL weapons into inventory ---
        slot_index = 0

        for weapon_id, data in item_data.items():
            if slot_index >= len(self._slots):
                break  # safety check (inventory full)

            self._slots[slot_index].set_item(
                Item(weapon_id, data["icon"], data["weapon_surf"])
            )
            slot_index += 1


    # ---------- GETTERS ----------
    def get_equipped_item(self):
        return self._equipped_item

    # ---------- LOGIC ----------
    # def toggle(self):
    #     self._open = not self._open

    def toggle(self):
        self._open = not self._open
        # print("Inventory open:", self._open)

    def handle_hotbar_keys(self, keys):
        for i in range(5):
            if keys[getattr(pygame, f"K_{i+1}")]:
                item = self._hotbar[i].get_item()
                if item:
                    self._equipped_item = item

    def update(self, mouse_pos, mouse_down, mouse_up):
        # We will IGNORE mouse_up from game.py and compute edges ourselves,
        # because your current mouse_up value is "not pressed" every frame.
        press = mouse_down and not self._mouse_down_prev
        release = (not mouse_down) and self._mouse_down_prev
        self._mouse_down_prev = mouse_down

        slots = self._hotbar + (self._slots if self._open else [])

        # Update hover first
        for slot in slots:
            slot.update(mouse_pos)

        # -------- PICK UP on mouse press --------
        if press and not self._dragged_item:
            for slot in slots:
                if slot.is_hovered() and slot.get_item():
                    self._dragged_item = slot.get_item()
                    self._drag_origin = slot
                    slot.clear_item()
                    break

        # -------- DROP on mouse release --------
        if release and self._dragged_item:
            target = None
            for slot in slots:
                if slot.is_hovered():
                    target = slot
                    break

            if target is None:
                # released nowhere → return to origin
                self._drag_origin.set_item(self._dragged_item)
            else:
                # drop (swap if occupied)
                if target.get_item() is None:
                    target.set_item(self._dragged_item)
                else:
                    temp = target.get_item()
                    target.set_item(self._dragged_item)
                    self._drag_origin.set_item(temp)

            self._dragged_item = None
            self._drag_origin = None

        # Drag follows mouse while holding
        if self._dragged_item:
            self._dragged_item.set_position(mouse_pos)


    def draw(self, screen):
        if self._open:
            for slot in self._slots:
                slot.draw(screen)

        for slot in self._hotbar:
            slot.draw(screen)

        if self._dragged_item:
            surf = self._dragged_item.get_weapon_surface()
            rect = surf.get_rect(center=pygame.mouse.get_pos())
            screen.blit(surf, rect)
