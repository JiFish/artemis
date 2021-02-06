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
import textwrap
from artemis import dos
from artemis import tass

__activation_time = time.time()

debug = False
fps_flag = False
version = "0.7 beta"

# automatically draw after some commands
__AUTO_DRAW = True

__CURSOR = ord("_")
__SPACE = ord(" ")

__SCREEN_WIDTH = 40
__SCREEN_HEIGHT = 25
__SCREEN_BUFFER_SIZE = __SCREEN_WIDTH*__SCREEN_HEIGHT
__SCREEN_COLS = 8
__SCREEN_MODE = 1

with open(os.path.dirname(os.path.realpath(__file__))+'/pallette.json') as pallette_file:
    __MASTER_PALLETTE = json.load(pallette_file)

__PALLETTE = __MASTER_PALLETTE[:__SCREEN_COLS]

__FOREGROUND_COL = 1;
__BACKGROUND_COL = 0;
__BORDER_COL = 0;
# Screen buffer, a tuplet for each cell
screen = [[__SPACE,__FOREGROUND_COL,__BACKGROUND_COL] for _ in range(__SCREEN_BUFFER_SIZE)]
__CURSOR_POS = 0

__ICON_CHARACTER = 239

__FULLSCREEN = False

def __load_tile_table(filename, width = 8, height = 8):
    image = pygame.image.load(filename)
    image_size = (128, 128)

    # Check image size
    if image.get_size() != image_size:
        raise Exception("Character set image is not 128x128")

    # Convert the surface to a mask and back
    # This ensures we get a nice 1-bit image
    # no matter the input
    image.set_colorkey([0,0,0])
    mask = pygame.mask.from_surface(image)
    image = pygame.Surface(size=image_size, depth=8)
    image.set_palette([[0,0,0],[255,255,255]])
    image = mask.to_surface(image)
    del mask

    # Chop image to tile table
    tile_table = []
    for tile_y in range(0, 16):
        for tile_x in range(0, 16):
            rect = (tile_x*width, tile_y*height, width, height)
            tile_table.append(image.subsurface(rect))

    return tile_table

def set_icon():
    __CHR_TILE_TABLE[__ICON_CHARACTER].set_palette_at(0, [0, 0, 0])
    __CHR_TILE_TABLE[__ICON_CHARACTER].set_palette_at(1, [255, 255, 255])
    pygame.display.set_icon(pygame.transform.scale(__CHR_TILE_TABLE[__ICON_CHARACTER], (64, 64)))

# Some pygame initalisation
# TODO: Variable sized window?
pygame.display.set_caption("Artemis Fantasy Microcomputer")
pygame.display.set_icon(pygame.Surface((0,0)))
pygame.mouse.set_visible(False)
pygame.init()
__SCREEN_SURFACE = pygame.display.set_mode((672, 432))
__TEXT_SURFACE = pygame.Surface((__SCREEN_WIDTH*8, __SCREEN_HEIGHT*8))
__TEXT_SURFACE.fill((0, 0, 0))
__TEXT_SCALED_SURFACE = pygame.Surface((640, 400))
__CHR_TILE_TABLE = __load_tile_table(os.path.dirname(os.path.realpath(__file__))+"/charset.png")
set_icon()
__MASTER_CHR_TILE_TABLE = [chr.copy() for chr in __CHR_TILE_TABLE]

__MASTER_CHR_TILE_TABLE = __load_tile_table(os.path.dirname(os.path.realpath(__file__))+"/charset.png", 8, 8)
__CLOCK = pygame.time.Clock()

# Maximum instructions before forcing a tick
__MAX_INSTRUCTIONS = 10000
__INSTRUCTIONS_COUNT = 0

def ins_tick():
    global __INSTRUCTIONS_COUNT
    __INSTRUCTIONS_COUNT += 1
    if __INSTRUCTIONS_COUNT > __MAX_INSTRUCTIONS:
        tick()
        if debug: print("Forced tick after "+str(__MAX_INSTRUCTIONS)+" instructions")

def set_palette(index, r, g, b):
    for i in [r,b,g]:
        if i < 0 or i > 4:
            raise ValueError("Invalid RGB value")
    if index < 0 or index > 15:
        raise ValueError("Invalid palette index")
    __PALLETTE[index] = [int(round(r*63.75)),
                         int(round(g*63.75)),
                         int(round(b*63.75))]

def cls():
    global screen, __FOREGROUND_COL, __BACKGROUND_COL, __CURSOR_POS
    screen = [[__SPACE,__FOREGROUND_COL,__BACKGROUND_COL] for _ in range(__SCREEN_BUFFER_SIZE)]
    __CURSOR_POS = 0

    if __AUTO_DRAW:
        draw()
        tick()

def set_mode(mode):
    global __SCREEN_WIDTH, __SCREEN_HEIGHT, __SCREEN_COLS, __SCREEN_BUFFER_SIZE
    global __TEXT_SURFACE, __BACKGROUND_COL, __FOREGROUND_COL, __BORDER_COL, __PALLETTE
    global __SCREEN_MODE

    if mode == __SCREEN_MODE:
        return  # Nothing to do

    if mode < 0 or mode > 6:
        raise ValueError("Invalid Mode")

    __SCREEN_MODE = mode

    if mode == 0:
        __SCREEN_WIDTH = 20
        __SCREEN_HEIGHT = 25
        __SCREEN_COLS = 32
    elif mode == 1:
        __SCREEN_WIDTH = 40
        __SCREEN_HEIGHT = 25
        __SCREEN_COLS = 8
    elif mode == 2:
        __SCREEN_WIDTH = 80
        __SCREEN_HEIGHT = 25
        __SCREEN_COLS = 4
    elif mode == 3:
        __SCREEN_WIDTH = 80
        __SCREEN_HEIGHT = 50
        __SCREEN_COLS = 2
    elif mode == 4:
        __SCREEN_WIDTH = 40
        __SCREEN_HEIGHT = 50
        __SCREEN_COLS = 4
    elif mode == 5:
        __SCREEN_WIDTH = 24
        __SCREEN_HEIGHT = 15
        __SCREEN_COLS = 32
    elif mode == 6:
        __SCREEN_WIDTH = 16
        __SCREEN_HEIGHT = 10
        __SCREEN_COLS = 125
    else:
        raise ValueError("Invalid Mode")

    # Set buffer size and recreate text surface
    __SCREEN_BUFFER_SIZE = __SCREEN_WIDTH*__SCREEN_HEIGHT
    __TEXT_SURFACE = pygame.Surface((__SCREEN_WIDTH*8, __SCREEN_HEIGHT*8))

    # Reducing colours
    if len(__PALLETTE) > __SCREEN_COLS:
        # Cut the pallete down to the new max colours
        __PALLETTE = __PALLETTE[:__SCREEN_COLS]
        __FOREGROUND_COL = min(__FOREGROUND_COL,__SCREEN_COLS-1)
        if __BACKGROUND_COL >= __SCREEN_COLS: __BACKGROUND_COL = 0
        if __BORDER_COL >= __SCREEN_COLS: __BORDER_COL = 0
    # Increasing colours
    elif len(__PALLETTE) < __SCREEN_COLS:
        # Pad the pallete with the master pallete to reach the new max colours
        __PALLETTE = __PALLETTE+__MASTER_PALLETTE[len(__PALLETTE):__SCREEN_COLS]

    # Clear the existing screen contents
    cls()

def set_caption(caption):
    pygame.display.set_caption(caption)

def redefine_char(chr, charstring):
    global __CHR_TILE_TABLE
    # Reset character
    if charstring == "":
        __CHR_TILE_TABLE[chr] = __MASTER_CHR_TILE_TABLE[chr].copy()
    # Redfine character
    else:
        charstring = list(charstring.ljust(8*8))
        if chr < 0 or chr > 255:
            raise ValueError()
        for i in range(8*8):
            pix = 0 if charstring[i] == ' ' else 1
            __CHR_TILE_TABLE[chr].set_at((i % 8, i // 8), pix)
    # Special case for char 239
    if chr == __ICON_CHARACTER:
        set_icon()

def redefine_char_from_int_list(chr, intlist):
    charstring = ""
    for i in intlist:
        i = max(0,min(255,i))
        for j in list(bin(i)[2:].zfill(8)):
            charstring += "X" if j == "1" else " "
    redefine_char(chr, charstring)

def get_cell(pos):
    if pos < 0 or pos >= __SCREEN_BUFFER_SIZE:
        raise IndexError()
    return screen[pos]

def set_cell(pos, cell):
    if pos < 0 or pos >= __SCREEN_BUFFER_SIZE:
        raise IndexError()
    screen[pos] = cell

def manipulate_cell(pos, key, val):
    global screen
    if pos < 0 or pos >= __SCREEN_BUFFER_SIZE or key < 0 or key > 2:
        raise ValueError("Cell position out of range")
    if key == 0 and (val < 0 or val > 255):
        raise ValueError("Value out of range")
    if key > 0 and (val < 0 or val >= __SCREEN_COLS):
        raise ValueError("Value out of range")

    screen[pos][key] = val

def clear_cell(pos):
    if pos < 0 or pos >= __SCREEN_BUFFER_SIZE:
        raise IndexError()
    screen[pos] = [__SPACE,  __FOREGROUND_COL, __BACKGROUND_COL]

def set_border(col):
    global __BORDER_COL
    __BORDER_COL = col;
    if __AUTO_DRAW:
        draw()
        tick()

def tick():
    global __INSTRUCTIONS_COUNT
    __INSTRUCTIONS_COUNT = 0

    if fps_flag:
        print ("{:.2f} fps   ".format(__CLOCK.get_fps()), end='\r')

    __CLOCK.tick(30)

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
            elif event.key == pygame.K_F12:
                dump_screen()

    return events

def wait(secs = 1):
    if __AUTO_DRAW:
        draw()
    secs = max(1,int(secs*1000))
    while secs > 0:
        events = tick()
        secs -= __CLOCK.get_time()

def scroll_screen():
    global screen, __CURSOR_POS

    while __CURSOR_POS < __SCREEN_BUFFER_SIZE: return

    screen = screen[__SCREEN_WIDTH:]
    screen += [[__SPACE,__FOREGROUND_COL,__BACKGROUND_COL] for _ in range(__SCREEN_WIDTH)]
    __CURSOR_POS -= __SCREEN_WIDTH

def draw():
    global __AUTO_DRAW
    # Switch auto_draw back on if it has been disabled
    if not __AUTO_DRAW: __AUTO_DRAW = True
    xpos = 0
    ypos = 0
    for x in screen:
        char, foreground, background = x
        tile = __CHR_TILE_TABLE[char]
        tile.set_palette_at(0, __PALLETTE[background])
        tile.set_palette_at(1, __PALLETTE[foreground])
        __TEXT_SURFACE.blit(tile, (xpos*8, ypos*8))
        if debug:
            pygame.draw.rect(__TEXT_SURFACE,[255,0,0],[xpos*8,ypos*8,(xpos*8)+9,(ypos*8)+9],1)
        xpos = xpos + 1
        if (xpos == __SCREEN_WIDTH):
            xpos = 0
            ypos = ypos + 1
            if ypos == __SCREEN_HEIGHT:
                break
    pygame.transform.scale(__TEXT_SURFACE, [640,400], __TEXT_SCALED_SURFACE)
    __SCREEN_SURFACE.fill(__PALLETTE[__BORDER_COL])
    __SCREEN_SURFACE.blit(__TEXT_SCALED_SURFACE, [16,16])
    pygame.display.flip()

def set_cursor(x, y):
    global __CURSOR_POS

    if not isinstance(x, int) or not isinstance(y, int):
        raise ValueError('Value provided not a number')
    if (x < 0 or x >= __SCREEN_WIDTH):
        raise ValueError('X position out of range')
    if (y < 0 or y >= __SCREEN_HEIGHT):
        raise ValueError('Y position out of range')

    __CURSOR_POS = (y*__SCREEN_WIDTH)+x

def set_color(f, b = -1):
    global __FOREGROUND_COL, __BACKGROUND_COL
    if f >= __SCREEN_COLS or b >= __SCREEN_COLS:
        raise ValueError("Invalid color")
    if (f > -1): __FOREGROUND_COL = f
    if (b > -1): __BACKGROUND_COL = b

def set_color_safe(f, b = -1):
    if f >= __SCREEN_COLS: f = -1
    if b >= __SCREEN_COLS: b = -1
    set_color(f, b)

def ui_print(text, do_draw = None, pos = None):
    global screen, __CURSOR_POS

    if do_draw == None: do_draw = __AUTO_DRAW
    text = str(text)

    for i in list(text):
        # Deal with newlines
        if i == "\n":
            __CURSOR_POS +=  __SCREEN_WIDTH - (__CURSOR_POS % __SCREEN_WIDTH)
        else:
            screen[__CURSOR_POS] = [ord(i), __FOREGROUND_COL, __BACKGROUND_COL]
            __CURSOR_POS += 1
        scroll_screen()

    if do_draw:
        draw()
        tick()

def ui_psuedo_plot(x, y):
    # Round to int values
    x = round(x)
    y = round(y)

    # Invalid plot position, fail silently
    if x >= __SCREEN_WIDTH*2 or x < 0 or y >= __SCREEN_HEIGHT*2 or y < 0:
        return

    # Work out in_nibble
    in_nibble = 2**(((y%2)*2)+x%2)

    # Fetch current cell
    cellpos = x//2 + ((y//2)*__SCREEN_WIDTH)
    [current_nibble, _, background] = get_cell(cellpos)
    # Calculate current_nibble
    current_nibble -= 128
    # Treat all characters outside range as blank
    if current_nibble < 0 or current_nibble > 15:
        current_nibble = 0

    # Calculate and set new character cell
    out_nibble = (in_nibble | current_nibble)+128
    set_cell(cellpos, [out_nibble, __FOREGROUND_COL, background])

    if __AUTO_DRAW:
        draw()
        tick()


def ui_print_window(text, x1, y1, x2, y2, wrap = True):
    if y2 < y1 or x2 < y1 or x1 < 0 or x2 >= __SCREEN_WIDTH or y1 < 0 or y2 >= __SCREEN_HEIGHT:
        raise ValueError("Invalid window position")

    max_width = x2 - x1 + 1
    max_height = y2 - y1 + 1
    text = text.splitlines()

    pieces = []
    if wrap:
        for p in text:
            wrapped_p = textwrap.wrap(p, width=max_width, replace_whitespace=False)
            # Detect zero length returns, so we don't lose empty lines
            if len(wrapped_p) == 0: pieces.append("")
            else: pieces += wrapped_p
    else:
        for p in text:
            pieces += [p[i:i+max_width] for i in range(0, len(p), max_width)]
    # Pad the pieces to fill the window
    pieces += [' '*max_width] * (max_height - len(pieces))
    for i in range(y1,y2+1):
        set_cursor(x1,i)
        ui_print(pieces.pop(0).ljust(max_width," "), do_draw=False)

    if __AUTO_DRAW:
        draw()
        tick()

def ui_print_breaking_list(plist):
    global __AUTO_DRAW
    line_row = 0
    # Blank link at end
    plist.append("")
    pak_str = "- PRESS ANY KEY TO CONTINUE -"[:__SCREEN_WIDTH-1]
    pak_str = (" "*((__SCREEN_WIDTH-len(pak_str))//2)) + pak_str
    # Loop the list,
    # pausing when we reach the height of the screen
    for line in plist:
        lines_in_row = max(1,-(-len(line)//__SCREEN_WIDTH))
        line_row += lines_in_row
        if line_row >= __SCREEN_HEIGHT:
            ui_print(pak_str, do_draw=False)
            ui_input_key()
            set_cursor(0,__SCREEN_HEIGHT-1)
            ui_print(" "*len(pak_str), do_draw=False)
            set_cursor(0,__SCREEN_HEIGHT-1)
            line_row = lines_in_row
        # Special case, where the line is exactly divisible by
        # the screen width, no newline is needed unless the
        # line is empty
        if line == "" or len(line) % 40 != 0:
            line += "\n"
        ui_print(line, do_draw=False)
    draw()
    tick()

def ui_input(prompt = "", max_len = 0, file_drop = False):
    global screen, __CURSOR_POS, __FOREGROUND_COL, __BACKGROUND_COL
    ui_print(prompt + chr(__CURSOR), do_draw=False)
    __CURSOR_POS -= 1
    if max_len < 1:
        max_len = __SCREEN_BUFFER_SIZE - __SCREEN_WIDTH
    input = ''
    draw()
    pygame.key.set_repeat(500,33)
    while True:
        events = tick()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    clear_cell(__CURSOR_POS)
                    pygame.key.set_repeat(0)
                    return input
                elif event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                    if (input != ''):
                        clear_cell(__CURSOR_POS)
                        __CURSOR_POS -= 1
                        screen[__CURSOR_POS] = [__CURSOR, __FOREGROUND_COL, __BACKGROUND_COL]
                        input = input[:-1]
                        draw()
                elif event.unicode != '' and ord(event.unicode) < 255 and event.unicode != "\n" and len(input) < max_len:
                    screen[__CURSOR_POS] = [ord(event.unicode), __FOREGROUND_COL, __BACKGROUND_COL]
                    __CURSOR_POS += 1
                    scroll_screen()
                    screen[__CURSOR_POS] = [__CURSOR, __FOREGROUND_COL, __BACKGROUND_COL]
                    input = input + event.unicode
                    draw()
            # Drag and drop .bas file
            elif file_drop and event.type == pygame.DROPFILE:
                extension = os.path.basename(event.file)
                extension = os.path.splitext(extension)[-1].lower()
                # Detected BASIC text file (BAS)
                if extension == '.bas':
                    clear_cell(__CURSOR_POS)
                    pygame.key.set_repeat(0)
                    return 'IMPORT "{}"'.format(event.file)
                # Detected Artemis Disk Image (ADI)
                elif extension in ['.adi', '.zip']:
                    clear_cell(__CURSOR_POS)
                    pygame.key.set_repeat(0)
                    return 'DSKIMPORT "{}"'.format(event.file)

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

def ui_are_you_sure(msg = "Are you sure? (Y/N)"):
    ui_print(msg)
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

def easter_egg():
    with open(os.path.dirname(os.path.realpath(__file__))+'/easter.sda') as easter_file:
        ee = json.load(easter_file)
    load_screen(ee)

def load_screen(screendump):
    global screen

    try:
        # Screen Mode
        set_mode(screendump['mode'])

        # INK, presence of ink in a dump is optional
        if 'ink' in screendump:
            for i, cols in enumerate(screendump['ink'][:__SCREEN_COLS]):
                set_palette(i, *cols)

        # BORDER, also optional
        if 'border' in screendump:
            set_border(screendump['border'])

        pos = 0
        for i in screendump['data']:
            if i != None:
                char = min(255,max(0,i[0]))
                fg = min(__SCREEN_COLS-1,max(0,i[1]))
                bg = min(__SCREEN_COLS-1,max(0,i[2]))
                screen[pos] = [char,fg,bg]
            pos += 1
            if pos == __SCREEN_BUFFER_SIZE:
                break
    except:
        raise Exception("Invalid File Format")

def dump_screen(filename = None):
    if filename == None:
        filename = time.strftime("%y%m%d%H%M%S")
    # v is format version number
    data = {'v': 1, 'mode': __SCREEN_MODE,
            'ink': [rgb_to_ink(i) for i in __PALLETTE],
            'border': __BORDER_COL, 'data': screen}
    dos.write_data_file(data, filename, "sda")

def rgb_to_ink(rgb):
    return [
        round(rgb[0]/63.75),
        round(rgb[1]/63.75),
        round(rgb[2]/63.75),
    ]

def load_charset(filename):
    global __CHR_TILE_TABLE
    dos.test_filename(filename)
    if not os.path.isfile(filename):
        raise OSError("File not found")
    try:
        __CHR_TILE_TABLE = __load_tile_table(filename)
        set_icon()
    except:
        raise Exception("Invalid character set image")

def flip_fullscreen():
    global __FULLSCREEN, __SCREEN_SURFACE
    __FULLSCREEN = not __FULLSCREEN

    if __FULLSCREEN:
        # Setting the display to SCALED allows
        # us toggle fullscreen at this resolution
        __SCREEN_SURFACE = pygame.display.set_mode((672, 432), pygame.SCALED)
        pygame.display.toggle_fullscreen()
    else:
        pygame.display.toggle_fullscreen()
        __SCREEN_SURFACE = pygame.display.set_mode((672, 432))
    draw()

def disable_auto_draw():
    global __AUTO_DRAW
    __AUTO_DRAW = False

def reset_screen():
    global __PALLETTE, __CHR_TILE_TABLE

    set_mode(1)
    set_border(0)
    set_color(1, 0)
    # Reset pallete
    for i in range(__SCREEN_COLS-1):
        __PALLETTE[i] = __MASTER_PALLETTE[i]
    # Reset tile table
    __CHR_TILE_TABLE = [chr.copy() for chr in __MASTER_CHR_TILE_TABLE]
    set_icon()
