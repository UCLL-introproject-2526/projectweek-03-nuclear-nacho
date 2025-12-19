import pygame
import time 

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption('RAD ZONE')

Game_logo_surf_white = pygame.image.load('RAD ZONE/current version/Graphics/Nuclear_Nacho_Logo_White.png').convert_alpha()
Game_logo_rect_white = Game_logo_surf_white.get_rect( center = (960, 540))

Game_logo_surf_black = pygame.image.load('RAD ZONE/current version/Graphics/Nuclear_Nacho_Logo_Black.png').convert_alpha()
Game_logo_rect_black = Game_logo_surf_black.get_rect( center = (960, 540))

Flicker_Interval = 60
Flicker_Duration = 2500

Start_time = pygame.time.get_ticks()
Last_flicker = 0
use_White = False
Flicker_active = True

def blitblack():
    screen.blit(Game_logo_surf_black, Game_logo_rect_black)
    pygame.display.flip()
def blitwhite():
    screen.blit(Game_logo_surf_white, Game_logo_rect_white)
    pygame.display.flip()


blitblack()
time.sleep(0.1)
blitwhite()
time.sleep(0.1)
blitblack()
time.sleep(0.1)
blitwhite()
time.sleep(0.1)
blitblack()
time.sleep(0.5)
blitwhite()


time.sleep(2.5)


from game import Game

Game().run()