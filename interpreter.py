#! /usr/bin/python

# SPDX-License-Identifier: GPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""This class implements a BASIC interpreter that
presents a prompt to the user. The user may input
program statements, list them and run the program.
The program may also be saved to disk and loaded
again.

"""

from basictoken import BASICToken as Token
from lexer import Lexer
from program import Program
from sys import stderr
import artemis
import os, io, webbrowser
from datetime import date

dos = artemis.dos

_help_url = "https://github.com/JiFish/artemis#the-main-interface"

# Discord Presence. Fails gracefully if module does not exist
try:
    from pypresence import Presence
    RPC = Presence('792576960923828255')
    RPC.connect()
    RPC.update(state="On the CLI", large_image="artemis_icon")
except ImportError:
    RPC = None

def main():
    artemis.set_caption("Artemis Fantasy Microcomputer")
    artemis.set_color(6)
    artemis.ui_print("Artemis Fantasy Microcomputer {}{}\n\n".format(chr(176), date.today().year), do_draw=False)
    artemis.ui_print(" JiBASIC {}\n\n".format(artemis.version), do_draw=False)
    artemis.set_color(1)
    artemis.ui_print("Type HELP to open documentation.\n\n", do_draw=False)
    artemis.ui_print("READY\n", do_draw=False)
    for i in range(0,8):
        artemis.screen[111+i] = [214,(i+1)%8,i]

    lexer = Lexer()
    program = Program()

    # Continuously accept user input and act on it until
    # the user enters 'EXIT'
    while True:

        try:
            stmt = artemis.ui_input('>', file_drop = True)

        except KeyboardInterrupt:
            break

        artemis.ui_print("\n")

        try:
            tokenlist = lexer.tokenize(stmt)

            # Execute commands directly, otherwise
            # add program statements to the stored
            # BASIC program

            if len(tokenlist) > 0:

                # Exit the interpreter
                if tokenlist[0].category == Token.EXIT:
                    break

                # Add a new program statement, beginning
                # a line number
                elif tokenlist[0].category == Token.UNSIGNEDINT\
                     and len(tokenlist) > 1:
                    program.add_stmt(tokenlist)

                # Delete a statement from the program
                elif tokenlist[0].category == Token.UNSIGNEDINT \
                        and len(tokenlist) == 1:
                    program.delete_statement(int(tokenlist[0].lexeme))

                # Execute the program
                elif tokenlist[0].category == Token.RUN:
                    if RPC: RPC.update(state="Running a program", large_image="artemis_icon")
                    try:
                        program.execute()

                    except KeyboardInterrupt:
                        artemis.ui_print("\nProgram terminated\n")

                    finally:
                        if RPC: RPC.update(state="On the CLI", large_image="artemis_icon")

                # List commands
                elif tokenlist[0].category == Token.LIST:
                    try:
                        type = tokenlist[1].lexeme[0].upper()
                        assert type in ['P','F','D']
                    except:
                        type = 'P'

                    if type == 'F':     # List files on the disk
                        list = dos.list_disk()
                    elif type == 'D':   # List all disks
                        list = dos.list_all_disks()
                    else:               # List Program
                        list = program.list().splitlines()

                    artemis.ui_print_breaking_list(list)

                # Export the program to disk
                elif tokenlist[0].category == Token.EXPORT:
                    # Use home dir as default instead of current disk
                    dos.chdir_home()
                    try:
                        if len(tokenlist) == 1: raise ValueError("EXPORT command missing input")
                        fn = tokenlist[1].lexeme
                        if '.' not in fn: fn += ".bas"
                        fn = os.path.realpath(fn)
                        with open(fn, 'w') as outfile:
                            outfile.write(program.list())
                        artemis.ui_print('Program exported to "{}"\n'.format(fn))
                    finally:    # Make sure we set the default location back
                        dos.chdir_disk()

                # Load the program from disk
                # Save the program to disk
                elif tokenlist[0].category == Token.SAVE:
                    if len(tokenlist) == 1: raise ValueError("SAVE command missing input")
                    program.save(tokenlist[1].lexeme)
                    artemis.ui_print("Program written to file\n")

                # Load the program from disk
                elif tokenlist[0].category == Token.LOAD:
                    if len(tokenlist) == 1: raise ValueError("LOAD command missing input")
                    program.load(tokenlist[1].lexeme)
                    artemis.ui_print("Program read from file\n")

                # Load the program from disk
                elif tokenlist[0].category == Token.IMPORT:
                    if len(tokenlist) == 1: raise ValueError("IMPORT command missing input")
                    # Use home dir as default instead of current disk
                    dos.chdir_home()
                    try:
                        with open(tokenlist[1].lexeme, 'r') as infile:
                            lines = infile.readlines()
                            infile.close()
                        program.delete()
                        for line in lines:
                            line = line.strip()
                            if line == "": continue
                            artemis.ui_print(line+"\n")
                            program.add_stmt(lexer.tokenize(line))
                        artemis.ui_print("\nProgram imported from file\n")

                    except OSError:
                        raise OSError("File not found")

                    finally:    # Make sure we set the default location back
                        dos.chdir_disk()

                # Delete the program from memory
                elif tokenlist[0].category == Token.NEW:
                    program.delete()

                # Clear the screen
                elif tokenlist[0].category == Token.CLS:
                    artemis.cls()

                # Mount a new or existing disk
                elif tokenlist[0].category == Token.MOUNT:
                    if len(tokenlist) == 1: raise ValueError("MOUNT command missing input")
                    diskname = tokenlist[1].lexeme

                    if not dos.disk_exists(diskname):
                        if not artemis.ui_are_you_sure("That disk does not exist.\nCreate it? (Y/N)"):
                            continue

                    dos.change_disk(diskname)
                    artemis.ui_print('Diskette "'+diskname+'" mounted.\n')

                    if dos.disk_has_autorun():
                        program.load("AUTORUN")
                        if RPC: RPC.update(state="Running disk "+diskname, large_image="artemis_icon")
                        try:
                            program.execute()

                        except KeyboardInterrupt:
                            artemis.ui_print("\nProgram terminated\n")

                        finally:
                            if RPC: RPC.update(state="On the CLI", large_image="artemis_icon")

                # Format current disk
                elif tokenlist[0].category == Token.FORMAT:
                    artemis.ui_print('Format "'+dos._current_disk+'" and destroy all contents? ')
                    if artemis.ui_are_you_sure():
                        dos.format_disk()
                        artemis.ui_print('Format complete!\n')

                # Remove file from disk
                elif tokenlist[0].category == Token.UNLINK:
                    if len(tokenlist) == 1: raise ValueError("UNLINK command missing input")
                    fn = tokenlist[1].lexeme
                    dos.file_remove(fn)
                    artemis.ui_print('"'+fn+'" deleted.\n')

                # Export current disk
                elif tokenlist[0].category == Token.DSKEXPORT:
                    # Use home dir as default instead of current disk
                    dos.chdir_home()
                    try:
                        if len(tokenlist) == 1:
                            fn = dos.get_current_disk()+".dia"
                        else:
                            fn = tokenlist[1].lexeme
                            if '.' not in fn: fn += '.dia'
                        fn = os.path.realpath(fn)
                        artemis.ui_print('Exporting to "{}"... '.format(fn))
                        dos.disk_export(fn)
                        artemis.ui_print("Done!\n")
                    finally:    # Make sure we set the default location back
                        dos.chdir_disk()

                # Import disk from file
                elif tokenlist[0].category == Token.DSKIMPORT:
                    if len(tokenlist) == 1: raise ValueError("DSKIMPORT command missing input")
                    artemis.ui_print('Importing "{}"... '.format(tokenlist[1].lexeme))
                    dos.disk_import(tokenlist[1].lexeme)
                    artemis.ui_print("Done!\nDiskette {} mounted.\n".format(dos.get_current_disk()))

                # HELP!
                elif tokenlist[0].category == Token.HELP:
                    webbrowser.open(_help_url)

                # Unrecognised input
                else:
                    artemis.ui_print("Unrecognised input: ")
                    for token in tokenlist:
                        artemis.ui_print(token.lexeme+" ")
                    artemis.ui_print("\n")

        # Trap all exceptions so that interpreter
        # keeps running
        except KeyError as e:
            artemis.ui_print(str(e)[1:-1]+"\n")
        except Exception as e:
            artemis.ui_print(str(e)+"\n")



if __name__ == "__main__":
    main()
