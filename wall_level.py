import pygame
from physics_objects import Sprite3D, Polygon
from pygame.math import Vector2, Vector3
import math
import contact
from text import textbox, InputBox
import try_again

go_to_next_level = False
at_the_door = False

yfactor = 0.3
#ground_height = 450

start_pos = (200,300,0)

background = pygame.image.load("wall_scene.png").convert()
cloud = pygame.image.load("big_cloud_year_minutes.png").convert()
cloud.set_colorkey((127,127,127))

horizon = 644

def screen_to_world(point):
    return Vector3(point[0], (point[1] - horizon)/yfactor, 0)

def world_to_screen(pos):
    return Vector2(pos.x, horizon + pos.y*yfactor - pos.z)

def ground(point):
    return 0

def ceiling(point):
    return math.inf

wall_boundary = Sprite3D(visible=False, mass=math.inf,
                         collide_shape=Polygon(local_points=[[907,0], [907,457], [1920,2300], [1920,2047]]))

doorstep = Sprite3D(visible=False, mass=math.inf, 
                    collide_shape=Polygon(local_points=[screen_to_world([1115-20,884])[0:2],screen_to_world([1320-20,1004])[0:2]]))

font = pygame.font.SysFont("inkfree", 60)
input_box = InputBox(font, (467+10, 615), cursor=True)

sprites = [wall_boundary]

def handle_event(event):
    if at_the_door:
        if input_box.handle_event(event):
            if input_box.finished:
                try:
                    response = int(input_box.text)
                except ValueError:
                    input_box.clear()
                    input_box.open()
                    response = ""
                if response == 365*24*60:
                    global go_to_next_level
                    go_to_next_level = True
                else:
                    try_again.show()
        elif try_again.handle_event(event, input_box):
            pass
        return True

def interact(player):
    c = contact.generate(player, doorstep)
    if c.overlap > 0:
        global at_the_door
        at_the_door = True
        

def draw(window, characters):
    window.blit(background, (0, 0))
    objects = characters + sprites
    objects.sort(key=lambda obj : obj.pos.y)
    for obj in objects:
        obj.draw(window, horizon, yfactor)
    if at_the_door:
        window.blit(cloud, (0,0))
        input_box.draw(window)
    try_again.draw(window)
