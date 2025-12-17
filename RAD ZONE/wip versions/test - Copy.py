import pygame
import random
import time
from sys import exit



pygame.init()
# screen = pygame.display.set_mode((1280, 720))
# pygame.display.set_caption('RAD ZONE')
clock = pygame.time.Clock()

# Game_logo_surf_white = pygame.image.load('Graphics/Nuclear_Nacho_Logo_White.png').convert_alpha()
# Game_logo_rect_white = Game_logo_surf_white.get_rect( center = (640, 360))

# Game_logo_surf_black = pygame.image.load('Graphics/Nuclear_Nacho_Logo_Black.png').convert_alpha()
# Game_logo_rect_black = Game_logo_surf_black.get_rect( center = (640, 360))

# Flicker_Interval = 60
# Flicker_Duration = 2500

# Start_time = pygame.time.get_ticks()
# Last_flicker = 0
# use_White = False
# Flicker_active = True

# def blitblack():
#     screen.blit(Game_logo_surf_black, Game_logo_rect_black)
#     pygame.display.flip()
# def blitwhite():
#     screen.blit(Game_logo_surf_white, Game_logo_rect_white)
#     pygame.display.flip()


# blitblack()
# time.sleep(0.1)
# blitwhite()
# time.sleep(0.1)
# blitblack()
# time.sleep(0.1)
# blitwhite()
# time.sleep(0.1)
# blitblack()
# time.sleep(0.5)
# blitwhite()


# time.sleep(2.5)
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

dt = 0

def load_image(path, size=None, center=(0, 0)):
    surf = pygame.image.load(path).convert_alpha()
    
    if size is not None:
        surf = pygame.transform.scale(surf, size)
    
    rect = surf.get_rect(center=center)
    return surf, rect

Map_surf, Map_rect = load_image(
    "Graphics/BasePlate.png",
    size=(4096, 4096),
    center=(960, 540)
)

Char_surf, Char_rect = load_image(
    "Graphics/AChar.png",
    size=(75, 75),
    center=(960, 540)
)

Inv_surf, Inv_rect = load_image(
    "Graphics/Inventory.png",
    size=(1256, 746),
    center=(960, 540)
)

Health_bar_surf, Health_bar_rect = load_image(
    'Graphics/Health_bar.png',
    size=(512, 58),
    center=(260, 30)
)

Stamina_bar_surf, Stamina_bar_rect = load_image(
    'Graphics/Stamina_bar.png',
    size=(512, 58),
    center=(260, 80)
)

Outline_Hbar_surf, Outline_Hbar_rect = load_image(
    'Graphics/Outline_bar.png',
    size=(512, 58),
    center=(260, 30)
)

Outline_Sbar_surf, Outline_Sbar_rect = load_image(
    'Graphics/Outline_bar.png',
    size=(512, 58),
    center=(260, 80)
)

Building1_surf, Building1_rect = load_image(
    'Graphics/Building1.png',
    size=(350, 350),
    center=(1600, 800)
)

Building2_surf, Building2_rect = load_image(
    'Graphics/Building2.png',
    size=(350, 350),
    center=(1950, 800)
)

Building3_surf, Building3_rect = load_image(
    'Graphics/Building3.png',
    size=(350, 350),
    center=(1250, 800)
)

Building4_surf, Building4_rect = load_image(
    'Graphics/Building4.png',
    size=(350, 350),
    center=(900, 800)
)

Building5_surf, Building5_rect = load_image(
    'Graphics/Building5.png',
    size=(350, 350),
    center=(550, 800)
)




# Tree_surf = pygame.image.load('Graphics/Tree.png').convert_alpha()
# Tree_surf = pygame.transform.scale(Tree_surf, (160, 160))
# Tree_rect = Tree_surf.get_rect(center = (923, 503))

screen.blit(Map_surf, Map_rect)
screen.blit(Char_surf, Char_rect)

# y = Map_rect.y
# x = Map_rect.x
speed = 200
Max_stamina = 100
stamina = Max_stamina

Stamina_drain = 40   # per second
Stamina_regen = 15

exhausted = False
exhaust_at = 0
recover_at = 20

camera_x = Map_surf.get_width() // 2 - Char_rect.centerx
camera_y = Map_surf.get_height() // 2 - Char_rect.centery

building1_world_pos = pygame.Vector2(1600, 800)
building2_world_pos = pygame.Vector2(1950, 800)
building3_world_pos = pygame.Vector2(1250, 800)
building4_world_pos = pygame.Vector2(900, 800)
building5_world_pos = pygame.Vector2(550, 800)

# player_world_x = camera_x + Char_rect.centerx
# player_world_y = camera_y + Char_rect.centery
# player_world_pos = pygame.Vector2(player_world_x, player_world_y)

MINIMAP_SIZE = 220
minimap_surf = pygame.Surface((MINIMAP_SIZE, MINIMAP_SIZE))
minimap_rect = minimap_surf.get_rect(topright=(screen.get_width() - 20, 20))

MINIMAP_ZOOM = 0.1   # 0.1 = very zoomed out, 0.3 = closer   

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
    
    
    keypress = pygame.key.get_pressed()

    if stamina <= exhaust_at:
        exhausted = True
    elif stamina >= recover_at:
        exhausted = False


    if keypress[pygame.K_LSHIFT]:
        speed = 200
        

    if keypress[pygame.K_LSHIFT] and (keypress[pygame.K_z] or keypress[pygame.K_q] or keypress[pygame.K_s] or keypress[pygame.K_d]) and not exhausted:
        speed = 300
        stamina -= Stamina_drain * dt
    else:
        speed = 200
        stamina += Stamina_regen * dt

    stamina = max(0, min(stamina, Max_stamina))

    # if keypress[pygame.K_z]:
    #     Map_rect.y += speed * dt
    #     update()
    # if keypress[pygame.K_s]:
    #     Map_rect.y -= speed * dt
    #     update()
    # if keypress[pygame.K_q]:
    #     Map_rect.x += speed * dt
    #     update()
    # if keypress[pygame.K_d]:
    #     Map_rect.x -= speed * dt
    #     update()

    if keypress[pygame.K_z]:
        camera_y -= speed * dt
        
    if keypress[pygame.K_s]:
        camera_y += speed * dt
        
    if keypress[pygame.K_q]:
        camera_x -= speed * dt
        
    if keypress[pygame.K_d]:
        camera_x += speed * dt
        
    if keypress[pygame.K_e]:
        screen.blit(Inv_surf, Inv_rect)
        # print('0000')
    if keypress[pygame.K_i]:
        print(Map_rect.x)
        print(Map_rect.y)

    stamina = max(0, min(stamina, Max_stamina))
    # bar_x, bar_y = 20, 20

    # bar_width = Stamina_bar_surf.get_width()
    # bar_height = Stamina_bar_surf.get_height()

    # ratio = stamina / Max_stamina
    # current_width = int(bar_width * ratio)

    # stamina_surface = Stamina_bar_surf.subsurface(
    #     (0, 0, current_width, bar_height)
    # )
    # Map
    screen.blit(Map_surf, (-camera_x, -camera_y))

    # Building (world → screen)
    building1_screen_pos = building1_world_pos - pygame.Vector2(camera_x, camera_y)
    screen.blit(Building1_surf, building1_screen_pos)
    building2_screen_pos = building2_world_pos - pygame.Vector2(camera_x, camera_y)
    screen.blit(Building2_surf, building2_screen_pos)
    building3_screen_pos = building3_world_pos - pygame.Vector2(camera_x, camera_y)
    screen.blit(Building3_surf, building3_screen_pos)
    building4_screen_pos = building4_world_pos - pygame.Vector2(camera_x, camera_y)
    screen.blit(Building4_surf, building4_screen_pos)
    building5_screen_pos = building5_world_pos - pygame.Vector2(camera_x, camera_y)
    screen.blit(Building5_surf, building5_screen_pos)

    # Player (screen space, fixed)
    screen.blit(Char_surf, Char_rect)

    ratio = stamina / Max_stamina

    ratio = stamina / Max_stamina
    ratio = max(0, min(ratio, 1))

    full_width = Stamina_bar_surf.get_width()
    height = Stamina_bar_surf.get_height()

    current_width = int(full_width * ratio)

    if current_width > 0:
        stamina_surface = Stamina_bar_surf.subsurface(
            (0, 0, current_width, height)
        )
        screen.blit(stamina_surface, Stamina_bar_rect.topleft)
    

    # UI
    screen.blit(Health_bar_surf, Health_bar_rect)
    screen.blit(Outline_Hbar_surf, Outline_Hbar_rect)
    screen.blit(Outline_Sbar_surf, Outline_Sbar_rect)

    player_world_pos = pygame.Vector2(
        camera_x + Char_rect.centerx,
        camera_y + Char_rect.centery
    )

    # ---- MINIMAP RENDER ----
    minimap_surf.fill((0, 0, 0))

    # Scaled camera offset
    # Player position in minimap space
    player_mm_pos = player_world_pos * MINIMAP_ZOOM

    # Center minimap on player
    mm_offset_x = MINIMAP_SIZE // 2 - player_mm_pos.x
    mm_offset_y = MINIMAP_SIZE // 2 - player_mm_pos.y


    # Draw scaled world
    scaled_map = pygame.transform.smoothscale(
        Map_surf,
        (int(Map_surf.get_width() * MINIMAP_ZOOM),
        int(Map_surf.get_height() * MINIMAP_ZOOM))
    )

    minimap_surf.blit(scaled_map, (mm_offset_x, mm_offset_y))

    # Scaled building
    scaled1_building = pygame.transform.smoothscale(
        Building1_surf,
        (int(Building1_surf.get_width() * MINIMAP_ZOOM),
        int(Building1_surf.get_height() * MINIMAP_ZOOM))
    )

    mm_building1_pos = building1_world_pos * MINIMAP_ZOOM + pygame.Vector2(mm_offset_x, mm_offset_y)
    minimap_surf.blit(scaled1_building, mm_building1_pos)

    scaled2_building = pygame.transform.smoothscale(
        Building2_surf,
        (int(Building2_surf.get_width() * MINIMAP_ZOOM),
        int(Building2_surf.get_height() * MINIMAP_ZOOM))
    )

    mm_building2_pos = building2_world_pos * MINIMAP_ZOOM + pygame.Vector2(mm_offset_x, mm_offset_y)
    minimap_surf.blit(scaled2_building, mm_building2_pos)

    scaled3_building = pygame.transform.smoothscale(
        Building3_surf,
        (int(Building3_surf.get_width() * MINIMAP_ZOOM),
        int(Building3_surf.get_height() * MINIMAP_ZOOM))
    )

    mm_building3_pos = building3_world_pos * MINIMAP_ZOOM + pygame.Vector2(mm_offset_x, mm_offset_y)
    minimap_surf.blit(scaled3_building, mm_building3_pos)

    scaled4_building = pygame.transform.smoothscale(
        Building4_surf,
        (int(Building4_surf.get_width() * MINIMAP_ZOOM),
        int(Building4_surf.get_height() * MINIMAP_ZOOM))
    )

    mm_building4_pos = building4_world_pos * MINIMAP_ZOOM + pygame.Vector2(mm_offset_x, mm_offset_y)
    minimap_surf.blit(scaled4_building, mm_building4_pos)

    scaled5_building = pygame.transform.smoothscale(
        Building5_surf,
        (int(Building5_surf.get_width() * MINIMAP_ZOOM),
        int(Building5_surf.get_height() * MINIMAP_ZOOM))
    )

    mm_building5_pos = building5_world_pos * MINIMAP_ZOOM + pygame.Vector2(mm_offset_x, mm_offset_y)
    minimap_surf.blit(scaled5_building, mm_building5_pos)
    

    # Frame
    pygame.draw.rect(minimap_surf, (200, 200, 200), minimap_surf.get_rect(), 2)

    pygame.draw.circle(
        minimap_surf,
        (0, 255, 0),
        (MINIMAP_SIZE // 2, MINIMAP_SIZE // 2),
        3
    )

    # Draw minimap to screen
    screen.blit(minimap_surf, minimap_rect)
    
    pygame.display.flip()


    dt = clock.tick(60)/1000