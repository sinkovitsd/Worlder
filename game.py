import pygame
from pygame.locals import *
from pygame.math import Vector2, Vector3
from physics_objects import Sprite3D, Polygon
import contact
import importlib

levels = ["start_level", "wall_level", "stream_level", "cave_level", 
          "underground_level", "underground_3_paths_level", "path_up_level", 
          "campground_checkin_level", "tent_level", "snowy_level"]
level_index = 9

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

speed = 1000
gravity = 2769

x = player_image.get_width()/2*0.7
player = Sprite3D(player_image, pos=level.start_pos, origin=Vector2(player_image.get_width()/2, player_image.get_height()-18*scale),
                  collide_shape=Polygon(local_points=[[-x,-x/5], [x,-x/5], [x, x/5], [-x, x/5]]))
player.images = [player_image, player_image2]
player.facing = 1
player.height = 610*scale

#print("player", player.collide_shape.points)

destination = Vector3(player.pos)
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
        elif event.type==MOUSEBUTTONDOWN or event.type==MOUSEMOTION and pygame.mouse.get_pressed()[0]:
            if event.pos[1] >= level.horizon:
                destination = level.screen_to_world(event.pos)
                
    player.clear_force()
    player.add_force(Vector3(0,0,-gravity))
    
    r = destination - player.pos
    r.z = 0
       
    if player.pos.z <= level.ground(player.pos):
        if r.magnitude() > speed * dt:
            player.vel = r.normalize()*speed + Vector3(0,0,player.vel.z)
        else:
            player.vel = Vector3(0, 0, player.vel.z)
            player.pos = destination + Vector3(0 , 0, player.pos.z)
    
    if player.vel.x > 0:
        player.image = player.images[0]
        player.facing = 1
    if player.vel.x < 0:
        player.image = player.images[1]
        player.facing = -1

    if player.pos.z <= level.ground(player.pos) and pygame.key.get_pressed()[K_SPACE]:
        player.vel.z = 1000

    for obj in level.sprites:
        contact.generate(player, obj, resolve=True)
    
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
        print(level_index)
        print(levels[level_index])
        window.blit(loading, (0,0))
        pygame.display.update()
        level = importlib.import_module(levels[level_index])
        pygame.event.clear()
        player.set(pos=level.start_pos)
        player.vel = Vector3(0,0,0)
        destination = Vector3(player.pos)
        
    level.draw(window, [player])
   