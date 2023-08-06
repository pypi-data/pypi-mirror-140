import os
import sys
import pygame

mod = sys.modules["__main__"]
try:
    WIDTH = mod.WIDTH
    HEIGHT = mod.HEIGHT
    pygame.init()
    w, h = pygame.display.get_desktop_sizes()[0]
    os.environ['SDL_VIDEO_WINDOW_POS'] = f'{int((w-WIDTH)/2)},{int((h-HEIGHT)/2)}'
except:
    os.environ['SDL_VIDEO_WINDOW_POS'] = '100,100'
    



import pgzrun
def go():
    "启动游戏引擎"
    pgzrun.go()


def get_screen():
    "返回当前游戏所在的屏幕"
    mod = sys.modules["__main__"]
    return mod.screen
