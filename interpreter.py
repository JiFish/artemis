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
import os, io, artemis
import webbrowser

dos = artemis.dos

_help_url = "https://github.com/JiFish/artemis#disk-system-and-commands"

def main():
    artemis.set_color(6)
    artemis.set_caption("Artemis Fantasy Microcomputer")
    artemis.ui_print("Artemis Fantasy Microcomputer "+chr(176)+"2020\n\n")
    artemis.ui_print(" JiBASIC 0.5\n\n")
    artemis.set_color(1)
    artemis.ui_print("READY\n")
    for i in range(0,8):
        artemis.screen[111+i] = [214,(i+1)%8,i]

    lexer = Lexer()
    program = Program()

    # Continuously accept user input and act on it until
    # the user enters 'EXIT'
    while True:

        try:
            stmt = artemis.ui_input('>')

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
                    try:
                        program.execute()

                    except KeyboardInterrupt:
                        artemis.ui_print("\nProgram terminated\n")

                # List the program
                elif tokenlist[0].category == Token.LIST:
                    artemis.ui_print_breaking_list(program.list().splitlines())

                # Export the program to disk
                elif tokenlist[0].category == Token.EXPORT:
                    if len(tokenlist) == 1: raise ValueError("EXPORT command missing input")
                    with open(tokenlist[1].lexeme, 'w') as outfile:
                        outfile.write(program.list())
                    artemis.ui_print("Program exported to file\n")

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
                    try:
                        with open(tokenlist[1].lexeme, 'r') as infile:
                            lines = infile.readlines()
                            infile.close()
                        program.delete()
                        for line in lines:
                            artemis.ui_print(line)
                            artemis.draw()
                            program.add_stmt(lexer.tokenize(line.strip()))
                        artemis.ui_print("\nProgram imported from file\n")

                    except OSError:
                        raise OSError("Could not read file")

                # Delete the program from memory
                elif tokenlist[0].category == Token.NEW:
                    program.delete()

                # Clear the screen
                elif tokenlist[0].category == Token.CLS:
                    artemis.cls()

                # List the disk
                elif tokenlist[0].category == Token.DSKLIST:
                    # List files on the disk
                    if len(tokenlist) < 2:
                        artemis.ui_print_breaking_list(dos.list_disk())
                    # List all disks
                    else:
                        artemis.ui_print_breaking_list(dos.list_all_disks())

                # Mount a new or existing disk
                elif tokenlist[0].category == Token.DSKMOUNT:
                    if len(tokenlist) == 1: raise ValueError("DSKMOUNT command missing input")
                    diskname = tokenlist[1].lexeme
                    dos.change_disk(diskname)
                    artemis.ui_print('DISKETTE "'+diskname+'" mounted.\n')

                # Format current disk
                elif tokenlist[0].category == Token.DSKFORMAT:
                    artemis.ui_print('Format "'+dos._current_disk+'" and destroy all contents? ')
                    if artemis.ui_are_you_sure():
                        dos.format_disk()
                        artemis.ui_print('Format complete!\n')

                # Remove file from disk
                elif tokenlist[0].category == Token.DSKRM:
                    if len(tokenlist) == 1: raise ValueError("DSKRM command missing input")
                    fn = tokenlist[1].lexeme
                    dos.file_remove(fn)
                    artemis.ui_print('"'+fn+'" deleted.\n')

                # HELP!
                elif tokenlist[0].category == Token.HELP:
                    # TODO: Send to docs page
                    webbrowser.open(_help_url)

                # Unrecognised input
                else:
                    artemis.ui_print("Unrecognised input\n")
                    for token in tokenlist:
                        token.print_lexeme()
                    artemis.ui_print("\n")

        # Trap all exceptions so that interpreter
        # keeps running
        except KeyError as e:
            artemis.ui_print(str(e)[1:-1]+"\n")
        except Exception as e:
            artemis.ui_print(str(e)+"\n")



if __name__ == "__main__":
    main()
