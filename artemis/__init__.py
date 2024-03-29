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

debug = False
fps_flag = False
version = "0.8 beta"

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

# automatically draw after some commands
__AUTO_DRAW = True

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
__CURSOR = ord("_")
__CURSOR_POS = 0
__CURSOR_I_POS = 0
__CURSOR_VISIBLE = False
__INPUT_BUFFER = [[]]
__INPUT_BUFFER_LIMIT = 128

__ICON_CHARACTER = 239

__FULLSCREEN = False

# Screen buffer objects
class ScreenCell():
    def __init__(self, colors, data):
        object.__setattr__(self, 'max_colors', int(colors))
        self.set(data)

    def set(self, data):
        self.character = int(data[0])
        self.foreground = int(data[1])
        self.background = int(data[2])

    def __setattr__(self, name, value):
        if name == 'character':
            if value < 0 or value > 255:
                raise ValueError("Invalid character value, valid values are 0 - 255")
        elif name == 'foreground' or name == 'background':
            if value < 0 or value > self.max_colors:
                raise ValueError("Invalid color value, valid values are 0 - {}".format(self.max_colors))
        else:
            raise AttributeError("ScreenCell has no attribute {}".format(name))
        object.__setattr__(self, name, value)

    def __setitem__(self, index, value):
        if index == 0:
            self.character = value
            return
        if index == 1:
            self.foreground = value
            return
        if index == 2:
            self.background = value
            return
        # Process anything else
        __setattr__(self, index, value)

    def __getitem__(self, index):
        if index == 0:
            return self.character
        if index == 1:
            return self.foreground
        if index == 2:
            return self.background
        raise IndexError("Invalid index, ScreenCells have index 0 - 2")

    def __len__(self):
        return 3

    def __repr__(self):
        return "({},{},{})".format(
            self.character,
            self.foreground,
            self.background
        )

def BuildNewScreen():
    s = []
    for _ in range(__SCREEN_BUFFER_SIZE):
        s.append(ScreenCell(__SCREEN_COLS,(__SPACE, __FOREGROUND_COL, __BACKGROUND_COL)))
    return s

screen = BuildNewScreen()

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
pygame.scrap.init()

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
    __PALLETTE[index] = [int(round(int(r)*63.75)),
                         int(round(int(g)*63.75)),
                         int(round(int(b)*63.75))]

def cls():
    global __CURSOR_POS, screen
    screen.clear()
    screen += BuildNewScreen()
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
    if chr < 0 or chr > 255:
        raise ValueError()
    # Reset character
    if charstring == "":
        __CHR_TILE_TABLE[chr] = __MASTER_CHR_TILE_TABLE[chr].copy()
    # Redfine character
    else:
        charstring = list(charstring.ljust(8*8))
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
    screen[pos].set(cell)

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
    screen[pos].set((__SPACE,  __FOREGROUND_COL, __BACKGROUND_COL))

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
    global screen, __CURSOR_POS, __CURSOR_I_POS

    if __CURSOR_POS < __SCREEN_BUFFER_SIZE: return

    del screen[:__SCREEN_WIDTH]
    screen += [ScreenCell(__SCREEN_COLS,(__SPACE,__FOREGROUND_COL,__BACKGROUND_COL)) for _ in range(__SCREEN_WIDTH)]
    __CURSOR_POS -= __SCREEN_WIDTH
    __CURSOR_I_POS -= __SCREEN_WIDTH

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
    # CURSOR
    if __CURSOR_VISIBLE:
        tile = __CHR_TILE_TABLE[__CURSOR]
        tile.set_palette_at(1, __PALLETTE[screen[__CURSOR_POS][1]])
        tile.set_colorkey(0)
        __TEXT_SURFACE.blit(tile, ((__CURSOR_POS%__SCREEN_WIDTH)*8,
                                   (__CURSOR_POS//__SCREEN_WIDTH)*8))
        tile.set_colorkey(None)

    pygame.transform.scale(__TEXT_SURFACE, [640,400], __TEXT_SCALED_SURFACE)
    __SCREEN_SURFACE.fill(__PALLETTE[__BORDER_COL])
    __SCREEN_SURFACE.blit(__TEXT_SCALED_SURFACE, [16,16])
    pygame.display.flip()

def set_cursor(x, y = None):
    global __CURSOR_POS

    if not isinstance(x, int):
        raise ValueError('Value provided not an integer')

    if y == None:
        if (x < 0 or x >= __SCREEN_BUFFER_SIZE):
            raise ValueError('Position out of range')
        __CURSOR_POS = x

    else:
        if not isinstance(y, int):
            raise ValueError('Value provided not an integer')
        if (x < 0 or x >= __SCREEN_WIDTH):
            raise ValueError('X position out of range')
        if (y < 0 or y >= __SCREEN_HEIGHT):
            raise ValueError('Y position out of range')
        __CURSOR_POS = (y*__SCREEN_WIDTH)+x

def set_cursor_symbol(symbol):
    global __CURSOR

    if not isinstance(symbol, str):
        raise ValueError('Value provided not a string')
    if symbol == "":
        raise ValueError('Value provided is an empty string')
    cursor_ord = ord(symbol[:1])
    if ord > 255:
        raise ValueError('Character out of range')

    __CURSOR = cursor_ord

def get_cursor_x():
    return __CURSOR_POS%__SCREEN_WIDTH

def get_cursor_y():
    return __CURSOR_POS//__SCREEN_WIDTH

def get_cursor():
    return __CURSOR_POS

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

def ui_print(text, do_draw = None):
    global screen, __CURSOR_POS

    if do_draw == None: do_draw = __AUTO_DRAW
    text = str(text)

    for i in [ord(c) for c in text]:
        # Deal with newlines
        if i == 10:
            __CURSOR_POS +=  __SCREEN_WIDTH - (__CURSOR_POS % __SCREEN_WIDTH)
        else:
            screen[__CURSOR_POS].set((i if i <= 255 else 0, __FOREGROUND_COL, __BACKGROUND_COL))
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
    [current_nibble, foreground, background] = get_cell(cellpos)
    # Calculate current_nibble
    current_nibble -= 128
    # Treat all characters outside range as blank
    if current_nibble < 0 or current_nibble > 15:
        current_nibble = 0

    # Calculate new character cell
    out_nibble = (in_nibble | current_nibble)

    # Special case, you are trying to plot using background color
    # flip the foreground and background colors of this cell
    if __FOREGROUND_COL == background and current_nibble > 0:
        out_nibble = ((~current_nibble & 0x0F) | in_nibble)
        set_cell(cellpos, [out_nibble+128, background, foreground])

    # Special case, if every pixel in the cell is filled and we
    # are drawing a pixel of a different color, we can reduce
    # color-clash by changing the background
    elif foreground != __FOREGROUND_COL and out_nibble == 15:
        set_cell(cellpos, [in_nibble+128, __FOREGROUND_COL, foreground])

    else:
        set_cell(cellpos, [out_nibble+128, __FOREGROUND_COL, background])

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

def ui_print_breaking_list(text, prompt = "- PRESS ANY KEY TO CONTINUE -"):
    global __CURSOR_POS

    # Input can be string or list of strings
    if type(text) == list:
        text = list("\n".join(text))
    else:
        text = list(str(text))

    # Format prompt so it is centered
    prompt = prompt[:__SCREEN_WIDTH-1]
    prompt = (" "*((__SCREEN_WIDTH-len(prompt))//2)) + prompt

    # Construct plist
    plist = []
    thisline = ""
    pos = get_cursor_x()
    for c in text:
        # newline by character
        if c == chr(10):
            plist.append(thisline+"\n")
            pos = 0
            thisline = ""
        else:
            thisline += c
            pos += 1
            # newline by length
            if pos == __SCREEN_WIDTH:
                plist.append(thisline)
                pos = 0
                thisline = ""
    # last line
    if pos > 0:
        plist.append(thisline+"\n")

    # Do breaking printing
    line_countdown = __SCREEN_HEIGHT - 1
    for line in plist:
        # Run out of lines, press a key to continue
        if line_countdown < 1:
            ui_print(prompt, do_draw=False)
            ui_input_key()
            # Redraw over message
            set_cursor(0,__SCREEN_HEIGHT-1)
            ui_print(" "*len(prompt), do_draw=False)
            set_cursor(0,__SCREEN_HEIGHT-1)
            line_countdown = __SCREEN_HEIGHT - 1

        # print this line
        ui_print(line, do_draw=False)
        line_countdown -= 1

    draw()
    tick()

def flip_edit_mode():
    global __CURSOR_VISIBLE, __CURSOR_I_POS

    __CURSOR_VISIBLE = not __CURSOR_VISIBLE
    if __CURSOR_VISIBLE:
        __CURSOR_I_POS = __CURSOR_POS
        pygame.key.set_repeat(500,33)
    else:
        __CURSOR_I_POS = 0
        pygame.key.set_repeat(0)

def ui_input(prompt = "", max_len = 0, file_drop = False):
    global screen, __CURSOR_POS, __INPUT_BUFFER

    ui_print(prompt, do_draw=False)
    flip_edit_mode()

    if max_len < 1:
        max_len = __SCREEN_BUFFER_SIZE - __SCREEN_WIDTH
    input_pos = 0
    buffer_pos = len(__INPUT_BUFFER)-1
    last_draw_len = 0
    input = []
    dirty = True
    while True:
        # Redraw
        if dirty:
            __CURSOR_POS = __CURSOR_I_POS
            ui_print("".join(input).ljust(last_draw_len, ' '), do_draw=False)
            __CURSOR_POS = __CURSOR_I_POS + input_pos
            draw()
            last_draw_len = len(input)
            dirty = False

        # Get input
        events = tick()
        for event in events:
            if event.type == pygame.KEYDOWN:
                dirty = True

                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    input_str = "".join(input)
                    # Add non-empty inputs to the buffer
                    if input_str.strip() != "":
                        __INPUT_BUFFER.insert(-1, input)
                        if len(__INPUT_BUFFER) == __INPUT_BUFFER_LIMIT:
                            __INPUT_BUFFER.pop(0)
                    flip_edit_mode()
                    return input_str

                elif event.key == pygame.K_UP and buffer_pos > 0:
                    buffer_pos -= 1
                    input = __INPUT_BUFFER[buffer_pos]
                    input_pos = len(input)

                elif event.key == pygame.K_DOWN and buffer_pos < len(__INPUT_BUFFER)-1:
                    buffer_pos += 1
                    input = __INPUT_BUFFER[buffer_pos]
                    input_pos = len(input)

                elif event.key == pygame.K_LEFT and input_pos > 0:
                    input_pos -= 1

                elif event.key == pygame.K_RIGHT and input_pos < len(input):
                    input_pos += 1

                elif event.key == pygame.K_BACKSPACE and input_pos > 0:
                    input_pos -= 1
                    input.pop(input_pos)

                elif event.key == pygame.K_DELETE and len(input) > 0 and input_pos < len(input):
                    input.pop(input_pos)

                elif event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    clip = pygame.scrap.get("text/plain;charset=utf-8")
                    if not clip: clip = pygame.scrap.get(pygame.SCRAP_TEXT)
                    if clip:
                        clip = list(clip.decode('charmap'))
                        clip = list(filter(lambda c: ord(c) >= 32, clip))
                        if len(clip)+len(input) <= max_len:
                            input = input[:input_pos]+clip+input[input_pos:]
                            input_pos += len(clip)

                elif event.unicode != '' and ord(event.unicode) >= 32 and ord(event.unicode) < 255 \
                     and len(input) < max_len:
                    input = input[:input_pos] + [event.unicode] + input[input_pos:]
                    input_pos += 1

                else:
                    dirty = False

            # Drag and drop file
            elif file_drop and event.type == pygame.DROPFILE:
                extension = os.path.basename(event.file)
                extension = os.path.splitext(extension)[-1].lower()

                # Detected Artemis Disk Image (ADI)
                if extension in ['.adi', '.zip']:
                    flip_edit_mode()
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
        if 'mode' in screendump:
            set_mode(screendump['mode'])

        # INK, presence of ink in a dump is optional
        if 'ink' in screendump:
            for i, cols in enumerate(screendump['ink'][:__SCREEN_COLS]):
                set_palette(i, *cols)

        # BORDER, also optional
        if 'border' in screendump:
            set_border(screendump['border'])

        if 'data' in screendump:
            pos = 0
            for i in screendump['data']:
                if i != None:
                    char = min(255,max(0,i[0]))
                    fg = min(__SCREEN_COLS-1,max(0,i[1]))
                    bg = min(__SCREEN_COLS-1,max(0,i[2]))
                    screen[pos].set((char,fg,bg))
                pos += 1
                if pos == __SCREEN_BUFFER_SIZE:
                    break
    except:
        raise Exception("Invalid File Format")

def get_screen_dump():
    # v is format version number
    return {'v': 1, 'mode': __SCREEN_MODE,
            'ink': [rgb_to_ink(i) for i in __PALLETTE],
            'border': __BORDER_COL, 'data': screen}

def dump_screen(filename = None):
    if filename == None:
        filename = time.strftime("%y%m%d%H%M%S")
    dos.write_data_file(get_screen_dump(), filename, "sda")

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
