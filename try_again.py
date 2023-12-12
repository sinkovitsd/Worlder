import pygame

active = False
try_again_sign = pygame.image.load("try_again.png").convert()
try_again_sign.set_colorkey((127,127,127))

def show():
    global active
    active = True
    pygame.time.set_timer(pygame.USEREVENT, 2000, 1)

def handle_event(event, input_box):
    global active
    if event.type == pygame.USEREVENT:
        active = False
        input_box.clear()
        input_box.open()

def draw(window):
    if active:
        window.blit(try_again_sign, [(window.get_width()-try_again_sign.get_width())/2, (window.get_height()-try_again_sign.get_height())/2])