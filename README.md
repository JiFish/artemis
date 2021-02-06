# Artemis - A Fantasy Microcomputer

Artemis is supposed to be a challenging fantasy computer. Can you create a fun game with the following limitations?

- Using a fairly limited and slow Unstructured BASIC language. (Though improvements to the language may be incoming...)
- 7 text modes to choose from, each a different compromise between number of characters and colors on the screen
- 125 possible colors and 255 redefinable character glyphs
- No graphical modes at all

Although limited, Artemis allows you develop using some modern tools:

- IMPORT programs from a text-file, so you to write your code in your favourite editor
- Integration with [playscii](http://vectorpoem.com/playscii/), a GUI you can design screens in
- Load the character set from a PNG image

![Artemis Screen](https://jifish.github.io/artemis/artemis_screen.gif)

## Downloading and Running

Download the latest release from the [Releases](https://github.com/JiFish/artemis/releases) page.

### Windows

If you select the msi, run the installation and a shortcut will be placed on the desktop.

Otherwise, unzip the download and run `artemis.exe`.

### Other platforms

Install Python 3, then use pip to install the required libraries:
```
pip install pygame midiutil
```

Then to start...
```
python interpreter.py
```

pypresence for discord presence is an optional library. It will be used if present.

## Documentation

The full documentation, including programming reference, is available at https://jifish.github.io/artemis/

## License

Artemis contains a fork of [PyBasic](https://github.com/richpl/PyBasic) by richpl.

Artemis / JiBASIC is available under the GNU General Public License, version 3.0 or later (GPL-3.0-or-later).
