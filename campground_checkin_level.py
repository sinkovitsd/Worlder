import pygame
from physics_objects import Sprite3D, Polygon, Circle, Wall
from pygame.math import Vector2, Vector3
import math
import contact
from text import textbox, InputBox
import try_again

go_to_next_level = False
talking = False
at_the_sign = False
answered = False

yfactor = 0.3
horizon = 510

start_pos = (580,2300,0)

background = pygame.image.load("campground_checkin_scene.png").convert()
background_talking = pygame.image.load("campground_checkin_stop.png").convert()
sign = pygame.image.load("tree_sign.png").convert()
#sign.set_colorkey((127,127,127))

def screen_to_world(point):
    return Vector3(point[0], (point[1] - horizon)/yfactor, 0)

def world_to_screen(pos):
    return Vector2(pos.x, horizon + pos.y*yfactor - pos.z)

def ground(point):
    return 0

def ceiling(point):
    return math.inf

checkin_boundary = Sprite3D(visible=False, mass=math.inf,
                         collide_shape=Polygon(local_points=[screen_to_world([640,500])[0:2],screen_to_world([640,800])[0:2],
                                                             screen_to_world([1090,800])[0:2],screen_to_world([1090,500])[0:2]]))

tree = Sprite3D(visible=False, mass=math.inf, 
                collide_shape=Polygon(local_points=[screen_to_world([300,840])[0:2],screen_to_world([470,840])[0:2],
                                                    screen_to_world([470,500])[0:2],screen_to_world([300,500])[0:2]]))

horizon_boundary = Sprite3D(visible=False, mass=math.inf, 
                            collide_shape=Polygon(local_points=[screen_to_world([0,650])[0:2],screen_to_world([1920,650])[0:2],
                                                    screen_to_world([1920,500])[0:2],screen_to_world([0,500])[0:2]]))

font = pygame.font.SysFont("inkfree", 60)
camp_boundary = Sprite3D(visible=False, mass=math.inf,
                         collide_shape=Polygon(local_points=[screen_to_world([1050,500])[0:2],screen_to_world([1050,2500])[0:2],
                                                    screen_to_world([1920,2500])[0:2],screen_to_world([1920,500])[0:2]]))

font = pygame.font.SysFont("inkfree", 60)
input_box = InputBox(font, (970, 940), color=(0,0,0), bg_color=(66,33,0), transparent=True, cursor=True)

sprites = []#[checkin_boundary, tree, far_boundary, camp_boundary]

#goal_polygon = Sprite3D(None, visible=False, pos=(1642, 188/yfactor, 0), collide_shape=Polygon(local_points=[[0, 0], [0, 89/yfactor], [178, 89/yfactor], [178, 0]]))


def handle_event(event):
    global at_the_sign
    if at_the_sign:
        if input_box.handle_event(event):
            if input_box.finished:
                try:
                    response = input_box.text
                    response = response.replace("*","")
                    response = response.replace(" ","")
                    response = float(response)
                except ValueError:
                    input_box.clear()
                    input_box.open()
                    response = ""
                if response == 9*3*1.5:
                    global answered, talking
                    at_the_sign = False
                    answered = True
                    talking = False
                else:
                    try_again.show()
        elif try_again.handle_event(event, input_box):
            pass
        return True
    return False

def interact(player):
    c = contact.generate(player, horizon_boundary, resolve=True)
    c = contact.generate(player, tree, resolve=True)
    if c.overlap > 0 and not answered:
        global at_the_sign
        at_the_sign = True
    c1 = contact.generate(player, camp_boundary, resolve=not answered)
    c2 = contact.generate(player, checkin_boundary, resolve=True)
    if not answered and (c1.overlap > 0 or c2.overlap > 0):
        global talking
        talking = True
    if answered and player.pos.x+player.image.get_width()-player.origin.x+50 > background.get_width():
        global go_to_next_level
        go_to_next_level = True
    
def draw(window, characters):
    if talking:
        window.blit(background_talking, (0,0))
    else:
        window.blit(background, (0,0))
    objects = characters + sprites
    objects.sort(key=lambda obj : obj.pos.y)
    for obj in objects:
        obj.draw(window, horizon, yfactor)
    if at_the_sign and not answered:
        window.blit(sign, (0,0))
        input_box.draw(window)
    try_again.draw(window)
