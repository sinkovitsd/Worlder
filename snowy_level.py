import pygame
from pygame.locals import *
from physics_objects import Sprite3D, Polygon, Circle
from pygame.math import Vector2, Vector3
import math
import contact
from text import textbox, InputBox
import try_again

go_to_next_level = False
at_the_sign = False
answered = False
hot_cocoa = False

yfactor = 0.3
horizon = 600

start_pos = (100,1500,0)

background = pygame.image.load("snowy_scene.png").convert()
sign_image = pygame.image.load("snowy_sign.png").convert()
sign_image.set_colorkey((127,127,127))
hot_cocoa_image = pygame.image.load("hot_cocoa.png").convert()
hot_cocoa_image.set_colorkey((255,0,0))
hot_cocoa_image2 = pygame.image.load("hot_cocoa2.png").convert()
hot_cocoa_image2.set_colorkey((255,0,0))
scale = 0.5
width = hot_cocoa_image.get_width()*scale
height = hot_cocoa_image.get_height()*scale
hot_cocoa_image = pygame.transform.scale(hot_cocoa_image, [width, height])
width = hot_cocoa_image2.get_width()*scale
height = hot_cocoa_image2.get_height()*scale
hot_cocoa_image2 = pygame.transform.scale(hot_cocoa_image2, [width, height])



def screen_to_world(point):
    return Vector3(point[0], (point[1] - horizon)/yfactor, 0)

def world_to_screen(pos):
    return Vector2(pos.x, horizon + pos.y*yfactor - pos.z)

def ground(point):
    return 0

def ceiling(point):
    return math.inf

boundary = Sprite3D(visible=False, mass=math.inf,
                         collide_shape=Polygon(local_points=[screen_to_world([400,600])[0:2],screen_to_world([400,765])[0:2],
                                                             screen_to_world([750,845])[0:2],screen_to_world([1630,860])[0:2],
                                                             screen_to_world([1730,825])[0:2],screen_to_world([1765,600])[0:2]]))

sign = Sprite3D(visible=False, mass=math.inf,
                collide_shape=Polygon(local_points=[screen_to_world([260,600])[0:2],screen_to_world([260,765])[0:2],
                                                    screen_to_world([775,765])[0:2],screen_to_world([775,600])[0:2]]))

door_boundary = Sprite3D(visible=False, mass=math.inf,
                collide_shape=Polygon(local_points=[screen_to_world([1255,800])[0:2],screen_to_world([1225,860])[0:2],
                                                    screen_to_world([1420,860])[0:2],screen_to_world([1420,800])[0:2]]))

font = pygame.font.SysFont("inkfree", 60)
input_box = InputBox(font, (860, 820), color=(0,0,0), bg_color=(185,122,87), cursor=True)

sprites = []

#goal_polygon = Sprite3D(None, visible=False, pos=(1642, 188/yfactor, 0), collide_shape=Polygon(local_points=[[0, 0], [0, 89/yfactor], [178, 89/yfactor], [178, 0]]))


def handle_event(event):
    global at_the_sign, answered, hot_cocoa
    if event.type == USEREVENT:
        hot_cocoa = False
        return True
    if at_the_sign:
        if input_box.handle_event(event):
            if input_box.finished:
                try:
                    response = input_box.text
                    response = response.replace("*","")
                    response = response.replace(" ","")
                    print("string", response)
                    response = float(response)
                    print("float", response)
                except ValueError:
                    input_box.clear()
                    input_box.open()
                    response = ""
                if response == 16.25 + 6.00 + 1.00:
                    at_the_sign = False
                    answered = True
                else:
                    try_again.show()
        elif try_again.handle_event(event, input_box):
            pass
        return True
    return False

def interact(player):
    c = contact.generate(player, boundary, resolve=True)
    c = contact.generate(player, sign, resolve=True)
    if not answered and c.overlap > 0:
        global at_the_sign
        at_the_sign = True
    c = contact.generate(player, door_boundary, resolve=False)
    global hot_cocoa
    if not hot_cocoa and c.overlap > 0:
        hot_cocoa = True
        pygame.time.set_timer(USEREVENT, 3000)
    if answered and player.pos.x + player.origin.x - 30 > background.get_width():
        global go_to_next_level
        go_to_next_level = True
        
def draw(window, characters):
    player = characters[0]
    window.blit(background, (0, 0))
    objects = characters + sprites
    objects.sort(key=lambda obj : obj.pos.y)
    for obj in objects:
        obj.draw(window, horizon, yfactor)
    if hot_cocoa:
        image = hot_cocoa_image2 if player.facing > 0 else hot_cocoa_image
        window.blit(image, world_to_screen(player.pos) 
                    + Vector2((0.4*player.image.get_width()+image.get_width()/2)*player.facing - image.get_width()/2, 
                              -player.image.get_height()*0.4 - image.get_height()/2))
    if at_the_sign:
        window.blit(sign_image, (0,0))
        input_box.draw(window)
    try_again.draw(window)
