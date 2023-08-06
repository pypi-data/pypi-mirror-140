import pygame
from pgzero.constants import mouse as mouse_keys


class Mouse(object):
    '鼠标类'

    def __init__(self) -> None:
        '鼠标类'
        self.keys = mouse_keys

    def get_pos(self):
        '获取鼠标坐标'
        return pygame.mouse.get_pos()

    def set_pos(x, y=None):
        if y == None:
            pos = x
        else:
            pos = (x, y)
        pygame.mouse.set_pos(pos)

    def hide(self) -> None:
        "隐藏鼠标"
        pygame.mouse.set_visible(False)

    def show(self) -> None:
        "显示鼠标"
        pygame.mouse.set_visible(True)


mouse = Mouse()
