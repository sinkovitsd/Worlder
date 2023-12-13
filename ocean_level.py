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
ice_cream = False
in_boat = False

yfactor = 0.3
horizon = 490
original_speed = 0

start_pos = (100,1500,0)

background = pygame.image.load("ocean_scene_new.png").convert()
sign_image = pygame.image.load("ocean_sign.png").convert()
#sign_image.set_colorkey((127,127,127))

boat_image = pygame.image.load("boat.png").convert()
boat_image.set_colorkey((127,127,127))

ice_cream_image = pygame.image.load("ice_cream.png").convert()
ice_cream_image.set_colorkey((255,255,255))
scale = 0.5
width = ice_cream_image.get_width()*scale
height = ice_cream_image.get_height()*scale
ice_cream_image = pygame.transform.scale(ice_cream_image, [width, height])

def screen_to_world(point):
    return Vector3(point[0], (point[1] - horizon)/yfactor, 0)

def world_to_screen(pos):
    return Vector2(pos.x, horizon + pos.y*yfactor - pos.z)

def ground(point):
    return 0

def ceiling(point):
    return math.inf

boat = Sprite3D(boat_image, visible=False, pos=screen_to_world([1057+50, 890+40]), origin=Vector2(245, 200), 
                mass=math.inf, collide_shape=Polygon(local_points=[[-220, -30], [220,-30], [220, 30], [-220, 30]]))

in_boat_boundary = Sprite3D(boat_image, visible=False, pos=boat.pos,
                            mass=math.inf, collide_shape=Polygon(local_points=[[-50, -35], [50,-35], [50, 25], [-50, 25]]))

water_boundary = Sprite3D(visible=False, mass=math.inf,
                         collide_shape=Polygon(local_points=[screen_to_world([1100+40,400])[0:2],screen_to_world([1025+20,1200])[0:2],
                                                             screen_to_world([1920,1200])[0:2],screen_to_world([1920,400])[0:2]]))

land_boundary = Sprite3D(visible=False, mass=math.inf,
                         collide_shape=Polygon(local_points=[screen_to_world([1100+40,400])[0:2],screen_to_world([1025+20,1200])[0:2],
                                                             screen_to_world([0,1200])[0:2],screen_to_world([0,400])[0:2]]))

# sign = Sprite3D(visible=False, mass=math.inf,
#                 collide_shape=Polygon(local_points=[screen_to_world([1037,598])[0:2],screen_to_world([949,698])[0:2],
#                                                     screen_to_world([926,774])[0:2],screen_to_world([1022,872])[0:2]]))

sign = Sprite3D(visible=False, mass=math.inf,
                collide_shape=Polygon(local_points=[screen_to_world([1023,531])[0:2],screen_to_world([934,630])[0:2],
                                                    screen_to_world([917,706])[0:2],screen_to_world([1007,799])[0:2]]))

ice_cream_stand = Sprite3D(visible=False, mass=math.inf,
                collide_shape=Polygon(local_points=[screen_to_world([440,400])[0:2],screen_to_world([440,548])[0:2],
                                                    screen_to_world([588,571])[0:2],screen_to_world([759,548])[0:2],screen_to_world([759,400])[0:2]]))

font = pygame.font.SysFont("inkfree", 80, True)
input_box = InputBox(font, (960, 900), color=(171,148,35), bg_color=(239,228,176), cursor=True)

sprites = [boat]

#goal_polygon = Sprite3D(None, visible=False, pos=(1642, 188/yfactor, 0), collide_shape=Polygon(local_points=[[0, 0], [0, 89/yfactor], [178, 89/yfactor], [178, 0]]))


def handle_event(event):
    global at_the_sign, answered, ice_cream
    if event.type == USEREVENT:
        ice_cream = False
        return True
    if at_the_sign:
        if input_box.handle_event(event):
            if input_box.finished:
                try:
                    response = input_box.text
                    response = response.replace("am","")
                    response = response.replace(" ","")
                    print("string", response)
                except ValueError:
                    input_box.clear()
                    input_box.open()
                    response = ""
                if response == str((2-3+12)%12)+":30":
                    at_the_sign = False
                    answered = True
                    boat.visible = True
                else:
                    try_again.show()
        elif try_again.handle_event(event, input_box):
            pass
        return True
    return False

def interact(player):
    # pos = world_to_screen(player.pos)
    # pos = [int(pos.x), int(pos.y)]
    # r, g, b, a = tuple(background.get_at(pos))
    # in_water = (g/r < 0.7)
    global in_boat, water_boundary, sprites, original_speed
    if in_boat:
        c = contact.generate(player, land_boundary, resolve=True)
    else:
        c = contact.generate(player, water_boundary, resolve=True)
    c = contact.generate(player, sign, resolve=False)
    if not answered and c.overlap > 0:
        global at_the_sign
        at_the_sign = True
    c = contact.generate(player, ice_cream_stand, resolve=True)
    global ice_cream
    if not ice_cream and c.overlap > 0:
        ice_cream = True
        pygame.time.set_timer(USEREVENT, 3000)
    if answered and player.pos.x + player.origin.x - 30 > background.get_width():
        global go_to_next_level
        go_to_next_level = True
        player.speed = original_speed
    if not answered and not in_boat and boat.visible:
        contact.generate(player, in_boat_boundary, resolve=True)
    if answered and not in_boat and boat.visible and contact.generate(player, in_boat_boundary, resolve=False).overlap > 20:
        in_boat = True
        player.pos = boat.pos + Vector3(0,0,0)
        #player.destination = screen_to_world((1920,850))
        original_speed = player.speed
        player.speed = 300
        sprites.remove(boat)
        
def draw(window, characters):
    player = characters[0]
    window.blit(background, (0, 0))
    objects = characters + sprites
    objects.sort(key=lambda obj : obj.pos.y)
    for obj in objects:
        obj.draw(window, horizon, yfactor)
    if ice_cream:
        image = ice_cream_image
        window.blit(image, world_to_screen(player.pos) 
                    + Vector2((0.37*player.image.get_width()+image.get_width()/2)*player.facing - image.get_width()/2, 
                              -player.image.get_height()*0.4 - image.get_height()/2))
    if in_boat:
        boat.pos = Vector3(player.pos)
        boat.draw(window, horizon, yfactor)
    if at_the_sign:
        window.blit(sign_image, (0,0))
        input_box.draw(window)
    try_again.draw(window)
