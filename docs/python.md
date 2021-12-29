# Artemis and Python

You can write your programs for Artemis using the python language. This is an easier and more modern way to develop your program.

This documentation is not intended to be a python tutorial. Instead it will instruct those who are already familiar with python on what features are available.

## Builtins

Most of the standard builtins are provided with a few differences:

### import

Is not available due to sandboxing. The `math` and `random` modules have already been imported for you.

### open()

The `file` parameter must conform to artemis' filename standard, or an exception will be thrown. This means you can only open files on the currently mounted artemis 'disk', no subdirectories. Filenames are limited to alphanumeric characters, and a single optional extension after a period ".".

- `abc123` - valid
- `abc123.ext` - valid
- `abc_123` - **invalid**
- `foo/abc123` - **invalid**
- `abc123.ext.ext` - **invalid**
- `c:\\abc123.ext` - **invalid**

### print()

The `file` parameter is ignored. Print will always output to artemis' screen

### quit() and exit()

Are not available.

## Artemis functions

The following additional functions are available to help you control Artemis.

- **key**(impatient=False) - Waits for a key to be pressed and returns the keycode. If _impatient_ is `True`, the function will give up waiting after 1 tick and return -1.
- **system_time**() - Return the time the system has been active in seconds. This value includes fractions of a second.
- **wait**(secs) - Pauses execution for *secs* seconds. *secs* can include a decimal point to allow sub-second waiting. Note: this command is not particularly accurate and you should expect the actual wait time to be +/-0.04 seconds at the least.

## Screen module

Screen functions are accessed via `screen`, e.g. `screen.cls()`.

- **border**(col) - Set the screen's border color to palette entry *col*.
- **cls**() - Clear the screen
- **color**(f, b=-1) - Sets the text color to *f* and optionally the background color to *b*. If negative values are given, the current color is maintained.
- **cursor**(x, y) - Move the cursor to position *x*, *y*.
- **cursor_symbol**(symbol) - Set the character used as the cursor to *symbol*. *symbol* is expected to be one character long string.
- **cursor_x**() - Returns the cursor's X position
- **cursor_y**() - Returns the cursor's Y position
- **dumps**() - Returns a dictionary representing the current state of the screen, including mode, ink, border and previously printed characters.
- **ink**(index, r, g, b) - Change the pallete at _index_. _r_, _g_ and _b_ can be integers from 0 - 4, giving 125 possible colors.
- **loads**(screendump) - Load screen data from dictionary *screendump* in to the screen. This data is in the same format as created by the **dumps** function. The screen mode, ink and border color is changed if needed. The change won't be visible until the screen is next drawn.
- **mode**(mode) - Change the screen mode to _mode_.

Available modes:

Mode | Characters | Colors | Pixel shape | Notes
-----|------------|--------|-------------|------
0    | 20 x 25    | 32     | 2 x 1       |
1    | 40 x 25    | 8      | 1 x 1       | Default
2    | 80 x 25    | 4      | 1 x 2       |
3    | 80 x 50    | 2      | 1 x 1       |
4    | 40 x 50    | 4      | 2 x 1       |
5    | 24 x 15    | 32     | 1 x 1       |
6    | 16 x 10    | 125    | 1 x 1       |

- **plot**(x, y) - Draws a psuedo-pixel using the current text color in position *x*, *y*. Treats each screen text-cell as 4 pixels giving a psuedo-pixel mode with dimensions twice that of the text mode. (e.g. 80 x 50 pixels in the default mode 1.) _(Note: A limitation of this is PLOT can also change the color of existing pixels within the same text-cell. This phenomenon is known as "Color Clash.")_
- **printb**(text, prompt = "- PRESS ANY KEY TO CONTINUE -") - This is a convenience function for printing large amounts of text. *text* is printed until the screen has been filled. The user will then be prompted to "PRESS ANY KEY TO CONTINUE", after which *text* resumes printing. This process repeats until *text* has been fully printed. If *prompt* is provided, it will replace the default prompt.
- **printw**(text, x1, y1, x2, y2, wrap=True) - Print text *text* to a virtual "Window" on-screen. The window's top-left position is defined by *x1* and *y1*, and it's bottom-right by *x2* and *y2*. If *wrap* is `True`, *text* will be wrapped cleanly - avoiding line-breaks in the middle of words. (This is the default behaviour.) If *text* is too long, it will be cropped, if it is too short it will be padded with spaces.
- **refresh**() - Force the screen to draw.
- **refresh_wait**() - Prevent functions like **print**, **border**, **cls** etc. from drawing the screen automatically. You can resume drawing by calling **refresh**.
- **rsts**() - Reset the screen parameters. Mode is set to 1, colors, ink and symbols are all set to the default.
- **symbol**(chr, charstring) - Redefine the bitmap of the character with the code *chr*. *charstring* is a string that represents the new bitmap. Each character in the string represents one pixel starting at the top-left. Use a space for the background and any other character for the foreground. If *y$* is an empty string, the character will be reset to the default.
- **symbol_image**(filename) - Load a complete set of characters from image with filename specified by *filename*. This image should be 128 x 128 pixels, with each 8x8 cell containing a character. Black is treated as the background and any other color as foreground. The file should be placed in a disk directory and using a artemis-friendly filename. A number of image types are supported, but a PNG is recommended.

### Direct screen access

Direct access to the screen cells is provided via the `screen.screen` object, which contains a ScreenCell object for each cell. You can access cells with their Index, which starts with 0 at the top left of the screen. The total number of cells is determined by the current screen mode. `screen.screen` can be iterated.

Don't hold on to the returned ScreenCell objects as they may become stale.

#### ScreenCell Objects

Each ScreenCell contains the character, foreground and background colors for that cell.

**Attributes**
- **character** - Get the character code, or assign this to change it. (Valid values int 0 - 255)
- **foreground** - Get the foreground color of the cell, or assign this to change it. (Valid values int 0 - [totalcolors-1])
- **background** - Get the background color of the cell, or assign this to change it. (Valid values int 0 - [totalcolors-1])
- **set**(cell) - Function to set all 3 values at once. _cell_ is expected to be a length 3 tuple, or other indexable value.
**Indexes**
You can also set or get the cell values using indexes. This means you can unpack the values e.g. `[char, fore, back] = thisCell`.
- **0** - Character Code
- **1** - Foreground
- **2** - Background

Finally, if you attempt to set a `screen.screen` index directly, instead the value will be passed in to the ScreenCell's **set** function. See the example below.

```
# Four ways to set a ScreenCell
scr = screen.screen

# Using Attributes
scr[0].character = 65
scr[0].foreground = 1
scr[0].background = 0

# Using Indexes
scr[0][0] = 65
scr[0][1] = 1
scr[0][2] = 0

# Using set function
scr[0].set((65, 1, 0))

# Directly assigning to screen
scr[0] = (65, 1, 0)
```

```
# Iterate the screen and count cells with background color 0
count = 0
for cell in screen.screen:
    if cell.background == 0:
        count += 1
print("{} cells had background 0".format(count))
```

```
# Move all the screen cells forward one place
scr = screen.screen
for i in range(len(scr)-1,0,-1):
    scr[i].set(scr[i-1])
```

## Sound module

Sound functions are accessed via `sound`. e.g. `sound.stop()`

- **play**(notestr, mode) - Play some music.
    - *notestr* a string representing the music to play. This is a subset of MML format.
    - *mode* the play mode. *0*: Music will play in the background. *1*: Execution will halt until music playback is complete. *2*: As 0, but the music loops until **stop** is called.
- **stop**() - Stop any currently playing music.
