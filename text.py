import pygame
import math
from pygame.locals import *

def textbox(text, font:pygame.font.Font, width:int, color=(0,0,0), bg_color=(255,255,255), transparent=True, line_breaks=False, spacing=1.0):
    if transparent:
        bg_color = [(color[i] + 127) % 256 for i in range(3)]
    if line_breaks:
        text = " \n ".join(line for line in text.splitlines() if line)
    else:
        text = " ".join(line for line in text.splitlines() if line)    
    words = text.split(" ")
    lines = []
    line_words = []
    total_height = 0
    for word in words:
        if word == "":
            continue
        elif word == "\n":
            lines.append(line_words)
            line_image = font.render(" ".join(line_words), True, color, bg_color)
            line_height = line_image.get_height()
            total_height += math.ceil(line_height*spacing)
            line_words = []
            continue
        while True:
            line_words.append(word)
            if len(line_words) > 1:
                line_height = line_image.get_height()
            line_image = font.render(" ".join(line_words), True, color, bg_color)
            #print(*line_words, line_image.get_width())
            if line_image.get_width() > width and len(line_words) > 1:
                word = line_words.pop()
                lines.append(line_words)
                line_words = []
                total_height += math.ceil(line_height*spacing)
            else:
                break
    if len(line_words) > 0:
        lines.append(line_words)
        line_image = font.render(" ".join(line_words), True, color, bg_color)
        line_height = line_image.get_height()
        total_height += math.ceil(line_height*max(1,spacing))
    
    box = pygame.Surface((width, total_height))
    box.fill(bg_color)
    y = 0
    for line_words in lines:
        line_image = font.render(" ".join(line_words), True, color, bg_color)
        line_image.set_colorkey(bg_color)
        box.blit(line_image, (0, y))
        line_height = line_image.get_height()
        y += math.ceil(line_height*spacing)
    if transparent:
        box.set_colorkey(bg_color)
    return box

class InputBox:
    cursor = "_"

    def __init__(self, font:pygame.font.Font, pos=(0,0), color=(0,0,0), bg_color=(255,255,255), transparent=False, cursor=False, prompt="", text=""):
        self.font = font
        self.pos = pos
        self.color = color
        self.bg_color = bg_color
        self.transparent = transparent
        self.cursor = cursor
        self.prompt = prompt
        self.text = text
        self.finished = False
        if transparent:
            bg_color = [(color[i] + 127) % 256 for i in range(3)]

    def handle_event(self, event):
        if event.type == KEYDOWN and not self.finished and not event.mod & (KMOD_CTRL|KMOD_ALT|KMOD_META):
            if event.key in [K_RETURN, K_TAB]:
                self.finished = True
            elif event.key == K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
            return True
        else:
            return False
        
    def clear(self):
        self.text = ""

    def open(self):
        self.finished = False
    
    def draw(self, window):
        display_text = self.prompt + self.text
        if self.cursor:
            display_text += InputBox.cursor
        image = self.font.render(display_text, True, self.color, self.bg_color)
        if self.transparent:
            image.set_colorkey(self.bg_color)
        window.blit(image, self.pos)
 