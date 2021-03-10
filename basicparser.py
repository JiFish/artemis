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

from basictoken import BASICToken as Token
from flowsignal import FlowSignal
import math
import random
import artemis

dos = artemis.dos
tass = artemis.tass


"""Implements a BASIC array, which may have up
to three dimensions of fixed size.

"""
class BASICArray:

    def __init__(self, dimensions):
        """Initialises the object with the specified
        number of dimensions. Maximum number of
        dimensions is three

        :param dimensions: List of array dimensions and their
        corresponding sizes

        """
        self.dims = min(3,len(dimensions))

        if self.dims == 0:
            raise SyntaxError("Zero dimensional array specified")

        # Check for invalid sizes and ensure int
        for i in range(self.dims):
            if dimensions[i] < 0:
                raise SyntaxError("Negative array size specified")
            # Allow sizes like 1.0f, but not 1.1f
            if int(dimensions[i]) != dimensions[i]:
                raise SyntaxError("Fractional array size specified")
            dimensions[i] = int(dimensions[i])

        if self.dims == 1:
            self.data = [None for x in range(dimensions[0])]
        elif self.dims == 2:
            self.data = [[None for x in range(dimensions[1])] for x in range(dimensions[0])]
        else:
            self.data = [[[None for x in range(dimensions[2])] for x in range(dimensions[1])] for x in range(dimensions[0])]

    def pretty_print(self):
        print(str(self.data))

"""Implements a BASIC parser that parses a single
statement when supplied.

"""
class BASICParser:

    def __init__(self):
        # Symbol table to hold variable names mapped
        # to values
        self.__symbol_table = {}

        # Stack on which to store operands
        # when evaluating expressions
        self.__operand_stack = []

        # List to hold contents of DATA statement
        self.__data_values = []

        # List to hold contents of FILEIN statement
        self.__file_values = []

        # These values will be
        # initialised on a per
        # statement basis
        self.__tokenlist = []
        self.__tokenindex = None

        # Set to keep track of extant loop variables
        self. __loop_vars = set()

    def parse(self, tokenlist, line_number):
        """Must be initialised with the list of
        BTokens to be processed. These tokens
        represent a BASIC statement without
        its corresponding line number.

        :param tokenlist: The tokenized program statement
        :param line_number: The line number of the statement

        :return: The FlowSignal to indicate to the program
        how to branch if necessary, None otherwise

        """
        self.__tokenlist = tokenlist
        self.__tokenindex = 0

        # Remember the line number to aid error reporting
        self.__line_number = line_number

        # Assign the first token
        self.__token = self.__tokenlist[self.__tokenindex]

        return self.__stmt()

    def __advance(self):
        """Advances to the next token

        """
        # Move to the next token
        self.__tokenindex += 1

        # Acquire the next token if there any left
        if not self.__tokenindex >= len(self.__tokenlist):
            self.__token = self.__tokenlist[self.__tokenindex]

    def __consume(self, expected_category):
        """Consumes a token from the list

        """
        if self.__token.category == expected_category:
            self.__advance()

        else:
            raise RuntimeError('Expecting ' + Token.catnames[expected_category] +
                               ' in line ' + str(self.__line_number))

    def __stmt(self):
        """Parses a program statement

        :return: The FlowSignal to indicate to the program
        how to branch if necessary, None otherwise

        """
        if self.__token.category in [Token.FOR, Token.IF, Token.NEXT,
                                     Token.ON]:
            return self.__compoundstmt()

        else:
            return self.__simplestmt()

    def __simplestmt(self):
        """Parses a non-compound program statement

        :return: The FlowSignal to indicate to the program
        how to branch if necessary, None otherwise

        """
        if self.__token.category == Token.NAME:
            self.__assignmentstmt()
            return None

        elif self.__token.category == Token.PRINT:
            self.__printstmt()
            return None

        elif self.__token.category == Token.PRINTW:
            self.__printwstmt()
            return None

        elif self.__token.category == Token.PRINTB:
            self.__printbstmt()
            return None

        elif self.__token.category == Token.LET:
            self.__letstmt()
            return None

        elif self.__token.category == Token.GOTO:
            return self.__gotostmt()

        elif self.__token.category == Token.GOSUB:
            return self.__gosubstmt()

        elif self.__token.category == Token.RETURN:
            return self.__returnstmt()

        elif self.__token.category == Token.STOP:
            return self.__stopstmt()

        elif self.__token.category == Token.INPUT:
            self.__inputstmt()
            return None

        elif self.__token.category == Token.WAITKEY:
            self.__waitkeystmt()
            return None

        elif self.__token.category == Token.KEY:
            self.__keystmt()
            return None

        elif self.__token.category == Token.DIM:
            self.__dimstmt()
            return None

        elif self.__token.category == Token.RANDOMIZE:
            self.__randomizestmt()
            return None

        elif self.__token.category == Token.DATA:
            self.__datastmt()
            return None

        elif self.__token.category == Token.READ:
            self.__readstmt()
            return None

        elif self.__token.category == Token.FILEIN:
            self.__fileinstmt()
            return None

        elif self.__token.category == Token.FILEOUT:
            self.__fileoutstmt()
            return None

        elif self.__token.category == Token.FILEREAD:
            self.__filereadstmt()
            return None

        elif self.__token.category == Token.UNLINK:
            self.__unlinkstmt()
            return None

        elif self.__token.category == Token.COL:
            self.__colstmt()
            return None

        elif self.__token.category == Token.CLS:
            self.__clsstmt()
            return None

        elif self.__token.category == Token.RSTS:
            self.__rstsstmt()
            return None

        elif self.__token.category == Token.BORDER:
            self.__borderstmt()
            return None

        elif self.__token.category == Token.CURSOR:
            self.__cursorstmt()
            return None

        elif self.__token.category == Token.WAIT:
            self.__waitstmt()
            return None

        elif self.__token.category == Token.POKES:
            self.__pokesstmt()
            return None

        elif self.__token.category == Token.LOADS:
            self.__loadsstmt()
            return None

        elif self.__token.category == Token.DUMPS:
            self.__dumpsstmt()
            return None

        elif self.__token.category == Token.SYMBOL:
            self.__symbolstmt()
            return None

        elif self.__token.category == Token.SYMBOLIMG:
            self.__symbolimgstmt()
            return None

        elif self.__token.category == Token.REFRESH:
            self.__refreshstmt()
            return None

        elif self.__token.category == Token.INK:
            self.__inkstmt()
            return None

        elif self.__token.category == Token.MODE:
            self.__modestmt()
            return None

        elif self.__token.category == Token.MUSICPLAY:
            self.__musicplaystmt()
            return None

        elif self.__token.category == Token.MUSICSTOP:
            self.__musicstopstmt()
            return None

        elif self.__token.category == Token.PLOT:
            self.__plotstmt()
            return None

        else:
            # Ignore comments, but raise an error
            # for anything else
            if self.__token.category != Token.REM:
                raise RuntimeError('Expecting program statement in line '
                                   + str(self.__line_number))

    def __printstmt(self):
        """Parses a PRINT statement, causing
        the value that is on top of the
        operand stack to be printed on
        the screen.

        """
        self.__advance()   # Advance past PRINT token

        output = ""
        linebreak = True

        # Check there are items to print
        if not self.__tokenindex >= len(self.__tokenlist):
            self.__logexpr()

            output += str(self.__operand_stack.pop())

            while self.__token.category == Token.COMMA:
                self.__advance()
                if self.__token.category == Token.COMMA:
                    linebreak = False
                    break
                else:
                    self.__logexpr()
                    output += str(self.__operand_stack.pop())

        # Final newline
        if linebreak: output += "\n"

        artemis.ui_print(output)

    def __printwstmt(self):
        """Parses a PRINTW statement"""
        self.__advance()   # Advance past PRINTW token

        # Get the string to print
        self.__logexpr()
        printw_args = [str(self.__operand_stack.pop())]

        # Get the four position args
        for _ in range(4):
            self.__consume(Token.COMMA)
            self.__expr()
            printw_args.append(self.__operand_stack.pop())

        # Optional wrap flag
        if self.__token.category == Token.COMMA:
            self.__advance()
            self.__logexpr()
            printw_args.append(self.__operand_stack.pop())

        try:
            artemis.ui_print_window(*printw_args)
        except ValueError as e:
            raise Exception(str(e) + ' in line '+ str(self.__line_number))

    def __printbstmt(self):
        """Parses a PRINTB statement"""
        self.__advance()   # Advance past PRINTB token

        # Get the string to print
        self.__logexpr()
        printb_args = [str(self.__operand_stack.pop())]

        # Optional prompt string
        if self.__token.category == Token.COMMA:
            self.__advance()
            self.__logexpr()
            printb_args.append(str(self.__operand_stack.pop()))

        try:
            artemis.ui_print_breaking_list(*printb_args)
        except ValueError as e:
            raise Exception(str(e) + ' in line '+ str(self.__line_number))

    def __letstmt(self):
        """Parses a LET statement,
        consuming the LET keyword.
        """
        self.__advance()  # Advance past the LET token
        self.__assignmentstmt()

    def __gotostmt(self):
        """Parses a GOTO statement

        :return: A FlowSignal containing the target line number
        of the GOTO

        """
        self.__advance()  # Advance past GOTO token
        self.__expr()

        # Set up and return the flow signal
        return FlowSignal(ftarget=self.__operand_stack.pop())

    def __gosubstmt(self):
        """Parses a GOSUB statement

        :return: A FlowSignal containing the first line number
        of the subroutine

        """

        self.__advance()  # Advance past GOSUB token
        self.__expr()

        # Set up and return the flow signal
        return FlowSignal(ftarget=self.__operand_stack.pop(),
                          ftype=FlowSignal.GOSUB)

    def __returnstmt(self):
        """Parses a RETURN statement"""

        self.__advance()  # Advance past RETURN token

        # Set up and return the flow signal
        return FlowSignal(ftype=FlowSignal.RETURN)

    def __stopstmt(self):
        """Parses a STOP statement"""

        self.__advance()  # Advance past STOP token

        return FlowSignal(ftype=FlowSignal.STOP)

    def __assignmentstmt(self):
        """Parses an assignment statement,
        placing the corresponding
        variable and its value in the symbol
        table.

        """
        left = self.__token.lexeme  # Save lexeme of
                                    # the current token
        self.__advance()

        if self.__token.category == Token.LEFTPAREN:
            # We are assiging to an array
            self.__arrayassignmentstmt(left)

        else:
            # We are assigning to a simple variable
            self.__consume(Token.ASSIGNOP)
            self.__logexpr()

            # Check that we are using the right variable name format
            right = self.__operand_stack.pop()

            if left.endswith('$') and not isinstance(right, str):
                raise SyntaxError('Syntax error: Attempt to assign non string to string variable' +
                                  ' in line ' + str(self.__line_number))

            elif not left.endswith('$') and isinstance(right, str):
                raise SyntaxError('Syntax error: Attempt to assign string to numeric variable' +
                                  ' in line ' + str(self.__line_number))

            self.__symbol_table[left] = right

    def __dimstmt(self):
        """Parses  DIM statement and creates a symbol
        table entry for an array of the specified
        dimensions.

        """
        self.__advance()  # Advance past DIM keyword

        # Extract the array name, append a suffix so
        # that we can distinguish from simple variables
        # in the symbol table
        name = self.__token.lexeme + '_array'
        self.__advance()  # Advance past array name

        self.__consume(Token.LEFTPAREN)

        # Extract the dimensions
        dimensions = []
        if not self.__tokenindex >= len(self.__tokenlist):
            self.__expr()
            dimensions.append(self.__operand_stack.pop())

            while self.__token.category == Token.COMMA:
                self.__advance()  # Advance past comma
                self.__expr()
                dimensions.append(self.__operand_stack.pop())

        self.__consume(Token.RIGHTPAREN)

        if len(dimensions) > 3:
            raise SyntaxError("Maximum number of array dimensions is three " +
                              "in line " + str(self.__line_number))

        self.__symbol_table[name] = BASICArray(dimensions)

    def __arrayassignmentstmt(self, name):
        """Parses an assignment to an array variable

        :param name: Array name

        """
        self.__consume(Token.LEFTPAREN)

        # Capture the index variables
        # Extract the dimensions
        indexvars = []
        if not self.__tokenindex >= len(self.__tokenlist):
            self.__expr()
            indexvars.append(self.__operand_stack.pop())

            while self.__token.category == Token.COMMA:
                self.__advance()  # Advance past comma
                self.__expr()
                indexvars.append(self.__operand_stack.pop())

        try:
            BASICarray = self.__symbol_table[name + '_array']

        except KeyError:
            raise KeyError('Array could not be found in line ' +
                           str(self.__line_number))

        if BASICarray.dims != len(indexvars):
            raise IndexError('Incorrect number of indices applied to array ' +
                             'in line ' + str(self.__line_number))

        self.__consume(Token.RIGHTPAREN)
        self.__consume(Token.ASSIGNOP)

        self.__logexpr()

        # Check that we are using the right variable name format
        right = self.__operand_stack.pop()

        if name.endswith('$') and not isinstance(right, str):
            raise SyntaxError('Attempt to assign non string to string array' +
                              ' in line ' + str(self.__line_number))

        elif not name.endswith('$') and isinstance(right, str):
            raise SyntaxError('Attempt to assign string to numeric array' +
                              ' in line ' + str(self.__line_number))

        # Assign to the specified array index
        try:
            if len(indexvars) == 1:
                BASICarray.data[indexvars[0]] = right

            elif len(indexvars) == 2:
                BASICarray.data[indexvars[0]][indexvars[1]] = right

            elif len(indexvars) == 3:
                BASICarray.data[indexvars[0]][indexvars[1]][indexvars[2]] = right

        except IndexError:
            raise IndexError('Array index out of range in line ' +
                             str(self.__line_number))

    def __waitkeystmt(self):
        """Parses an waitkey statement, extracts the input
        from the user and places the values into the
        symbol table

        """
        self.__advance()  # Advance past WAITKEY token

        if self.__token.category != Token.NAME and self.__token.category != Token.WAITKEY:
            raise ValueError('Expecting NAME in WAITKEY statement ' +
                             'in line ' + str(self.__line_number))

        input = artemis.ui_input_key()
        if self.__token.category == Token.NAME:
            self.__symbol_table[self.__token.lexeme] = input


    def __keystmt(self):
        """Parses an key statement, extracts the input
        from the user and places the values into the
        symbol table

        """
        self.__advance()  # Advance past KEY token

        if self.__token.category != Token.NAME:
            raise ValueError('Expecting NAME in KEY statement ' +
                             'in line ' + str(self.__line_number))

        input = artemis.ui_input_key(True)
        if self.__token.category == Token.NAME:
            self.__symbol_table[self.__token.lexeme] = input


    def __inputstmt(self):
        """Parses an input statement, extracts the input
        from the user and places the values into the
        symbol table

        """
        self.__advance()  # Advance past INPUT token

        prompt = '? '
        if self.__token.category == Token.STRING:
            # Acquire the input prompt
            self.__logexpr()
            prompt = self.__operand_stack.pop()
            self.__consume(Token.COLON)

        # Acquire the comma separated input variables
        variables = []
        if not self.__tokenindex >= len(self.__tokenlist):
            if self.__token.category != Token.NAME:
                raise ValueError('Expecting NAME in INPUT statement ' +
                                 'in line ' + str(self.__line_number))
            variables.append(self.__token.lexeme)
            self.__advance()  # Advance past variable

            while self.__token.category == Token.COMMA:
                self.__advance()  # Advance past comma
                variables.append(self.__token.lexeme)
                self.__advance()  # Advance past variable

        # Gather input from the user into the variables
        inputvals = artemis.ui_input(prompt).split(',', (len(variables)-1))
        artemis.ui_print("\n")

        for variable in variables:
            left = variable

            try:
                right = inputvals.pop(0)

                if left.endswith('$'):
                    self.__symbol_table[left] = str(right)

                elif not left.endswith('$'):
                    try:
                        if '.' in right:
                           self.__symbol_table[left] = float(right)
                        else:
                           self.__symbol_table[left] = int(right)

                    except ValueError:
                        raise ValueError('Non-numeric input provided to a numeric variable ' +
                                         'in line ' + str(self.__line_number))

            except IndexError:
                # No more input to process
                pass

    def __datastmt(self):
        """Parses a DATA statement"""

        self.__advance()  # Advance past DATA token

        # Acquire the comma separated values
        if not self.__tokenindex >= len(self.__tokenlist):
            self.__expr()
            self.__data_values.append(self.__operand_stack.pop())

            while self.__token.category == Token.COMMA:
                self.__advance()  # Advance past comma
                self.__expr()
                self.__data_values.append(self.__operand_stack.pop())

    def __plotstmt(self):
        """Parses a PLOT statement
        """
        self.__advance()   # Advance past PLOT token

        self.__expr()
        xpos = self.__operand_stack.pop()
        self.__consume(Token.COMMA)
        self.__expr()
        ypos = self.__operand_stack.pop()

        artemis.ui_psuedo_plot(xpos, ypos)

    def __musicplaystmt(self):
        """Parses a MUSICPLAY statement"""

        self.__advance()  # Advance past MUSICPLAY token

        self.__expr()
        notestr = self.__operand_stack.pop()

        if self.__token.category == Token.COMMA:
            self.__advance()  # Advance past comma
            self.__expr()
            mode = self.__operand_stack.pop()
        else:
            mode = 0

        if mode < 0 or mode > 2:
            raise ValueError("Invalid mode for MUSICPLAY in line "
                             + str(self.__line_number))

        try:
            tass.play_string(notestr, mode)
        except ValueError as e:
            raise ValueError(str(e) + ' in line '+ str(self.__line_number))


    def __musicstopstmt(self):
        """Parses a MUSICSTOP statement"""

        self.__advance()  # Advance past MUSICPLAY token

        tass.stop()

    def __loadsstmt(self):
        """Parses a LOADS statement"""

        self.__advance()  # Advance past LOADS token

        self.__expr()
        fn = self.__operand_stack.pop()

        try:
            artemis.load_screen(dos.read_data_file(fn, "sda"))
        except Exception as e:
            raise Exception(str(e) + ' in line '+ str(self.__line_number))

    def __dumpsstmt(self):
        """Parses a DUMPS statement"""

        self.__advance()  # Advance past DUMPS token

        self.__expr()
        fn = self.__operand_stack.pop()

        try:
            artemis.dump_screen(fn)
        except Exception as e:
            raise Exception(str(e) + ' in line '+ str(self.__line_number))

    def __fileinstmt(self):
        """Parses a FILEIN statement"""

        self.__advance()  # Advance past FILEIN token

        self.__expr()
        fn = self.__operand_stack.pop()
        start = None
        end = None

        if self.__token.category == Token.COMMA:
            self.__advance()  # Advance past comma
            self.__expr()
            start = self.__operand_stack.pop()

            if self.__token.category == Token.COMMA:
                self.__advance()  # Advance past comma
                self.__expr()
                end = self.__operand_stack.pop()

        try:
            # Retrieve file data and slice
            data = dos.read_data_file(fn)[start:end]
            # Verify data before we store it
            for i in data:
                if type(i) not in [int, float, str]: raise TypeError()
            # overwrite existing values
            self.__file_values = data
        except OSError as e:
            raise ValueError(str(e) + ' in line '+ str(self.__line_number))
        except TypeError:
            raise TypeError('Invalid data file in line '+ str(self.__line_number))

    def __fileoutstmt(self):
        """Parses a FILEOUT statement"""

        self.__advance()  # Advance past FILEOUT token

        self.__expr()
        fn = self.__operand_stack.pop()

        self.__consume(Token.COMMA)
        self.__expr()
        mode = self.__operand_stack.pop()
        if mode != 0 and mode != 1:
            raise ValueError("Invalid FILEOUT overwrite mode " +
                             'in line ' + str(self.__line_number))

        # Acquire the comma separated values
        writebuff = []
        self.__consume(Token.COMMA)
        self.__expr()
        writebuff.append(self.__operand_stack.pop())

        while self.__token.category == Token.COMMA:
            self.__advance()  # Advance past comma
            self.__expr()
            writebuff.append(self.__operand_stack.pop())

        # Attempt file write
        try:
            if mode == 0:
                dos.write_data_file(writebuff, fn)
            else:
                dos.append_data_file(writebuff, fn)
        except OSError as e:
            raise ValueError(str(e) + ' in line '+ str(self.__line_number))

    def __unlinkstmt(self):
        """Parses a UNLINK statement"""

        self.__advance()  # Advance past UNLINK token

        self.__expr()
        fn = self.__operand_stack.pop()

        try:
            dos.file_remove(fn)
        except: pass    # Fail silently

    def __filereadstmt(self):
        self.__readstmt(True)

    def __readstmt(self, fromfile = False):
        """Parses a READ/FILEREAD statement."""

        self.__advance()  # Advance past READ / FILEREAD token

        # Get the list we are working with
        if fromfile:
            readlist = self.__file_values
        else:
            readlist = self.__data_values

        # Acquire the comma separated input variables
        variables = []
        if not self.__tokenindex >= len(self.__tokenlist):
            variables.append(self.__token.lexeme)
            self.__advance()  # Advance past variable

            while self.__token.category == Token.COMMA:
                self.__advance()  # Advance past comma
                variables.append(self.__token.lexeme)
                self.__advance()  # Advance past variable

        # Check that we have enough data values to fill the
        # variables
        if len(variables) > len(readlist):
            raise RuntimeError('Insufficient constants supplied to '+
                                ('FILEREAD' if fromfile else 'READ')+
                               ' in line ' + str(self.__line_number))

        # Gather input from the DATA statement into the variables
        for variable in variables:
            left = variable
            right = readlist.pop(0)

            if left.endswith('$'):
                # Python inserts quotes around input data
                if isinstance(right, int):
                    raise ValueError('Non-string input provided to a string variable ' +
                                     'in line ' + str(self.__line_number))

                else:
                    self.__symbol_table[left] = right

            elif not left.endswith('$'):
                try:
                    if '.' in right:
                       self.__symbol_table[left] = float(right)
                    else:
                       self.__symbol_table[left] = int(right)

                except ValueError:
                    raise ValueError('Non-numeric input provided to a numeric variable ' +
                                     'in line ' + str(self.__line_number))

    def __clsstmt(self):
        """Parses a CLS statement"""

        self.__advance()  # Advance past CLS token

        artemis.cls()

    def __rstsstmt(self):
        """Parses a RSTS statement"""

        self.__advance()  # Advance past RSTS token

        artemis.reset_screen()

    def __colstmt(self):
        """Parses a COL statement"""

        self.__advance()  # Advance past COL token

        self.__expr()
        foreground = self.__operand_stack.pop()
        if self.__token.category == Token.COMMA:
            self.__advance()  # Advance past comma
            self.__expr()
            background = self.__operand_stack.pop()
        else:
            background = -1

        try:
            artemis.set_color(foreground, background)
        except ValueError:
            raise ValueError('Input provided to COL statement out of range ' +
                             'in line ' + str(self.__line_number))


    def __cursorstmt(self):
        """Parses a CURSOR statement"""

        self.__advance()  # Advance past CURSOR token

        self.__expr()
        param1 = self.__operand_stack.pop()

        # Setting position
        if self.__token.category == Token.COMMA:
            self.__advance()  # Advance past comma
            self.__expr()
            ypos = self.__operand_stack.pop()

            try:
                artemis.set_cursor(param1, ypos)
            except ValueError as e:
                raise ValueError(str(e) + ' in line '+ str(self.__line_number))

        # Setting character
        else:
            try:
                artemis.set_cursor_symbol(param1)
            except ValueError as e:
                raise ValueError(str(e) + ' in line '+ str(self.__line_number))


    def __pokesstmt(self):
        """Parses a POKES statement"""

        self.__advance()  # Advance past CURSOR token

        self.__expr()
        pos = self.__operand_stack.pop()

        self.__consume(Token.COMMA)

        self.__expr()
        param_one = self.__operand_stack.pop()

        self.__consume(Token.COMMA)

        self.__expr()
        param_two = self.__operand_stack.pop()

        # If we have a third comma, this is the alternate syntax
        param_three = None
        if self.__token.category == Token.COMMA:
            self.__advance()  # Advance past comma
            self.__expr()
            param_three = self.__operand_stack.pop()

        try:
            if param_three == None:
                artemis.manipulate_cell(pos, param_one, param_two)
            else:   # alternate syntax
                artemis.manipulate_cell(pos, 0, param_one)
                artemis.manipulate_cell(pos, 1, param_two)
                artemis.manipulate_cell(pos, 2, param_three)

        except ValueError as e:
            raise ValueError(str(e)+" in POKES in line " +
                             str(self.__line_number))


    def __symbolstmt(self):
        """Parses a SYMBOL statement"""

        self.__advance()  # Advance past SYMBOL token

        self.__expr()
        charcode = self.__operand_stack.pop()

        self.__consume(Token.COMMA)

        self.__expr()
        newchar = self.__operand_stack.pop()

        try:
            if isinstance(newchar, str):
                artemis.redefine_char(charcode, newchar)
            else:
                intlist = [newchar]

                # Look for next 7 values
                for _ in range(7):
                    if self.__token.category != Token.COMMA: break
                    self.__advance()  # Advance past comma
                    self.__expr()
                    intlist.append(self.__operand_stack.pop())

                artemis.redefine_char_from_int_list(charcode, intlist)

        except ValueError:
            raise ValueError("Invalid value supplied to SYMBOL in line " +
                             str(self.__line_number))

        except IndexError:
            raise IndexError("Value supplied to SYMBOL out of range in line " +
                             str(self.__line_number))


    def __symbolimgstmt(self):
        """Parses a SYMBOLIMG statement"""

        self.__advance()  # Advance past SYMBOLIMG token

        self.__expr()
        fn = self.__operand_stack.pop()

        try:
            artemis.load_charset(fn)
        except Exception as e:
            raise Exception(str(e) + ' in line '+ str(self.__line_number))


    def __inkstmt(self):
        """Parses a INK statement"""

        self.__advance()  # Advance past INK token

        p = []
        for i in range(4):
            if i > 0: self.__consume(Token.COMMA)

            self.__expr()
            p.append(self.__operand_stack.pop())

        try:
            artemis.set_palette(*p)

        except ValueError:
            raise ValueError("Invalid value supplied to INK in line " +
                             str(self.__line_number))

        except IndexError:
            raise IndexError("Value supplied to INK out of range in line " +
                             str(self.__line_number))


    def __borderstmt(self):
        """Parses a BORDER statement"""

        self.__advance()  # Advance past BORDER token

        self.__expr()
        col = self.__operand_stack.pop()
        if not isinstance(col, int):
            raise ValueError('Value provided to BORDER not a number in line '+ str(self.__line_number))
        if col < 0 or col > 15:
            raise ValueError('Value provided to BORDER out of range in line '+ str(self.__line_number))

        artemis.set_border(col)


    def __waitstmt(self):
        """Parses a WAIT statement"""

        self.__advance()  # Advance past WAIT token

        self.__expr()
        secs = self.__operand_stack.pop()
        if not isinstance(secs, int) and not isinstance(secs, float):
            raise ValueError('Value provided to WAIT not a number in line '+ str(self.__line_number))
        if secs < 0:
            raise ValueError('Value provided to WAIT out of range in line '+ str(self.__line_number))

        artemis.wait(secs)


    def __refreshstmt(self):
            """Parses a REFRESH statement"""

            self.__advance()  # Advance past REFRESH token

            if self.__token.category == Token.WAIT:
                self.__advance()  # Advance past WAIT token
                artemis.disable_auto_draw()
            else:
                artemis.draw()
                artemis.tick()


    def __modestmt(self):
        """Parses a MODE statement"""

        self.__advance()  # Advance past MODE token

        self.__expr()
        mode = self.__operand_stack.pop()

        try:
            artemis.set_mode(mode)
        except ValueError:
            raise ValueError("Invalid value supplied to MODE in line " +
                             str(self.__line_number))


    def __expr(self):
        """Parses a numerical expression consisting
        of two terms being added or subtracted,
        leaving the result on the operand stack.

        """
        self.__term()  # Pushes value of left term
                       # onto top of stack

        while self.__token.category in [Token.PLUS, Token.MINUS]:
            savedcategory = self.__token.category
            self.__advance()
            self.__term()  # Pushes value of right term
                           # onto top of stack
            rightoperand = self.__operand_stack.pop()
            leftoperand = self.__operand_stack.pop()

            if savedcategory == Token.PLUS:
                self.__operand_stack.append(leftoperand + rightoperand)

            else:
                self.__operand_stack.append(leftoperand - rightoperand)

    def __term(self):
        """Parses a numerical expression consisting
        of two factors being multiplied together,
        leaving the result on the operand stack.

        """
        self.__sign = 1  # Initialise sign to keep track of unary
                         # minuses
        self.__factor()  # Leaves value of term on top of stack

        while self.__token.category in [Token.TIMES, Token.DIVIDE, Token.MODULO]:
            savedcategory = self.__token.category
            self.__advance()
            self.__sign = 1  # Initialise sign
            self.__factor()  # Leaves value of term on top of stack
            rightoperand = self.__operand_stack.pop()
            leftoperand = self.__operand_stack.pop()

            if savedcategory == Token.TIMES:
                self.__operand_stack.append(leftoperand * rightoperand)

            elif savedcategory == Token.DIVIDE:
                self.__operand_stack.append(leftoperand / rightoperand)

            else:
                self.__operand_stack.append(leftoperand % rightoperand)

    def __factor(self):
        """Evaluates a numerical expression
        and leaves its value on top of the
        operand stack.

        """
        if self.__token.category == Token.PLUS:
            self.__advance()
            self.__factor()

        elif self.__token.category == Token.MINUS:
            self.__sign = -self.__sign
            self.__advance()
            self.__factor()

        elif self.__token.category == Token.UNSIGNEDINT:
            self.__operand_stack.append(self.__sign*int(self.__token.lexeme))
            self.__advance()

        elif self.__token.category == Token.UNSIGNEDFLOAT:
            self.__operand_stack.append(self.__sign*float(self.__token.lexeme))
            self.__advance()

        elif self.__token.category == Token.STRING:
            self.__operand_stack.append(self.__token.lexeme)
            self.__advance()

        elif self.__token.category == Token.NAME and \
             self.__token.category not in Token.functions:
            # Check if this is a simple or array variable
            if (self.__token.lexeme + '_array') in self.__symbol_table:
                # Capture the current lexeme
                arrayname = self.__token.lexeme + '_array'

                # Array must be processed
                # Capture the index variables
                self.__advance()  # Advance past the array name

                try:
                    self.__consume(Token.LEFTPAREN)
                except RuntimeError:
                    raise RuntimeError('Array used without index in line ' +
                                     str(self.__line_number))

                indexvars = []
                if not self.__tokenindex >= len(self.__tokenlist):
                    self.__expr()
                    indexvars.append(self.__operand_stack.pop())

                    while self.__token.category == Token.COMMA:
                        self.__advance()  # Advance past comma
                        self.__expr()
                        indexvars.append(self.__operand_stack.pop())

                BASICarray = self.__symbol_table[arrayname]
                arrayval = self.__get_array_val(BASICarray, indexvars)

                if arrayval != None:
                    self.__operand_stack.append(self.__sign*arrayval)

                else:
                    raise IndexError('Empty array value returned in line ' +
                                     str(self.__line_number))

            elif self.__token.lexeme in self.__symbol_table:
                # Simple variable must be processed
                self.__operand_stack.append(self.__sign*self.__symbol_table[self.__token.lexeme])

            else:
                raise RuntimeError('Name ' + self.__token.lexeme + ' is not defined' +
                                   ' in line ' + str(self.__line_number))

            self.__advance()

        elif self.__token.category == Token.LEFTPAREN:
            self.__advance()

            # Save sign because expr() calls term() which resets
            # sign to 1
            savesign = self.__sign
            self.__logexpr()  # Value of expr is pushed onto stack

            if savesign == -1:
                # Change sign of expression
                self.__operand_stack[-1] = -self.__operand_stack[-1]

            self.__consume(Token.RIGHTPAREN)

        elif self.__token.category in Token.functions:
            self.__operand_stack.append(self.__evaluate_function(self.__token.category))

        else:
            raise RuntimeError('Expecting factor in numeric expression' +
                               ' in line ' + str(self.__line_number))

    def __get_array_val(self, BASICarray, indexvars):
        """Extracts the value from the given BASICArray at the specified indexes

        :param BASICarray: The BASICArray
        :param indexvars: The list of indexes, one for each dimension

        :return: The value at the indexed position in the array

        """
        if BASICarray.dims != len(indexvars):
            raise IndexError('Incorrect number of indices applied to array ' +
                             'in line ' + str(self.__line_number))

        # Fetch the value from the array
        try:
            if len(indexvars) == 1:
                arrayval = BASICarray.data[indexvars[0]]

            elif len(indexvars) == 2:
                arrayval = BASICarray.data[indexvars[0]][indexvars[1]]

            elif len(indexvars) == 3:
                arrayval = BASICarray.data[indexvars[0]][indexvars[1]][indexvars[2]]

        except IndexError:
            raise IndexError('Array index out of range in line ' +
                             str(self.__line_number))

        return arrayval

    def __compoundstmt(self):
        """Parses compound statements,
        specifically if-then-else and
        loops

        :return: The FlowSignal to indicate to the program
        how to branch if necessary, None otherwise

        """
        if self.__token.category == Token.FOR:
            return self.__forstmt()

        elif self.__token.category == Token.NEXT:
            return self.__nextstmt()

        elif self.__token.category == Token.IF:
            return self.__ifstmt()

        elif self.__token.category == Token.ON:
            return self.__ongosubstmt()

    def __ifstmt(self):
        """Parses if-then-else
        statements

        :return: The FlowSignal to indicate to the program
        how to branch if necessary, None otherwise

        """

        self.__advance()  # Advance past IF token
        self.__logexpr()

        # Save result of expression
        saveval = self.__operand_stack.pop()

        # Process the THEN part and save the jump value
        self.__consume(Token.THEN)

        if self.__token.category == Token.GOTO:
            self.__advance()    # Advance past optional GOTO

        self.__expr()
        then_jump = self.__operand_stack.pop()

        # Jump if the expression evaluated to True
        if saveval:
            # Set up and return the flow signal
            return FlowSignal(ftarget=then_jump)

        # See if there is an ELSE part
        if self.__token.category == Token.ELSE:
            self.__advance()

            if self.__token.category == Token.GOTO:
                self.__advance()    # Advance past optional GOTO

            self.__expr()

            # Set up and return the flow signal
            return FlowSignal(ftarget=self.__operand_stack.pop())

        else:
            # No ELSE action
            return None

    def __forstmt(self):
        """Parses for loops

        :return: The FlowSignal to indicate that
        a loop start has been processed

        """

        # Set up default loop increment value
        step = 1

        self.__advance()  # Advance past FOR token

        # Process the loop variable initialisation
        loop_variable = self.__token.lexeme  # Save lexeme of
                                             # the current token

        if loop_variable.endswith('$'):
            raise SyntaxError('Syntax error: Loop variable is not numeric' +
                              ' in line ' + str(self.__line_number))

        self.__advance()  # Advance past loop variable
        self.__consume(Token.ASSIGNOP)
        self.__expr()

        # Check that we are using the right variable name format
        # for numeric variables
        start_val = self.__operand_stack.pop()

        # Advance past the 'TO' keyword
        self.__consume(Token.TO)

        # Process the terminating value
        self.__expr()
        end_val = self.__operand_stack.pop()

        # Check if there is a STEP value
        increment = True
        if not self.__tokenindex >= len(self.__tokenlist):
            self.__consume(Token.STEP)

            # Acquire the step value
            self.__expr()
            step = self.__operand_stack.pop()

            # Check whether we are decrementing or
            # incrementing
            if step == 0:
                raise IndexError('Zero step value supplied for loop' +
                                 ' in line ' + str(self.__line_number))

            elif step < 0:
                increment = False

        # Now determine the status of the loop

        # If the loop variable is not in the set of extant
        # variables, this is the first time we have entered the loop
        # Note that we cannot use the presence of the loop variable in
        # the symbol table for this test, as the same variable may already
        # have been instantiated elsewhere in the program
        if loop_variable not in self.__loop_vars:
            self.__symbol_table[loop_variable] = start_val

            # Also add loop variable to set of extant loop
            # variables
            self.__loop_vars.add(loop_variable)

        else:
            # We need to modify the loop variable
            # according to the STEP value
            self.__symbol_table[loop_variable] += step

        # If the loop variable has reached the end value,
        # remove it from the set of extant loop variables to signal that
        # this is the last loop iteration
        stop = False
        if increment and self.__symbol_table[loop_variable] > end_val:
            stop = True

        elif not increment and self.__symbol_table[loop_variable] < end_val:
            stop = True

        if stop:
            # Loop must terminate, so remove loop vriable from set of
            # extant loop variables and remove loop variable from
            # symbol table
            self.__loop_vars.remove(loop_variable)
            del self.__symbol_table[loop_variable]
            return FlowSignal(ftype=FlowSignal.LOOP_SKIP,
                              ftarget=loop_variable)
        else:
            # Set up and return the flow signal
            return FlowSignal(ftype=FlowSignal.LOOP_BEGIN)

    def __nextstmt(self):
        """Processes a NEXT statement that terminates
        a loop

        :return: A FlowSignal indicating that a loop
        has been processed

        """

        self.__advance()  # Advance past NEXT token

        return FlowSignal(ftype=FlowSignal.LOOP_REPEAT)

    def __ongosubstmt(self):
        """Process the ON-GOSUB statement

        :return: A FlowSignal indicating the subroutine line number
        if the condition is true, None otherwise

        """

        self.__advance()  # Advance past ON token
        self.__logexpr()

        # Save result of expression
        saveval = self.__operand_stack.pop()

        # Process the GOSUB part and save the jump value
        # if the condition is met
        if saveval:
            return self.__gosubstmt()
        else:
            return None

    def __relexpr(self):
        """Parses a relational expression
        """
        self.__expr()

        # Since BASIC uses same operator for both
        # assignment and equality, we need to check for this
        if self.__token.category == Token.ASSIGNOP:
            self.__token.category = Token.EQUAL

        if self.__token.category in [Token.LESSER, Token.LESSEQUAL,
                              Token.GREATER, Token.GREATEQUAL,
                              Token.EQUAL, Token.NOTEQUAL]:
            savecat = self.__token.category
            self.__advance()
            self.__expr()

            right = self.__operand_stack.pop()
            left = self.__operand_stack.pop()

            if savecat == Token.EQUAL:
                self.__operand_stack.append(left == right)  # Push True or False

            elif savecat == Token.NOTEQUAL:
                self.__operand_stack.append(left != right)  # Push True or False

            elif savecat == Token.LESSER:
                self.__operand_stack.append(left < right)  # Push True or False

            elif savecat == Token.GREATER:
                self.__operand_stack.append(left > right)  # Push True or False

            elif savecat == Token.LESSEQUAL:
                self.__operand_stack.append(left <= right)  # Push True or False

            elif savecat == Token.GREATEQUAL:
                self.__operand_stack.append(left >= right)  # Push True or False

    def __logexpr(self):
        """Parses a logical expression
        """
        self.__notexpr()

        while self.__token.category in [Token.OR, Token.AND]:
            savecat = self.__token.category
            self.__advance()
            self.__notexpr()

            right = self.__operand_stack.pop()
            left = self.__operand_stack.pop()

            if savecat == Token.OR:
                self.__operand_stack.append(left or right)  # Push True or False

            elif savecat == Token.AND:
                self.__operand_stack.append(left and right)  # Push True or False

    def __notexpr(self):
        """Parses a logical not expression
        """
        if self.__token.category == Token.NOT:
            self.__advance()
            self.__relexpr()
            right = self.__operand_stack.pop()
            self.__operand_stack.append(not right)
        else:
            self.__relexpr()

    def __evaluate_function(self, category):
        """Evaluate the function in the statement
        and return the result.

        :return: The result of the function

        """

        self.__advance()  # Advance past function name

        # Process arguments according to function
        if category == Token.RND:
            return random.random()

        if category == Token.PI:
            return math.pi

        if category == Token.SYSTIME:
            return artemis.get_system_time()

        if category == Token.CURSORX:
            return artemis.get_cursor_x()

        if category == Token.CURSORY:
            return artemis.get_cursor_y()

        if category == Token.RNDINT:
            self.__consume(Token.LEFTPAREN)

            self.__expr()
            lo = self.__operand_stack.pop()

            self.__consume(Token.COMMA)

            self.__expr()
            hi = self.__operand_stack.pop()

            self.__consume(Token.RIGHTPAREN)

            try:
                return random.randint(lo, hi)

            except ValueError:
                raise ValueError("Invalid value supplied to RNDINT in line " +
                                 str(self.__line_number))

        if category == Token.PEEKS:
            self.__consume(Token.LEFTPAREN)

            self.__expr()
            pos = self.__operand_stack.pop()

            self.__consume(Token.COMMA)

            self.__expr()
            key = self.__operand_stack.pop()

            self.__consume(Token.RIGHTPAREN)

            try:
                cell = artemis.get_cell(pos)
                return cell[key]

            except ValueError:
                raise ValueError("Invalid value supplied to PEEKS in line " +
                                 str(self.__line_number))

            except IndexError:
                raise IndexError("Value supplied to PEEKS out of range in line " +
                                 str(self.__line_number))

        if category == Token.MAX:
            self.__consume(Token.LEFTPAREN)

            self.__expr()
            value_list = [self.__operand_stack.pop()]

            while self.__token.category == Token.COMMA:
                self.__advance() # Advance past comma
                self.__expr()
                value_list.append(self.__operand_stack.pop())

            self.__consume(Token.RIGHTPAREN)

            try:
                return max(*value_list)

            except TypeError:
                raise TypeError("Invalid type supplied to MAX in line " +
                                 str(self.__line_number))

        if category == Token.MIN:
            self.__consume(Token.LEFTPAREN)

            self.__expr()
            value_list = [self.__operand_stack.pop()]

            while self.__token.category == Token.COMMA:
                self.__advance() # Advance past comma
                self.__expr()
                value_list.append(self.__operand_stack.pop())

            self.__consume(Token.RIGHTPAREN)

            try:
                return min(*value_list)

            except TypeError:
                raise TypeError("Invalid type supplied to MIN in line " +
                                 str(self.__line_number))

        if category == Token.POW:
            self.__consume(Token.LEFTPAREN)

            self.__expr()
            base = self.__operand_stack.pop()

            self.__consume(Token.COMMA)

            self.__expr()
            exponent = self.__operand_stack.pop()

            self.__consume(Token.RIGHTPAREN)

            try:
                return math.pow(base, exponent)

            except ValueError:
                raise ValueError("Invalid value supplied to POW in line " +
                                 str(self.__line_number))

        if category == Token.TERNARY:
            self.__consume(Token.LEFTPAREN)

            self.__logexpr()
            condition = self.__operand_stack.pop()

            self.__consume(Token.COMMA)

            self.__expr()
            whentrue = self.__operand_stack.pop()

            self.__consume(Token.COMMA)

            self.__expr()
            whenfalse = self.__operand_stack.pop()

            self.__consume(Token.RIGHTPAREN)

            return whentrue if condition else whenfalse

        if category == Token.MID:
            self.__consume(Token.LEFTPAREN)

            self.__expr()
            instring = self.__operand_stack.pop()

            self.__consume(Token.COMMA)

            self.__expr()
            start = self.__operand_stack.pop()

            if self.__token.category == Token.COMMA:
                self.__advance() # Advance past comma
                self.__expr()
                end = self.__operand_stack.pop()
            else:
                end = None

            self.__consume(Token.RIGHTPAREN)

            try:
                return instring[start:end]

            except TypeError:
                raise TypeError("Invalid type supplied to MID$ in line " +
                                 str(self.__line_number))

        if category == Token.INSTR:
            self.__consume(Token.LEFTPAREN)

            self.__expr()
            hackstackstring = self.__operand_stack.pop()
            if not isinstance(hackstackstring, str):
                raise TypeError("Invalid type supplied to INSTR in line " +
                                 str(self.__line_number))

            self.__consume(Token.COMMA)

            self.__expr()
            needlestring = self.__operand_stack.pop()

            start = end = None
            if self.__token.category == Token.COMMA:
                self.__advance() # Advance past comma
                self.__expr()
                start = self.__operand_stack.pop()

                if self.__token.category == Token.COMMA:
                    self.__advance() # Advance past comma
                    self.__expr()
                    end = self.__operand_stack.pop()

            self.__consume(Token.RIGHTPAREN)

            try:
                return hackstackstring.find(needlestring, start, end)

            except TypeError:
                raise TypeError("Invalid type supplied to INSTR in line " +
                                 str(self.__line_number))

        # Everything else has ONE PARAM
        self.__consume(Token.LEFTPAREN)

        self.__expr()
        value = self.__operand_stack.pop()

        self.__consume(Token.RIGHTPAREN)

        if category == Token.SQR:
            try:
                return math.sqrt(value)

            except ValueError:
                raise ValueError("Invalid value supplied to SQR in line " +
                                 str(self.__line_number))

        elif category == Token.ABS:
            try:
                return abs(value)

            except ValueError:
                raise ValueError("Invalid value supplied to ABS in line " +
                                 str(self.__line_number))

        elif category == Token.ATN:
            try:
                return math.atan(value)

            except ValueError:
                raise ValueError("Invalid value supplied to ATN in line " +
                                 str(self.__line_number))

        elif category == Token.COS:
            try:
                return math.cos(value)

            except ValueError:
                raise ValueError("Invalid value supplied to COS in line " +
                                 str(self.__line_number))

        elif category == Token.EXP:
            try:
                return math.exp(value)

            except ValueError:
                raise ValueError("Invalid value supplied to EXP in line " +
                                 str(self.__line_number))

        elif category == Token.INT:
            try:
                return math.floor(value)

            except ValueError:
                raise ValueError("Invalid value supplied to INT in line " +
                                 str(self.__line_number))

        elif category == Token.ROUND:
            try:
                return round(value)

            except TypeError:
                raise TypeError("Invalid type supplied to LEN in line " +
                                 str(self.__line_number))

        elif category == Token.LOG:
            try:
                return math.log(value)

            except ValueError:
                raise ValueError("Invalid value supplied to LOG in line " +
                                 str(self.__line_number))

        elif category == Token.SIN:
            try:
                return math.sin(value)

            except ValueError:
                raise ValueError("Invalid value supplied to SIN in line " +
                                 str(self.__line_number))

        elif category == Token.TAN:
            try:
                return math.tan(value)

            except ValueError:
                raise ValueError("Invalid value supplied to TAN in line " +
                                 str(self.__line_number))

        elif category == Token.CHR:
            try:
                if value < 0 or value > 255:
                    raise ValueError("Value supplied to CHR$ out of range in line " +
                                 str(self.__line_number))
                return chr(value)

            except TypeError:
                raise TypeError("Invalid type supplied to CHR$ in line " +
                                 str(self.__line_number))

            except ValueError:
                raise ValueError("Invalid value supplied to CHR$ in line " +
                                 str(self.__line_number))

        elif category == Token.ASC:
            try:
                return ord(value)

            except TypeError:
                raise TypeError("Invalid type supplied to ASC in line " +
                                 str(self.__line_number))

            except ValueError:
                raise ValueError("Invalid value supplied to ASC in line " +
                                 str(self.__line_number))

        elif category == Token.STR:
            return str(value)

        elif category == Token.VAL:
            try:
                numeric = float(value)
                if numeric.is_integer():
                    return int(numeric)
                return numeric

            # Like other BASIC variants, non-numeric strings return 0
            except ValueError:
                return 0

        elif category == Token.LEN:
            try:
                return len(value)

            except TypeError:
                raise TypeError("Invalid type supplied to LEN in line " +
                                 str(self.__line_number))

        elif category == Token.UPPER:
            if not isinstance(value, str):
                raise TypeError("Invalid type supplied to UPPER$ in line " +
                                 str(self.__line_number))

            return value.upper()

        elif category == Token.LOWER:
            if not isinstance(value, str):
                raise TypeError("Invalid type supplied to LOWER$ in line " +
                                 str(self.__line_number))

            return value.lower()

        else:
            raise SyntaxError("Unrecognised function in line " +
                              str(self.__line_number))

    def __randomizestmt(self):
        """Implements a function to seed the random
        number generator

        """
        self.__advance()  # Advance past RANDOMIZE token

        if not self.__tokenindex >= len(self.__tokenlist):
            self.__expr()  # Process the seed
            seed = self.__operand_stack.pop()

            random.seed(seed)

        else:
            random.seed()
