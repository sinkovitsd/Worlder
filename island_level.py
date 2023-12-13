import pygame
from pygame.locals import *
from physics_objects import Sprite3D, Polygon, Circle
from pygame.math import Vector2, Vector3
import math
import contact
from text import textbox, InputBox
import try_again

go_to_next_level = False

yfactor = 0.5
horizon = 0

def screen_to_world(point):
    return Vector3(point[0], (point[1] - horizon)/yfactor, 0)

def world_to_screen(pos):
    return Vector2(pos.x, horizon + pos.y*yfactor - pos.z)

start_pos = screen_to_world([1320,700])

index = 0

slides = []
slides.append(pygame.image.load("island_scene1.png").convert())
slides.append(pygame.image.load("island_scene2.png").convert())
slides.append(pygame.image.load("island_scene3.png").convert())

badge_image = pygame.image.load("badge_W.png").convert()
badge_image.set_colorkey((255,255,255))
scale = 1/4
width = badge_image.get_width()*scale
height = badge_image.get_height()*scale
badge_image = pygame.transform.scale(badge_image, [width, height])

badge_given = False

buddy_image = pygame.image.load("buddy.png").convert()
buddy_image.set_colorkey((255,255,255))
scale = 1/2
width = buddy_image.get_width()*scale
height = buddy_image.get_height()*scale
buddy_image = pygame.transform.scale(buddy_image, [width, height])

buddy_run = False

buddy = Sprite3D(buddy_image, visible=False, pos=screen_to_world([625,590+50]), origin=(115*scale,270*scale),
                 collide_shape=Circle(radius=115))


def ground(point):
    return 0

def ceiling(point):
    return math.inf


font = pygame.font.SysFont("inkfree", 60)
#input_box = InputBox(font, (600, 590), color=(128,64,64), bg_color=(185,122,87), cursor=True)

sprites = [buddy]

def handle_event(event):
    global index, go_to_next_level, badge_given, buddy_run
    if event.type == KEYDOWN:
        if event.key in (K_BACKSPACE, K_LEFT):
            if index > 0:
                index -= 1
        else:
            if index + 1 < len(slides):
                index += 1
            else:
                go_to_next_level = True
            if index == 1:
                badge_given = True
                pygame.time.set_timer(USEREVENT, 1000, 1)
    elif event.type == USEREVENT:
        if not buddy.visible:
            buddy.visible = True
            pygame.time.set_timer(USEREVENT, 500, 1)
        else:
            buddy_run = True
    return True

def interact(player):
    player.image = player.images[1]
    player.facing = -1
    if buddy_run:
        r = player.pos + Vector3(-20,0,-55) - buddy.pos
        if r.magnitude() > 130:
            buddy.vel = r.normalize()*600
            buddy.update(1/60)
        
def draw(window, characters):
    window.blit(slides[index], (0, 0))
    objects = characters + sprites
    objects.sort(key=lambda obj : obj.pos.y)
    for obj in objects:
        obj.draw(window, horizon, yfactor)
    player = characters[0]
    if badge_given:
        image = badge_image
        window.blit(image, world_to_screen(player.pos) 
                    + Vector2((0.37*player.image.get_width()+image.get_width()/2)*player.facing - image.get_width()/2, 
                              -player.image.get_height()*0.4 - image.get_height()/2))
    buddy.draw(window, horizon, yfactor)
    
        