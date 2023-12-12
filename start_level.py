import pygame
from physics_objects import Sprite3D, Polygon
from pygame.math import Vector2, Vector3
import math
import contact

go_to_next_level = False

yfactor = 0.3
ground_height = 450

start_pos = (200,300,0)

sky = pygame.image.load("sky.png").convert()
flora = pygame.image.load("flora.png").convert()
ground = pygame.image.load("ground_nobush.png").convert()
bush = pygame.image.load("bush.png").convert()
bush.set_colorkey((43,132,43))
tree = pygame.image.load("tree.png").convert()
tree.set_colorkey((43,132,43))

hello = pygame.image.load("hello.png").convert()
hello.set_colorkey((255,255,255))

horizon = sky.get_height()

def screen_to_world(point):
    return Vector3(point[0], (point[1] - horizon)/yfactor, 0)

def world_to_screen(pos):
    return Vector2(pos.x, horizon + pos.y*yfactor - pos.z)

def ground(point):
    return 0

def ceiling(point):
    return math.inf

x=bush.get_width()/2
bush = Sprite3D(bush, mass=math.inf, pos=(271+bush.get_width()/2, (98+bush.get_height())/yfactor, 0), origin=Vector2(bush.get_width()/2, bush.get_height()),
                collide_shape=Polygon(local_points=[[-x,-x/3], [x,-x/3], [x, x/3], [-x, x/3]]))
tree = Sprite3D(tree, pos=(1031+100, (325-150)/yfactor, 0), origin=Vector2(0, 325), 
                mass=math.inf, collide_shape=Polygon(local_points=[[70, -30], [420,-30], [420, 30], [70, 30]]))

print("bush", bush.collide_shape.local_points)
print("bush", bush.collide_shape.points)
print("tree", tree.collide_shape.local_points)
print("tree", tree.collide_shape.points)

sprites = [bush, tree]

goal_polygon = Sprite3D(None, visible=False, pos=(1642, 188/yfactor, 0), collide_shape=Polygon(local_points=[[0, 0], [0, 89/yfactor], [178, 89/yfactor], [178, 0]]))

print("goal", goal_polygon.collide_shape.points)

def handle_event(event):
    return False

def interact(player):
    c = contact.generate(player, goal_polygon)
    global go_to_next_level 
    go_to_next_level = c.overlap > 0

def draw(window, characters):
    window.blit(sky, (0, 0))
    window.blit(ground, (0, horizon))
    objects = characters + sprites
    objects.sort(key=lambda obj : obj.pos.y)
    for obj in objects:
        obj.draw(window, horizon, yfactor)
        if obj in characters:
            window.blit(hello, world_to_screen(obj.pos) - obj.origin + Vector2(obj.image.get_width(),0))


