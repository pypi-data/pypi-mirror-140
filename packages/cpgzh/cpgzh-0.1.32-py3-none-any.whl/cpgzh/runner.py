import pgzrun
import sys


def go():
    "启动游戏引擎"
    pgzrun.go()


def get_screen():
    "返回当前游戏所在的屏幕"
    mod = sys.modules["__main__"]
    return mod.screen
