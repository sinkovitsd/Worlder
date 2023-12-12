import pygame
from physics_objects import Sprite3D, Polygon
from pygame.math import Vector2, Vector3
import math
import contact
from text import textbox, InputBox
import try_again

go_to_next_level = False
at_the_sign = False
problem_done = False

yfactor = 0.3

start_pos = (100,500,0)

background = pygame.image.load("stream_scene.png").convert()
sign = pygame.image.load("big_sign.png").convert()
sign.set_colorkey((127,127,127))

horizon = 615

def screen_to_world(point):
    return Vector3(point[0], (point[1] - horizon)/yfactor, 0)

def world_to_screen(pos):
    return Vector2(pos.x, horizon + pos.y*yfactor - pos.z)

def ground(point):
    return 0

def ceiling(point):
    return math.inf

stream_boundary = Sprite3D(visible=False, mass=math.inf,
                           collide_shape=Polygon(local_points=[screen_to_world([937,600])[0:2],screen_to_world([660,1079])[0:2],
                                                               screen_to_world([1380,1079])[0:2],screen_to_world([1430,600])[0:2]]))

sign_area = Sprite3D(visible=False, mass=math.inf, 
                     collide_shape=Polygon(local_points=[screen_to_world([660,690])[0:2],screen_to_world([760,690])[0:2]]))


arrow_image = pygame.image.load("arrow.png").convert()
arrow_image.set_colorkey((127,127,127))

arrow = Sprite3D(arrow_image, visible=False, pos=(1642, 188/yfactor, 0), collide_shape=Polygon(local_points=[[0, 0], [0, 89/yfactor], [178, 89/yfactor], [178, 0]]))


font = pygame.font.SysFont("inkfree", 60)
input_box = InputBox(font, (600, 590), color=(128,64,64), bg_color=(185,122,87), cursor=True)

sprites = [stream_boundary]

#goal_polygon = Sprite3D(None, visible=False, pos=(1642, 188/yfactor, 0), collide_shape=Polygon(local_points=[[0, 0], [0, 89/yfactor], [178, 89/yfactor], [178, 0]]))


def handle_event(event):
    global at_the_sign, background
    if at_the_sign:
        if input_box.handle_event(event):
            if input_box.finished:
                try:
                    response = int(input_box.text)
                except ValueError:
                    input_box.clear()
                    input_box.open()
                    response = ""
                if response == 648/9:
                    global problem_done
                    problem_done = True
                    at_the_sign = False
                    background = pygame.image.load("stream_scene_with_bridge.png").convert()
                    stream_boundary_top = Sprite3D(visible=False, mass=math.inf,
                        collide_shape=Polygon(local_points=[screen_to_world([850,770])[0:2],screen_to_world([920,615])[0:2],
                                                            screen_to_world([1430,590])[0:2],screen_to_world([1420,767])[0:2]]))
                    stream_boundary_bottom = Sprite3D(visible=False, mass=math.inf,
                        collide_shape=Polygon(local_points=[screen_to_world([760,970])[0:2],screen_to_world([650,1080])[0:2],
                                                            screen_to_world([1382,1080])[0:2],screen_to_world([1445,970])[0:2]]))
                    global sprites
                    sprites = [stream_boundary_top, stream_boundary_bottom]
                    arrow.visible = True
                else:
                    try_again.show()
        elif try_again.handle_event(event, input_box):
            pass
        return True

def interact(player):
    if not problem_done:
        c = contact.generate(player, sign_area)
        if c.overlap > 0:
            global at_the_sign
            at_the_sign = True
    else:
        c = contact.generate(player, arrow)
        if c.overlap > 0:
            global go_to_next_level
            go_to_next_level = True

        
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
    if problem_done:
        arrow.draw(window, horizon, yfactor)
        