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

"""Class to represent a token for the BASIC
programming language. A token consists of
three items:

column      Column in which token starts
category    Category of the token
lexeme      Token in string form

"""


class BASICToken:

        """BASICToken categories"""

        EOF             = 0   # End of file
        LET             = 1   # LET keyword
        LIST            = 2   # LIST command
        PRINT           = 3   # PRINT command
        RUN             = 4   # RUN command
        FOR             = 5   # FOR keyword
        NEXT            = 6   # NEXT keyword
        IF              = 7   # IF keyword
        THEN            = 8   # THEN keyword
        ELSE            = 9   # ELSE keyword
        ASSIGNOP        = 10  # '='
        LEFTPAREN       = 11  # '('
        RIGHTPAREN      = 12  # ')'
        PLUS            = 13  # '+'
        MINUS           = 14  # '-'
        TIMES           = 15  # '*'
        DIVIDE          = 16  # '/'
        NEWLINE         = 17  # End of line
        UNSIGNEDINT     = 18  # Integer
        NAME            = 19  # Identifier that is not a keyword
        EXIT            = 20  # Used to quit the interpreter
        DIM             = 21  # DIM keyword
        GREATER         = 22  # '>'
        LESSER          = 23  # '<'
        STEP            = 24  # STEP keyword
        GOTO            = 25  # GOTO keyword
        GOSUB           = 26  # GOSUB keyword
        INPUT           = 27  # INPUT keyword
        REM             = 28  # REM keyword
        RETURN          = 29  # RETURN keyword
        SAVE            = 30  # SAVE command
        LOAD            = 31  # LOAD command
        NOTEQUAL        = 32  # '<>'
        LESSEQUAL       = 33  # '<='
        GREATEQUAL      = 34  # '>='
        UNSIGNEDFLOAT   = 35  # Floating point number
        STRING          = 36  # String values
        TO              = 37  # TO keyword
        NEW             = 38  # NEW command
        EQUAL           = 39  # '='
        COMMA           = 40  # ','
        STOP            = 41  # STOP keyword
        COLON           = 42  # ':'
        ON              = 43  # ON keyword
        POW             = 44  # Power function
        SQR             = 45  # Square root function
        ABS             = 46  # Absolute value function
        DIM             = 47  # DIM keyword
        RANDOMIZE       = 48  # RANDOMIZE keyword
        RND             = 49  # RND keyword
        ATN             = 50  # Arctangent function
        COS             = 51  # Cosine function
        EXP             = 52  # Exponential function
        LOG             = 53  # Natural logarithm function
        SIN             = 54  # Sine function
        TAN             = 55  # Tangent function
        DATA            = 56  # DATA keyword
        READ            = 57  # READ keyword
        INT             = 58  # INT function
        CHR             = 59  # CHR$ function
        ASC             = 60  # ASC function
        STR             = 61  # STR$ function
        MID             = 62  # MID$ function
        MODULO          = 63  # MODULO operator
        TERNARY         = 64  # TERNARY functions
        VAL             = 65  # VAL function
        LEN             = 66  # LEN function
        UPPER           = 67  # UPPER function
        LOWER           = 68  # LOWER function
        ROUND           = 69  # ROUND function
        MAX             = 70  # MAX function
        MIN             = 71  # MIN function
        INSTR           = 72  # INSTR function
        AND             = 73  # AND operator
        OR              = 74  # OR operator
        NOT             = 75  # NOT operator

        # JiBasic specific from here. Leaving gap for easier code sharing with PyBasic
        COL             = 100 # Set colors command
        CLS             = 101 # Clear screen command
        WAIT            = 102 # Wait command
        IMPORT          = 103 # Import program from text command
        BORDER          = 104 # Set border colour command
        CURSOR          = 105 # Set cursor position command
        RNDINT          = 106 # RNDINT function
        WAITKEY         = 107 # WAITKEY command
        PEEKS           = 108 # PEEKS function
        POKES           = 109 # POKES command
        SYMBOL          = 110 # SYMBOL command
        REFRESH         = 111 # REFRESH command
        INK             = 112 # INK command
        MODE            = 113 # MODE command
        EXPORT          = 114 # EXPORT command
        FILEIN          = 115 # FILEIN command
        FILEOUT         = 116 # FILEOUT command
        FILEREAD        = 117 # FILEREAD command
        DSKLIST         = 118 # DSKLIST command
        DSKMOUNT        = 119 # DSKMOUNT command
        DSKFORMAT       = 120 # DSKFORMAT command
        DSKRM           = 121 # DSKRM command
        MUSICPLAY       = 122 # MUSICPLAY command
        MUSICSTOP       = 123 # MUSICSTOP command
        KEY             = 124 # KEY command
        SYSTIME         = 125 # TIME function
        LOADS           = 126 # LOADS command
        DUMPS           = 127 # DUMPS command
        HELP            = 128 # HELP command


        # Displayable names for each token category
        catnames = ['EOF', 'LET', 'LIST', 'PRINT', 'RUN',
        'FOR', 'NEXT', 'IF', 'THEN', 'ELSE', 'ASSIGNOP',
        'LEFTPAREN', 'RIGHTPAREN', 'PLUS', 'MINUS', 'TIMES',
        'DIVIDE', 'NEWLINE', 'UNSIGNEDINT', 'NAME', 'EXIT',
        'DIM', 'GREATER', 'LESSER', 'STEP', 'GOTO', 'GOSUB',
        'INPUT', 'REM', 'RETURN', 'SAVE', 'LOAD',
        'NOTEQUAL', 'LESSEQUAL', 'GREATEQUAL',
        'UNSIGNEDFLOAT', 'STRING', 'TO', 'NEW', 'EQUAL',
        'COMMA', 'STOP', 'COLON', 'ON', 'POW', 'SQR', 'ABS',
        'DIM', 'RANDOMIZE', 'RND', 'ATN', 'COS', 'EXP',
        'LOG', 'SIN', 'TAN', 'DATA', 'READ', 'INT',
        'CHR', 'ASC', 'STR', 'MID', 'MODULO', 'TERNARY',
        'VAL', 'LEN', 'UPPER', 'LOWER', 'ROUND',
        'MAX', 'MIN', 'INSTR', 'AND', 'OR', 'NOT']

        # Pad the list up to 99
        catnames += [''] * (99 - len(catnames))

        # Add JiBasic Cat Names
        catnames += ['COL', 'CLS', 'WAIT', 'IMPORT',
        'BORDER', 'CURSOR', 'RNDINT', 'WAITKEY', 'PEEKS',
        'POKES', 'SYMBOL', 'REFRESH', 'INK', 'MODE',
        'EXPORT', 'FILEIN', 'FILEOUT', 'FILEREAD',
        'DSKLIST', 'DSKMOUNT', 'DSKFORMAT', 'DSKRM',
        'MUSICPLAY', 'MUSICSTOP', 'KEY', 'SYSTIME',
        'LOADS', 'DUMPS', 'HELP']

        smalltokens = {'=': ASSIGNOP, '(': LEFTPAREN, ')': RIGHTPAREN,
                       '+': PLUS, '-': MINUS, '*': TIMES, '/': DIVIDE,
                       '\n': NEWLINE, '<': LESSER,
                       '>': GREATER, '<>': NOTEQUAL,
                       '<=': LESSEQUAL, '>=': GREATEQUAL, ',': COMMA,
                       ':': COLON, '%': MODULO, '!=': NOTEQUAL}

        # Dictionary of BASIC reserved words
        keywords = {'LET': LET, 'LIST': LIST, 'PRINT': PRINT,
                    'FOR': FOR, 'RUN': RUN, 'NEXT': NEXT,
                    'IF': IF, 'THEN': THEN, 'ELSE': ELSE,
                    'EXIT': EXIT, 'DIM': DIM, 'STEP': STEP,
                    'GOTO': GOTO, 'GOSUB': GOSUB,
                    'INPUT': INPUT, 'REM': REM, 'RETURN': RETURN,
                    'SAVE': SAVE, 'LOAD': LOAD, 'NEW': NEW,
                    'STOP': STOP, 'TO': TO, 'ON':ON, 'POW': POW,
                    'SQR': SQR, 'ABS': ABS,
                    'RANDOMIZE': RANDOMIZE, 'RND': RND,
                    'ATN': ATN, 'COS': COS, 'EXP': EXP,
                    'LOG': LOG, 'SIN': SIN, 'TAN': TAN,
                    'DATA': DATA, 'READ': READ, 'INT': INT,
                    'CHR$': CHR, 'ASC': ASC, 'STR$': STR,
                    'MID$': MID, 'MOD': MODULO,
                    'IF$': TERNARY, 'IFF': TERNARY,
                    'VAL': VAL, 'LEN': LEN,
                    'UPPER$': UPPER, 'LOWER$': LOWER,
                    'ROUND': ROUND, 'MAX': MAX, 'MIN': MIN,
                    'INSTR': INSTR, 'END': STOP,
                    'AND': AND, 'OR': OR, 'NOT': NOT}

        # JiBasic Dictionary of BASIC reserved words
        keywords = {**keywords,
                    'COL': COL, 'CLS': CLS, 'WAIT': WAIT,
                    'IMPORT': IMPORT, 'BORDER': BORDER,
                    'CURSOR': CURSOR, 'RNDINT': RNDINT,
                    'WAITKEY': WAITKEY, 'PEEKS': PEEKS,
                    'POKES': POKES, 'SYMBOL': SYMBOL,
                    'REFRESH': REFRESH, 'INK':INK, 'MODE':MODE,
                    'EXPORT':EXPORT, 'FILEIN':FILEIN,
                    'FILEOUT': FILEOUT, 'FILEREAD': FILEREAD,
                    'DSKLIST': DSKLIST, 'DSKMOUNT': DSKMOUNT,
                    'DSKFORMAT': DSKFORMAT, 'DSKRM': DSKRM,
                    'MUSICPLAY': MUSICPLAY, 'MUSICSTOP': MUSICSTOP,
                    'KEY': KEY, 'SYSTIME': SYSTIME,
                    'LOADS': LOADS, 'DUMPS': DUMPS,
                    'HELP': HELP}

        # Functions
        functions = {ABS, ATN, COS, EXP, INT, LOG, POW, RND, SIN, SQR, TAN,
                     CHR, ASC, MID, TERNARY, STR, VAL, LEN, UPPER, LOWER,
                     ROUND, MAX, MIN, INSTR}

        # JiBasic Functions
        functions = functions.union({RNDINT, PEEKS, WAITKEY, KEY, SYSTIME})

        def __init__(self, column, category, lexeme):

            self.column = column      # Column in which token starts
            self.category = category  # Category of the token
            self.lexeme = lexeme      # Token in string form

        def pretty_print(self):
            """Pretty prints the token

            """
            print('Column:', self.column,
                  'Category:', self.catnames[self.category],
                  'Lexeme:', self.lexeme)

        def print_lexeme(self):
            print(self.lexeme+' ')
