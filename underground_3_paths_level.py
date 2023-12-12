import pygame
from physics_objects import Sprite3D, Polygon
from pygame.math import Vector2, Vector3
import math
import contact
from text import textbox, InputBox
import try_again

go_to_next_level = False
at_the_sign = False

yfactor = 0.0

start_pos = (100,0,-800)

background = pygame.image.load("underground_3_paths_scene.png").convert()

sign = pygame.image.load("letter_sign.png").convert()

horizon = 0

def screen_to_world(point):
    return Vector3(point[0], 0, 0)

def world_to_screen(pos):
    return Vector2(pos.x, horizon - pos.z)

ground_array = []
ceiling_array = []
for x in range(0, background.get_width()):
    found_ground = False
    found_ceiling = False
    for y in range(0, background.get_height()):
        if not found_ceiling and background.get_at((x,y)) == (0,0,0):
            found_ceiling = True
            ceiling_array.append(y-1)
        if found_ceiling and background.get_at((x,y)) == (66,33,0):
            found_ground = True
            ground_array.append(y)
            break
    if not found_ground:
        ground_array.append(y+1)


def ground(point):
    return -ground_array[int(point.x)]

def ceiling(point):
    return -ceiling_array[int(point.x)]

sprites = []

font = pygame.font.SysFont("inkfree", 60)
input_box = InputBox(font, (870, 910), color=(0,0,0), transparent=True, cursor=True)


def handle_event(event):
    if at_the_sign:
        if input_box.handle_event(event):
            if input_box.finished:
                try:
                    response = int(input_box.text)
                except ValueError:
                    input_box.clear()
                    input_box.open()
                    response = ""
                if response == (13 + 15 + 14 + 18)/4:
                    global go_to_next_level
                    go_to_next_level = True
                else:
                    try_again.show()
        elif try_again.handle_event(event, input_box):
            pass
        return True
    return False

def interact(player):
    global at_the_sign
    if player.pos.x+player.image.get_width()-player.origin.x > 1250:
        at_the_sign = True
        return True
    
        
def draw(window, characters):
    window.blit(background, (0, 0))
    objects = characters + sprites
    objects.sort(key=lambda obj : obj.pos.y)
    for obj in objects:
        obj.draw(window, horizon, yfactor)
    if at_the_sign:
        window.blit(sign, (0,0))
        input_box.draw(window)
    try_again.draw(window)
