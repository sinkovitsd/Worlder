import pygame
from pygame.locals import *
from text import textbox, InputBox

pygame.init()
pygame.font.init()
   
window = pygame.display.set_mode(flags=FULLSCREEN)

clock = pygame.time.Clock()
fps = 60
dt = 1/fps

# text='''Our Father who art in Heaven, hallowed be Thy name.  
# Thy kingdom come.  Thy will be done on earth as it is in heaven.
# Give us this day our daily bread.
# And forgive us our trespasses as we forgive those who trespass against us.
# Lead us not into temptation, but deliver us from evil.
# For Thine is the kingdom and the power and the glory, forever and ever. Amen.'''

text = ""
font_list = pygame.font.get_fonts()
font_list.sort()
print(font_list)

pygame.key.set_repeat(500, 67)

font = pygame.font.SysFont("kristenitc", 40)

width = 700
x = 50
spacing = 1
text_box = textbox(text, font, width, transparent=False, spacing=spacing, line_breaks=True)

input_box = InputBox(font, (x+width+50, 100), color=(255,255,255), prompt="> ")

running = True
while running:
    pygame.display.update()
    dt = clock.tick()/1000
    window.fill([75,0,130])

    while event := pygame.event.poll():
        if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
            running = False
        elif input_box.handle_event(event):
            if input_box.finished:
                text += " "
                text += input_box.text + "\n"
                input_box.clear()
                input_box.open()
                text_box = textbox(text, font, width, transparent=False, spacing=spacing, line_breaks=True)

    pygame.draw.line(window, (0,255,0), (x-1,0), (x-1,window.get_height()))
    pygame.draw.line(window, (0,255,0), (x+width,0), (x+width,window.get_height()))
    window.blit(text_box, (x,0))
    input_box.draw(window) 
    
