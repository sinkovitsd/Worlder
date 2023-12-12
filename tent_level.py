import pygame
from pygame.locals import *
from physics_objects import Sprite3D, Polygon, Circle, Wall
from pygame.math import Vector2, Vector3
import math
import contact
from text import textbox, InputBox
import try_again

go_to_next_level = False
sleeping = False

talking = False
at_the_sign = False
answered = False

yfactor = 0.3
horizon = 600


background = pygame.image.load("tent_scene.png").convert()
sleeping_background = pygame.image.load("sleeping.png").convert()
#sign = pygame.image.load("tree_sign.png").convert()
#sign.set_colorkey((127,127,127))

def screen_to_world(point):
    return Vector3(point[0], (point[1] - horizon)/yfactor, 0)

def world_to_screen(pos):
    return Vector2(pos.x, horizon + pos.y*yfactor - pos.z)

start_pos = screen_to_world([50, 950])

def ground(point):
    return 0

def ceiling(point):
    return math.inf

tent = Sprite3D(visible=False, mass=math.inf,
                         collide_shape=Polygon(local_points=[screen_to_world([315,600])[0:2], screen_to_world([315,735])[0:2],screen_to_world([383,824])[0:2],
                                                             screen_to_world([985,821])[0:2],screen_to_world([1041,685])[0:2],screen_to_world([1041,600])[0:2]]))

sleeping_bag = Sprite3D(visible=False, mass=math.inf, 
                collide_shape=Polygon(local_points=[screen_to_world([610,855])[0:2],screen_to_world([745,865])[0:2],
                                                    screen_to_world([763,567])[0:2],screen_to_world([657,567])[0:2]]))

horizon_boundary = Sprite3D(visible=False, mass=math.inf, 
                            collide_shape=Polygon(local_points=[screen_to_world([0,700])[0:2],screen_to_world([1920,700])[0:2],
                                                    screen_to_world([1920,500])[0:2],screen_to_world([0,500])[0:2]]))

fire_boundary = Sprite3D(visible=False, mass=math.inf,
                         collide_shape=Polygon(local_points=[screen_to_world([990,500])[0:2],screen_to_world([990,2500])[0:2],
                                                    screen_to_world([1920,2500])[0:2],screen_to_world([1920,500])[0:2]]))

#font = pygame.font.SysFont("inkfree", 60)
#input_box = InputBox(font, (970, 940), color=(0,0,0), bg_color=(66,33,0), transparent=True, cursor=True)

sprites = []#[checkin_boundary, tree, far_boundary, camp_boundary]

#goal_polygon = Sprite3D(None, visible=False, pos=(1642, 188/yfactor, 0), collide_shape=Polygon(local_points=[[0, 0], [0, 89/yfactor], [178, 89/yfactor], [178, 0]]))


def handle_event(event):
    if event.type==USEREVENT:
        global go_to_next_level
        go_to_next_level = True
        return True
    elif sleeping:
        return True
    return False

def interact(player):
    global sleeping
    c = contact.generate(player, sleeping_bag, resolve=True)
    if c.overlap > 0 and not sleeping:
        sleeping = True
        pygame.time.set_timer(USEREVENT, 5000)
    c = contact.generate(player, horizon_boundary, resolve=True)
    c = contact.generate(player, fire_boundary, resolve=True)
    c = contact.generate(player, tent, resolve=True)
    
def draw(window, characters):
    if sleeping:
        window.blit(sleeping_background, (0,0))
    else:
        window.blit(background, (0,0))
        objects = characters + sprites
        objects.sort(key=lambda obj : obj.pos.y)
        for obj in objects:
            obj.draw(window, horizon, yfactor)
        