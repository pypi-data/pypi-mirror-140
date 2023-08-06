def get_keys():
    '获取按键'
    import os
    import pygame.locals
    path = os.path.join(os.path.dirname(__file__), 'keys.py')
    srclines = ["class keys(IntEnum):\n    '用于获取键盘按键的类'\n"]
    for k, v in vars(pygame.locals).items():
        if k.startswith('K_'):
            if k[2].isalpha():
                k = k[2:]
            srclines.append("    %s = %d\n" % (k.upper(), v))
    srclines.append("\nclass keymods(IntEnum):\n")
    for k, v in vars(pygame.locals).items():
        if k.startswith('KMOD_'):
            srclines.append("    %s = %d\n" % (k[5:].upper(), v))
    strings = 'from enum import IntEnum\n\n'
    for s in srclines:
        if not s.endswith('\n'):
            s += '\n'
        strings += s
    with open(path, 'w+', encoding='utf-8') as f:
        f.write(strings)


if __name__ == '__main__':
    get_keys()
