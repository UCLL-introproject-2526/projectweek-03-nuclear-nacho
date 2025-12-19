import pygame
from slot import Slot
from item import Item


class Inventory:
    def __init__(self, socket_surf, item_data, screen_size, inventory_bg, hotbar_bg, player):

        self._player = player
        self._selected_hotbar = 0

        w, h = screen_size

        # Open state
        self._open = False

        # Slots
        self._slots = []
        self._hotbar = []

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
        bg_padding_x = int(size * 1.6)
        bg_padding_y = int(size * 1.6)
        self._inventory_bg = pygame.transform.scale(
            inventory_bg, (inv_width + bg_padding_x, inv_height + bg_padding_y)
        )

        hotbar_padding_x = int(size * 0.4)
        hotbar_padding_y = int(size * 0.3)
        self._hotbar_bg = pygame.transform.scale(
            hotbar_bg, (hotbar_width + hotbar_padding_x, size + hotbar_padding_y)
        )

        offset_x = int(size * 0.3)
        offset_y = int(size * 0.67)
        self._inventory_bg_rect = self._inventory_bg.get_rect(
            center=(w // 2 + offset_x, h // 2 + offset_y)
        )
        self._hotbar_bg_rect = self._hotbar_bg.get_rect(center=(w // 2, hotbar_y))

        # Create inventory slots
        for row in range(rows):
            for col in range(cols):
                pos = (start_x + col * (size + gap), start_y + row * (size + gap))
                self._slots.append(Slot(self._socket_surf, pos))

        # Create hotbar slots
        for i in range(hotbar_slots):
            pos = (hotbar_start_x + i * (size + gap), hotbar_y)
            self._hotbar.append(Slot(self._socket_surf, pos))

        # Spawn items in slots
        slot_index = 0
        for item_id, data in item_data.items():
            if slot_index >= len(self._slots):
                break
            item = Item(
                item_id,
                data["icon"],
                data.get("weapon_surf"),
                data.get("char_weapon"),
                data.get("stackable", False),
                data.get("amount", 1),
                data.get("max_stack", 1)
            )
            self._slots[slot_index].set_item(item)
            slot_index += 1

    # ---------- GETTERS ----------
    def get_equipped_item(self):
        return self._equipped_item

    # ---------- TOGGLE ----------
    def toggle(self):
        self._open = not self._open

    def select_next(self):
        prev_index = self._selected_hotbar
        self._selected_hotbar = (self._selected_hotbar + 1) % len(self._hotbar)

        prev_item = self._equipped_item
        new_item = self._hotbar[self._selected_hotbar].get_item()

        self._player.set_equipped_item(new_item)
        self._equipped_item = new_item

        # Play sound only if the new item exists AND is different from the previous
        if new_item is not None and new_item != prev_item:
            self._player.play_equip_sound(new_item)


    def select_previous(self):
        prev_index = self._selected_hotbar
        self._selected_hotbar = (self._selected_hotbar - 1) % len(self._hotbar)

        prev_item = self._equipped_item
        new_item = self._hotbar[self._selected_hotbar].get_item()

        self._player.set_equipped_item(new_item)
        self._equipped_item = new_item

        # Play sound only if the new item exists AND is different from the previous
        if new_item is not None and new_item != prev_item:
            self._player.play_equip_sound(new_item)






    # ---------- UPDATE ----------
    def update(self, mouse_pos, mouse_down, mouse_up):
        press = mouse_down and not self._mouse_down_prev
        release = (not mouse_down) and self._mouse_down_prev
        self._mouse_down_prev = mouse_down

        slots = self._hotbar + (self._slots if self._open else [])

        # Update hover states
        for slot in slots:
            slot.update(mouse_pos)

        # PICK UP ITEM
        if press and not self._dragged_item:
            for slot in slots:
                if slot.is_hovered() and slot.get_item():
                    self._dragged_item = slot.get_item()
                    self._drag_origin = slot
                    slot.clear_item()
                    break

        # DROP ITEM
        if release and self._dragged_item:
            target_slot = None
            for slot in slots:
                if slot.is_hovered():
                    target_slot = slot
                    break

            if target_slot is None:
                # Drop back to origin
                self._drag_origin.set_item(self._dragged_item)
            else:
                target_item = target_slot.get_item()
                if target_item is None:
                    target_slot.set_item(self._dragged_item)
                elif target_item.can_stack_with(self._dragged_item):
                    added = target_item.add_to_stack(self._dragged_item.get_amount())
                    if added < self._dragged_item.get_amount():
                        self._dragged_item.remove_from_stack(added)
                        self._drag_origin.set_item(self._dragged_item)
                else:
                    # Swap items
                    temp = target_item
                    target_slot.set_item(self._dragged_item)
                    self._drag_origin.set_item(temp)

            # ✅ Play sound if dropped into hotbar
            if target_slot in self._hotbar:
                # Only play sound if the dropped item is different from currently equipped item
                slot_index = self._hotbar.index(target_slot)
                if slot_index == self._selected_hotbar:
                    self._player.play_equip_sound(target_slot.get_item())

            # Reset drag
            self._dragged_item = None
            self._drag_origin = None

        # DRAGGED ITEM FOLLOWS MOUSE
        if self._dragged_item:
            self._dragged_item.set_position(mouse_pos)


    # ---------- ITEM USAGE ----------
    def use_item(self, item):
        """Gebruik consumables of items op de speler"""
        item_id = item.get_id()

        if item_id == "energy_drink":
            self._player.restore_stamina(40)
            item.remove_from_stack(1)

        elif item_id == "bandage":
            self._player.heal(30)
            item.remove_from_stack(1)

        elif item_id == "iodine":
            # voorbeeld: geen effect maar verbruikbaar
            item.remove_from_stack(1)

        if item.get_amount() <= 0:
            self.remove_item(item)

    def remove_item(self, item):
        """Verwijder item uit alle slots"""
        for slot in self._slots + self._hotbar:
            if slot.get_item() == item:
                slot.clear_item()
                if self._equipped_item == item:
                    self._equipped_item = None
                break

    # ---------- DRAW ----------
    def draw(self, screen):
        # Inventory background + slots
        if self._open:
            screen.blit(self._inventory_bg, self._inventory_bg_rect)

            for slot in self._slots:
                slot.draw(screen)
        # ---------- HOTBAR (always visible) ----------
        screen.blit(self._hotbar_bg, self._hotbar_bg_rect)
        for slot in self._hotbar:
            slot.draw(screen)

        for i, slot in enumerate(self._hotbar):
            slot.set_selected(i == self._selected_hotbar)
            slot.draw(screen)
        # ---------- DRAGGED ITEM (top layer) ----------
        if self._dragged_item:
            surf = self._dragged_item.get_weapon_surface() or self._dragged_item.get_icon()
            rect = surf.get_rect(center=pygame.mouse.get_pos())
            screen.blit(surf, rect)
        


