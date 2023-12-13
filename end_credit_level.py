import pygame
from pygame.locals import *
from physics_objects import Sprite3D, Polygon
from pygame.math import Vector2, Vector3
import math
import contact
from text import textbox, InputBox
import try_again

go_to_next_level = False

yfactor = 0.3

start_pos = (100,500,0)

background = pygame.image.load("title_screen.png").convert()

horizon = 615

def screen_to_world(point):
    return Vector3(point[0], (point[1] - horizon)/yfactor, 0)

def world_to_screen(pos):
    return Vector2(pos.x, horizon + pos.y*yfactor - pos.z)

def ground(point):
    return 0

def ceiling(point):
    return math.inf


font = pygame.font.SysFont("kristenitc", 96)
text = font.render("Thanks for playing!", True, (255,174,201), (0,0,0))
#input_box = InputBox(font, (600, 590), color=(128,64,64), bg_color=(185,122,87), cursor=True)

sprites = []

def handle_event(event):
    if event.type == KEYDOWN:
        global go_to_next_level
        go_to_next_level = True
    return True

def interact(player):
    pass
    
def draw(window, characters):
    window.blit(background, (0, 0))
    window.blit(text, (965,815))

    
        