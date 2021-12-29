import JiBASIC
from JiBASIC import BASICToken as Token
from sys import stderr, version_info

import artemis
import os, io, webbrowser, sys, traceback
from datetime import date

dos = artemis.dos

_help_url = "https://jifish.github.io/artemis/main"

# Discord Presence. Fails gracefully if module does not exist
try:
    from pypresence import Presence
    RPC = Presence('792576960923828255')
    RPC.connect()
    RPC.update(state="On the CLI", large_image="artemis_icon")
except ImportError:
    RPC = None
except Exception:
    pass

def main():
    artemis.set_caption("Artemis Fantasy Microcomputer ({})".format(artemis.version))
    artemis.set_color(6)
    artemis.ui_print("Artemis Microcomputer {}{}\n\n".format(chr(176), date.today().year), do_draw=False)
    artemis.ui_print("JiBASIC {} & Python {}.{}.{}\n\n".format(JiBASIC.version,version_info.major, version_info.minor, version_info.micro), do_draw=False)
    artemis.set_color(1)
    artemis.ui_print("Type HELP to open documentation.\n\n", do_draw=False)
    artemis.ui_print("READY\n", do_draw=False)
    for i in range(0,8):
        artemis.screen[31+i].set((214,(i+1)%8,i))

    lexer = JiBASIC.Lexer()
    program = JiBASIC.Program()

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
                        assert type in ['P','F','D','S']
                    except:
                        type = 'P'

                    if type == 'F':     # List files on the disk
                        plist = dos.list_disk()
                    elif type == 'S':     # List files on the disk
                        plist = dos.list_disk(ext=".bas")
                    elif type == 'D':   # List all disks
                        plist = dos.list_all_disks()
                    else:               # List Program
                        plist = program.list().splitlines()

                    artemis.ui_print_breaking_list(plist)

                # Save the program to disk
                elif tokenlist[0].category == Token.SAVE:
                    if len(tokenlist) == 1: raise ValueError("SAVE command missing input")
                    fn = tokenlist[1].lexeme
                    if '.' not in fn: fn += ".bas"
                    dos.file_put_contents(fn, program.list())
                    artemis.ui_print('Program exported to "{}"\n'.format(fn))

                # Load the program from disk
                elif tokenlist[0].category == Token.LOAD:
                    if len(tokenlist) == 1: raise ValueError("LOAD command missing input")
                    fn = tokenlist[1].lexeme
                    if '.' not in fn: fn += ".bas"
                    try:
                        lines = dos.file_get_contents(fn)
                    except OSError:
                        artemis.ui_print("Program not found.\n")
                        continue
                    program.load_full_program(lexer, lines)
                    artemis.ui_print("Program read from file\n")

                # Delete the program from memory
                elif tokenlist[0].category == Token.NEW:
                    program.delete()

                # Clear the screen
                elif tokenlist[0].category == Token.CLS:
                    artemis.cls()

                # Reset the screen
                elif tokenlist[0].category == Token.RSTS:
                    artemis.reset_screen()

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
                        lines = dos.file_get_contents("autorun.bas")
                        program.load_full_program(lexer, lines)
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

                # Online / DIAL
                elif tokenlist[0].category == Token.DIAL:
                    artemis.online.supply_basic(program, lexer)
                    artemis.online.start(tokenlist[1].lexeme)

                # Run Python script
                elif tokenlist[0].category == Token.PY:
                    with open(tokenlist[1].lexeme, 'r') as infile:
                        pyprog = infile.read()
                        infile.close()
                    try:
                        exec(pyprog, {"__builtins__":artemis.pybox.pyboxbuiltins})
                    except SyntaxError as err:
                        error_class = err.__class__.__name__
                        detail = err.args[0]
                        line_number = err.lineno
                        raise err.__class__("{} at line {}: {}".format(error_class, line_number, detail))
                    except Exception as err:
                        error_class = err.__class__.__name__
                        detail = err.args[0]
                        _, _, tb = sys.exc_info()
                        line_number = traceback.extract_tb(tb)[-1][1]
                        raise err.__class__("{} at line {}: {}".format(error_class, line_number, detail))

                # Easter Egg
                elif tokenlist[0].category == Token.PI:
                    artemis.easter_egg()

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
