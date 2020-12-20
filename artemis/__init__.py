# Artemis - Core
#
# These functions draw the sceen, deal with user input, timing etc.
#
# Artemis is technically independent component from JiBASIC. Providing a way to
# manipulate the screen, play sound and read and write from disk.
#
# But if you've come here looking for documentation on the interface... Sorry :(
# This is something I want to improve, but the whole thing needs a refactor first.
#

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

# Windows magic
if os.name == 'nt':
    import ctypes
    myappid = 'jifish.artemis.fc.0' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

import pygame
import pygame.locals
import time
import json
from artemis import dos
from artemis import tass

_activation_time = time.time()

debug = False
fps_flag = False

_CURSOR = ord("_")
_SPACE = ord(" ")

_SCREEN_WIDTH = 40
_SCREEN_HEIGHT = 25
_SCREEN_BUFFER_SIZE = _SCREEN_WIDTH*_SCREEN_HEIGHT
_SCREEN_COLS = 8

_master_pallette = [
[0, 0, 0],
[0, 128, 0],
[128, 0, 0],
[0, 0, 128],
[128, 0, 128],
[0, 128, 128],
[128, 128, 0],
[128, 128, 128],
[0, 255, 0],
[255, 0, 0],
[0, 0, 255],
[255, 0, 255],
[0, 255, 255],
[255, 255, 0],
[255, 255, 255],
[128, 255, 128],
[255, 128, 128],
[128, 128, 255],
[255, 128, 255],
[128, 255, 255],
[255, 255, 128],
[255, 255, 255],
[64, 192, 64],
[192, 64, 64],
[64, 64, 192],
[192, 64, 192],
[64, 192, 192],
[192, 192, 64],
[0, 64, 0],
[64, 0, 0],
[0, 0, 64],
[64, 64, 64]]

col_lookup = _master_pallette[:_SCREEN_COLS]

foreground_col = 1;
background_col = 0;
border_col = 0;
# Screen buffer, a tuplet for each cell
screen = [[_SPACE,foreground_col,background_col] for _ in range(_SCREEN_BUFFER_SIZE)]
fullscreen = False


def load_tile_table(filename, width, height):
    image = pygame.image.load(filename)#.convert()
    image_width, image_height = image.get_size()
    tile_table = []
    for tile_y in range(0, int(image_height/height)):
        #line = []
        #tile_table.append(line)
        for tile_x in range(0, int(image_width/width)):
            rect = (tile_x*width, tile_y*height, width, height)
            tile_table.append(image.subsurface(rect))
    return tile_table

# Some pygame initalisation
# TODO: Variable sized window?
pygame.init()
screen_surface = pygame.display.set_mode((672, 432))
pygame.mouse.set_visible(False)
text_layer = pygame.Surface((_SCREEN_WIDTH*8, _SCREEN_HEIGHT*8))
text_layer.fill((0, 0, 0))
scaled_screen = pygame.Surface((640, 400))
table = load_tile_table(os.path.dirname(os.path.realpath(__file__))+"/charset.png", 8, 8)
master_table = load_tile_table(os.path.dirname(os.path.realpath(__file__))+"/charset.png", 8, 8)
pygame.display.set_caption("Artemis Fantasy Microcomputer")
pygame.display.set_icon(pygame.transform.scale(table[239], (64, 64)))
clock = pygame.time.Clock()

cursor_pos = 0

# Maximum instructions before forcing a tick
max_ins = 10000
ins_cnt = 0

def ins_tick():
    global ins_cnt
    ins_cnt += 1
    if ins_cnt > max_ins:
        tick()
        if debug: print("Forced tick after "+str(max_ins)+" instructions")

def set_palette(index, r, g, b):
    for i in [r,b,g]:
        if i < 0 or i > 4:
            raise ValueError("Invalid RGB value")
    if index < 0 or index > 15:
        raise ValueError("Invalid palette index")
    col_lookup[index] = [int(round(r*63.75)),
                         int(round(g*63.75)),
                         int(round(b*63.75))]

def cls():
    global screen, foreground_col, background_col, cursor_pos
    screen = [[_SPACE,foreground_col,background_col] for _ in range(_SCREEN_BUFFER_SIZE)]
    cursor_pos = 0

def set_mode(mode):
    global _SCREEN_WIDTH, _SCREEN_HEIGHT, _SCREEN_COLS, _SCREEN_BUFFER_SIZE
    global text_layer, background_col, foreground_col, border_col, col_lookup
    if mode == 0:
        _SCREEN_WIDTH = 20
        _SCREEN_HEIGHT = 25
        _SCREEN_COLS = 16
    elif mode == 1:
        _SCREEN_WIDTH = 40
        _SCREEN_HEIGHT = 25
        _SCREEN_COLS = 8
    elif mode == 2:
        _SCREEN_WIDTH = 80
        _SCREEN_HEIGHT = 25
        _SCREEN_COLS = 4
    elif mode == 3:
        _SCREEN_WIDTH = 80
        _SCREEN_HEIGHT = 50
        _SCREEN_COLS = 2
    elif mode == 4:
        _SCREEN_WIDTH = 40
        _SCREEN_HEIGHT = 50
        _SCREEN_COLS = 4
    elif mode == 5:
        _SCREEN_WIDTH = 24
        _SCREEN_HEIGHT = 15
        _SCREEN_COLS = 16
    elif mode == 6:
        _SCREEN_WIDTH = 16
        _SCREEN_HEIGHT = 10
        _SCREEN_COLS = 32
    else:
        raise ValueError("Invalid Mode")
    _SCREEN_BUFFER_SIZE = _SCREEN_WIDTH*_SCREEN_HEIGHT
    text_layer = pygame.Surface((_SCREEN_WIDTH*8, _SCREEN_HEIGHT*8))

    # Reducing colours
    if len(col_lookup) > _SCREEN_COLS:
        # Cut the pallete down to the new max colours
        col_lookup = col_lookup[:_SCREEN_COLS]
        foreground_col = min(foreground_col,_SCREEN_COLS-1)
        if background_col >= _SCREEN_COLS: background_col = 0
        if border_col >= _SCREEN_COLS: border_col = 0
    # Increasing colours
    elif len(col_lookup) < _SCREEN_COLS:
        # Pad the pallete with the master pallete to reach the new max colours
        col_lookup = col_lookup+_master_pallette[len(col_lookup):_SCREEN_COLS]
    cls()

def set_caption(caption):
    pygame.display.set_caption(caption)

def redefine_char(chr, charstring):
    global table
    # Reset character
    if charstring == "":
        table[chr] = master_table[chr].copy()
    # Redfine character
    else:
        charstring = list(charstring.ljust(8*8))
        if chr < 0 or chr > 255:
            raise ValueError()
        for i in range(8*8):
            pix = 0 if charstring[i] == ' ' else 1
            table[chr].set_at((i % 8, i // 8), pix)
    # Special case for char 239
    if chr == 239:
        table[239].set_palette_at(0, [0, 0, 0])
        table[239].set_palette_at(1, [255, 255, 255])
        pygame.display.set_icon(pygame.transform.scale(table[239], (64, 64)))

def redefine_char_from_int_list(chr, intlist):
    charstring = ""
    for i in intlist:
        i = max(0,min(255,i))
        for j in list(bin(i)[2:].zfill(8)):
            charstring += "X" if j == "1" else " "
    redefine_char(chr, charstring)

def get_cell(pos):
    if pos < 0 or pos >= _SCREEN_BUFFER_SIZE:
        raise IndexError()
    return screen[pos]

def set_cell(pos, cell):
    if pos < 0 or pos >= _SCREEN_BUFFER_SIZE:
        raise IndexError()
    screen[pos] = cell

def manipulate_cell(pos, key, val):
    global screen
    if pos < 0 or pos >= _SCREEN_BUFFER_SIZE or key < 0 or key > 2:
        raise IndexError()
    if key == 0 and (val < 0 or val > 255):
        raise ValueError()
    if key > 0 and (val < 0 or val >= _SCREEN_COLS):
        raise ValueError()

    screen[pos][key] = val

def set_border(col):
    global border_col
    border_col = col;
    draw()
    tick()

def split_string(str, limit, sep=" "):
    if (str == ""):
        return ['']
    words = str.split()
    if max(map(len, words)) > limit:
        raise ValueError("limit is too small")
    res, part, others = [], words[0], words[1:]
    for word in others:
        if len(sep)+len(word) > limit-len(part):
            res.append(part)
            part = word
        else:
            part += sep+word
    if part:
        res.append(part)
    return res

def print_block(str, xpos, ypos, len = -1, height = _SCREEN_HEIGHT):
    if len == -1:
        len = _SCREEN_WIDTH-xpos
    height = ypos+height
    for lines in str.split("\n"):
        lines = split_string(lines, len)
        for line in lines:
            ui_print(line.ljust(len, ' '), (ypos*_SCREEN_WIDTH)+xpos)
            ypos += 1
            if (ypos == height): return

def print_block_full(str):
    print_block(str,0,0,_SCREEN_WIDTH,_SCREEN_HEIGHT)

ticktime = _activation_time
def tick():
    global ins_cnt, ticktime
    ins_cnt = 0

    if fps_flag:
        print ("{} fps".format(1/max(0.00000000001,time.time()-ticktime)))
        ticktime = time.time()

    clock.tick(30)

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            raise KeyboardInterrupt()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL:
                raise KeyboardInterrupt()
            elif event.key == pygame.K_RETURN and pygame.key.get_mods() & pygame.KMOD_ALT:
                flip_fullscreen()
                return []

    return events

def wait(secs = 1):
    loops = round(secs*30)
    for _ in range(loops):
        tick()

def scroll_screen():
    global screen, foreground_col, background_col, cursor_pos

    if (len(screen) <= _SCREEN_BUFFER_SIZE): return

    while (len(screen) > _SCREEN_BUFFER_SIZE):
        screen = screen[_SCREEN_WIDTH:]
        cursor_pos = cursor_pos - _SCREEN_WIDTH
    screen = screen + [[_SPACE,foreground_col,background_col] for _ in range(_SCREEN_BUFFER_SIZE-len(screen))]


def draw():
    global screen, debug
    xpos = 0
    ypos = 0
    for x in screen:
        char, foreground, background = x
        tile = table[char]
        tile.set_palette_at(0, col_lookup[background])
        tile.set_palette_at(1, col_lookup[foreground])
        text_layer.blit(tile, (xpos*8, ypos*8))
        if debug:
            pygame.draw.rect(text_layer,[255,0,0],[xpos*8,ypos*8,(xpos*8)+9,(ypos*8)+9],1)
        xpos = xpos + 1
        if (xpos == _SCREEN_WIDTH):
            xpos = 0
            ypos = ypos + 1
            if ypos == _SCREEN_HEIGHT:
                break
    pygame.transform.scale(text_layer, [640,400], scaled_screen)
    screen_surface.fill(col_lookup[border_col])
    screen_surface.blit(scaled_screen, [16,16])
    pygame.display.flip()

def set_cursor(x, y):
    global cursor_pos
    cursor_pos = (y*_SCREEN_WIDTH)+x

def set_color(f, b = -1):
    global foreground_col, background_col
    if f >= _SCREEN_COLS or b >= _SCREEN_COLS or f < 0 or b < -1:
        raise ValueError("Invalid color")
    foreground_col = f
    if (b != -1):
        background_col = b

def ui_print(text, pos = -1):
    global screen, cursor_pos, foreground_col, background_col
    text = str(text)
    if pos >= 0:
        cursor_pos = pos

    # Deal with newlines
    if "\n" in text:
        p = cursor_pos % _SCREEN_WIDTH
        st = list(text)
        for i in range(len(st)):
            if st[i] == "\n":
                st[i] = " "*(_SCREEN_WIDTH-p)
                p = -1
            p = (p + 1) % _SCREEN_WIDTH
        text = "".join(st)

    # Build subbuffer
    newbuff = []
    for i in list(text):
        newbuff.append([ord(i), foreground_col, background_col])
    # Update Screen Buffer
    textlen = len(text)
    screen = screen[:cursor_pos]+newbuff+screen[(cursor_pos+textlen):]
    # Move cursor
    cursor_pos += textlen
    # Scroll screen
    scroll_screen()

def ui_print_breaking_list(plist):
    line_row = 0
    # Blank link at end
    plist.append("")
    pak_str = "- PRESS ANY KEY TO CONTINUE -"[:_SCREEN_WIDTH-1]
    pak_str = (" "*((_SCREEN_WIDTH-len(pak_str))//2)) + pak_str + "\n"
    # Loop the list,
    # pausing when we reach the height of the screen
    for line in plist:
        lines_in_row = max(1,-(-len(line)//_SCREEN_WIDTH))
        line_row += lines_in_row
        if line_row >= _SCREEN_HEIGHT:
            ui_print(pak_str)
            ui_input_key()
            set_cursor(0,_SCREEN_HEIGHT-1)
            line_row = lines_in_row
        ui_print(line+"\n")

def ui_input(prompt = "", max_len = 0):
    global screen, cursor_pos, foreground_col, background_col
    ui_print(prompt + chr(_CURSOR))
    cursor_pos -= 1
    if max_len == 0:
        max_len = 1024
    input = ''
    draw()
    cursorbuff = [[_CURSOR, foreground_col, background_col]]
    pygame.key.set_repeat(500,33)
    while True:
        events = tick()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    pygame.key.set_repeat(0)
                    return input
                elif event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                    if (input != ''):
                        cursor_pos -= 1
                        screen = screen[:cursor_pos] + cursorbuff + [[_SPACE, foreground_col, background_col]] + screen[cursor_pos+2:]
                        input = input[:-1]
                        draw()
                elif event.unicode != '' and ord(event.unicode) < 255 and event.unicode != "\n" and len(input) < max_len:
                    screen = screen[:cursor_pos] + [[ord(event.unicode), foreground_col, background_col]] + cursorbuff + screen[cursor_pos+2:]
                    cursor_pos += 1
                    input = input + event.unicode
                    scroll_screen()
                    draw()

def ui_input_key(impatient = False):
    draw()
    while True:
        events = tick()
        for event in events:
            if event.type == pygame.QUIT:
                raise KeyboardInterrupt()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    raise KeyboardInterrupt()
                return event.key
    if impatient: return -1

def ui_are_you_sure():
    ui_print("Are you sure? (Y/N)")
    result = (ui_input_key() == pygame.K_y)
    ui_print("\n")
    return result

def ui_input_numb():
    draw()
    while True:
        events = tick()
        for event in events:
            if event.type == pygame.QUIT:
                raise KeyboardInterrupt()
            if event.type == pygame.KEYDOWN:
                if   event.key == pygame.K_0: return 0
                elif event.key == pygame.K_1: return 1
                elif event.key == pygame.K_2: return 2
                elif event.key == pygame.K_3: return 3
                elif event.key == pygame.K_4: return 4
                elif event.key == pygame.K_5: return 5
                elif event.key == pygame.K_6: return 6
                elif event.key == pygame.K_7: return 7
                elif event.key == pygame.K_8: return 8
                elif event.key == pygame.K_9: return 9

def get_system_time():
    return time.time()-_activation_time

def load_screen(filename):
    global screen

    screendump = dos.read_data_file(filename, "sda")
    try:
        pos = 0
        for i in screendump:
            char = min(255,max(0,i[0]))
            fg = min(_SCREEN_COLS-1,max(0,i[1]))
            bg = min(_SCREEN_COLS-1,max(0,i[2]))
            screen[pos] = [char,fg,bg]
            pos += 1
            if pos == _SCREEN_BUFFER_SIZE:
                break
    except:
        raise Exception("Invalid File Format")

def dump_screen(filename):
    dos.write_data_file(screen, filename, "sda")

# This seems buggy, switching back from fullscreen leaves the window partly off-screen
def flip_fullscreen():
    global fullscreen, screen_surface
    fullscreen = not fullscreen

    if fullscreen:
        screen_surface = pygame.display.set_mode((672, 432), pygame.FULLSCREEN)
    else:
        screen_surface = pygame.display.set_mode((672, 432), flags=0)
    draw()
