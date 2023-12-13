import pygame
from pygame.locals import *
from pygame.math import Vector2, Vector3
from physics_objects import Sprite3D, Polygon
import contact
import importlib

levels = ["title_level", "start_level", "wall_level", "stream_level", "cave_level", 
          "underground_level", "underground_3_paths_level", "path_up_level", 
          "campground_checkin_level", "tent_level", "snowy_level" ,"ocean_level",
          "island_level", "end_credit_level"]
level_index = 0

pygame.init()
pygame.font.init()

window = pygame.display.set_mode(flags=FULLSCREEN)

level = importlib.import_module(levels[level_index])

loading = pygame.image.load("loading.png").convert()

player_image = pygame.image.load("Bella.png").convert()
scale = 0.5
width = player_image.get_width()*scale
height = player_image.get_height()*scale
player_image = pygame.transform.scale(player_image, [width, height])
player_image.set_colorkey([255,255,255])
player_image2 = pygame.image.load("Bella_left.png").convert()
player_image2 = pygame.transform.scale(player_image2, [width, height])
player_image2.set_colorkey([255,255,255])

clock = pygame.time.Clock()
fps = 60
dt = 1/fps

gravity = 2769
jumping = False

x = player_image.get_width()/2*0.7
player = Sprite3D(player_image, pos=level.start_pos, origin=Vector2(player_image.get_width()/2, player_image.get_height()-18*scale),
                  collide_shape=Polygon(local_points=[[-x,-x/5], [x,-x/5], [x, x/5], [-x, x/5]]))
player.images = [player_image, player_image2]
player.facing = 1
player.height = 610*scale
player.speed = 1000

#print("player", player.collide_shape.points)

buttons_active = False

player.destination = Vector3(player.pos)
running = True
while running:
    pygame.display.update()
    clock.tick(fps)
    window.fill([75,0,130])

    while event := pygame.event.poll():
        if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
            running = False
        elif level.handle_event(event):
            pass
        elif event.type==MOUSEBUTTONDOWN or buttons_active and event.type==MOUSEMOTION and event.buttons[0]:
            if event.type == MOUSEBUTTONDOWN:
                buttons_active = True
            pos = Vector2(event.pos)
            if pos.y < level.horizon:
                pos.y = level.horizon
            player.destination = level.screen_to_world(pos)
        elif event.type == KEYDOWN and event.key == K_SPACE:
            jumping = True
        elif event.type == KEYUP and event.key == K_SPACE:
            jumping = False

                
    player.clear_force()
    player.add_force(Vector3(0,0,-gravity))
    
    r = player.destination - player.pos
    r.z = 0
       
    if player.pos.z <= level.ground(player.pos):
        if r.magnitude() > player.speed * dt:
            player.vel = r.normalize()*player.speed + Vector3(0,0,player.vel.z)
        else:
            player.vel = Vector3(0, 0, player.vel.z)
            player.pos = player.destination + Vector3(0 , 0, player.pos.z)
    
    if player.vel.x > 0:
        player.image = player.images[0]
        player.facing = 1
    if player.vel.x < 0:
        player.image = player.images[1]
        player.facing = -1

    if player.pos.z <= level.ground(player.pos) and jumping and pygame.key.get_pressed()[K_SPACE]:
        player.vel.z = 1000

    player.update(dt)
    
    ground = level.ground(player.pos)
    if player.pos.z < ground:
        player.pos.z = ground
        player.vel.z = 0

    ceiling = level.ceiling(player.pos)
    if player.pos.z + player.height >= ceiling:
        player.pos.z = ceiling - player.height
        player.vel.z = 0

    level.interact(player)
    if level.go_to_next_level:
        level_index += 1
        buttons_active = False
        print(level_index)
        if level_index >= len(levels):
            level_index = 0
            print("Going back to the title screen.")
        print(levels[level_index])
        window.blit(loading, (0,0))
        pygame.display.update()
        level = importlib.import_module(levels[level_index])
        pygame.event.clear()
        player.set(pos=level.start_pos)
        player.vel = Vector3(0,0,0)
        player.destination = Vector3(player.pos)
        
    level.draw(window, [player])
   