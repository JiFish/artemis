# Artemis - A Fantasy Microcomputer

Artemis is supposed to be a challenging fantasy computer. Can you create a fun game with the following limitations?

- 7 text modes to choose from, each a different compromise between number of characters and colors on the screen
- 125 possible colors and 255 redefinable character glyphs
- No bitmap modes or sprites
- Using an Unstructured BASIC language (or Python if you prefer.)

Although limited, Artemis allows you develop using some modern tools:

- Integration with [playscii](http://vectorpoem.com/playscii/), a GUI you can design screens in.
- Loading of the character set from a PNG image.
- Importing BASIC programs and Python scripts from text-files. (Allowing development in your favourite editor.)

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
python run.py
```

pypresence for discord presence is an optional library. It will be used if present.

## Documentation

The full documentation, including programming reference, is available at https://jifish.github.io/artemis/

## Powered by

Thank you to the following open source projects:

- [PyBasic](https://github.com/richpl/PyBasic) by richpl
- [pygame2](https://www.pygame.org/)
- [MIDIUtil](https://github.com/MarkCWirt/MIDIUtil) by MarkCWirt
- [python](https://www.python.org/)

## License

Artemis contains a fork of [PyBasic](https://github.com/richpl/PyBasic) by richpl.

Artemis / JiBASIC is available under the GNU General Public License, version 3.0 or later (GPL-3.0-or-later).
