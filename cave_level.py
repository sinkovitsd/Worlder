import pygame
from physics_objects import Sprite3D, Polygon, Circle
from pygame.math import Vector2, Vector3
import math
import contact
from text import textbox, InputBox
import try_again

go_to_next_level = False
at_the_sign = False

yfactor = 0.3
horizon = 630

start_pos = (100,700,0)

background = pygame.image.load("cave_scene.png").convert()
sign = pygame.image.load("stone_sign.png").convert()
#sign.set_colorkey((127,127,127))

def screen_to_world(point):
    return Vector3(point[0], (point[1] - horizon)/yfactor, 0)

def world_to_screen(pos):
    return Vector2(pos.x, horizon + pos.y*yfactor - pos.z)

def ground(point):
    return 0

def ceiling(point):
    return math.inf

cave_boundary = Sprite3D(visible=False, mass=math.inf,
                         collide_shape=Polygon(local_points=[screen_to_world([1143,630])[0:2],screen_to_world([1137,736])[0:2],
                                                             screen_to_world([1574,780])[0:2],screen_to_world([1897,745])[0:2],
                                                             screen_to_world([1897,630])[0:2]]))

rock = Sprite3D(visible=False, mass=math.inf, pos=[1420,450,0], collide_shape=Circle(radius=290))

font = pygame.font.SysFont("inkfree", 60)
input_box = InputBox(font, (670, 645), color=(0,0,0), bg_color=(127,127,127), cursor=True)

sprites = [cave_boundary, rock]

#goal_polygon = Sprite3D(None, visible=False, pos=(1642, 188/yfactor, 0), collide_shape=Polygon(local_points=[[0, 0], [0, 89/yfactor], [178, 89/yfactor], [178, 0]]))


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
                if response == 583+602+379:
                    global go_to_next_level
                    go_to_next_level = True
                else:
                    try_again.show()
        elif try_again.handle_event(event, input_box):
            pass
        return True

def interact(player):
    c = contact.generate(player, rock, resolve=True)
    if c.overlap > 0:
        global at_the_sign
        at_the_sign = True
        
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
