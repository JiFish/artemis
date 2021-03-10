import artemis
import builtins
import math
import random
from types import SimpleNamespace

pyboxbuiltins = dict()
exclude_list = ['__import__', 'exit', 'quit', 'print', 'input', 'open']
for i in dir(builtins):
    if i not in exclude_list:
        pyboxbuiltins[i] = getattr(builtins, i)

def safeprint(*objects, sep=' ', end='\n', file=None, flush=False):
    printstr = sep.join([str(o) for o in objects])
    printstr += end
    artemis.ui_print(printstr, True if flush else None)

def safeinput(prompt):
    i = artemis.ui_input(prompt)
    artemis.ui_print("\n")
    return i

def safeopen(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None):
    artemis.dos.test_filename(file)
    return open(file, mode, buffering, encoding, errors, newline, closefd, opener)

def refresh():
    artemis.draw()
    artemis.tick()

class ScreenAccessor():
    def __getitem__(self, index):
        return artemis.screen[index]

    def __setitem__(self, index, value):
        artemis.screen[index].set(value)

    def __len__(self):
        return len(artemis.screen)

    def __repr__(self):
        return artemis.screen.__repr__()

pyboxbuiltins["print"] = safeprint
pyboxbuiltins["input"] = safeinput
pyboxbuiltins["open"] = safeopen
pyboxbuiltins["key"] = artemis.ui_input_key
pyboxbuiltins["system_time"] = artemis.get_system_time
pyboxbuiltins["wait"] = artemis.wait
pyboxbuiltins["math"] = math
pyboxbuiltins["random"] = random

# Screen 'module'
pyboxbuiltins["screen"] = SimpleNamespace(
    ink = artemis.set_palette,
    cls = artemis.cls,
    mode = artemis.set_mode,
    symbol = artemis.redefine_char,
    border = artemis.set_border,
    cursor = artemis.set_cursor,
    cursor_symbol = artemis.set_cursor_symbol,
    cursor_x = artemis.get_cursor_x,
    cursor_y = artemis.get_cursor_y,
    color = artemis.set_color,
    plot = artemis.ui_psuedo_plot,
    printw = artemis.ui_print_window,
    printb = artemis.ui_print_breaking_list,
    loads = artemis.load_screen,
    dumps = artemis.get_screen_dump,
    symbol_image = artemis.load_charset,
    refresh = refresh,
    refresh_wait = artemis.disable_auto_draw,
    rsts = artemis.reset_screen,
    screen = ScreenAccessor()
)

# Sound 'module'
pyboxbuiltins["sound"] = {
    'play': artemis.tass.play_string,
    'stop': artemis.tass.stop
}
