# Artemis - A Fantasy Microcomputer

## Introduction

### What is a Fantasy Computer?

TODO

### Why Artemis?

Artemis is supposed to be a challenging fantasy computer. Can you create a fun game with the following limitations?

- Using a fairly limited and slow BASIC language. (Though improvements to the language are incoming...)
- With no graphical commands at all, only text
- 125 possible colors and 255 redefinable character glyphs
- 7 text modes to choose from, each a different compromise between number of characters and colors on the screen

As mentioned above JiBASIC is slow. This isn't a bug, it's a feature - or to be more accurate not a priority. Artemis is explicitly not designed to be friendly to developing real-time action games.

### Inspirations

This project was inspired by Basic8 and Ozapell Basic, nether of which was _quite_ what I was after.

Artemis' specifications (and name) were inspired by the Amstrad CPC line of machines. The CPC's unusual 3-level RGB palette was expanded to 5-level for Artemis. The character set is also inspired by Amstrad's custom extended ASCII, using most of the same glyph positions.

### Development

Artemis is also free open-source software and should work on many platforms.

Artemis is currently beta software. However, an important goal is to maintain forward compatibility for programs.

JiBASIC is a fork of PyBasic by richpl (https://github.com/richpl/PyBasic) with many platform-dependent features added. Fixes and improvements from PyBasic will be pulled in to JiBASIC, and any fixes here will be sent back via pull-request. Much of the following documentation is also forked from PyBasic.

Currently programs written for, or saved in, PyBasic will run in Artemis. But this may not be the case in the future.

Artemis is also powered by pygame2 (https://www.pygame.org/news) and midiutil (https://github.com/MarkCWirt/MIDIUtil)

### To start...

Run `artemis.exe` under Windows.

Other platforms will require you to install Python 3, then use pip to install the required libraries:
```
pip install pygame midiutil
```

Then to start...
```
python interpreter.py
```

## The Main Interface

When Artemis is loaded, you will be presented with a command input screen. From here you can create, load or save programs and a few perform a few other tasks.

Programs may be listed using the **LIST** command:

```
> LIST
10 LET I = 10
20 PRINT I
>
```

A program is executed using the **RUN** command:

```
> RUN
10
>
```

A program may be saved to disk using the **SAVE** command.

```
> SAVE "myfile"
Program written to file
>
```

Note the saved file is *not* a textual copy of the program statements. For that see **EXPORT**.

The program may be re-loaded from disk using the **LOAD** command:

```
> LOAD "myfile"
Program read from file
>
```

To load a text file of program statements, see **IMPORT**.

Files are saved to the user's documents directory in the subdirectory `artemis/HOME/`. See below for more information.

Individual program statements may be deleted by entering their line number only:

```
> 10 PRINT "Hello"
> 20 PRINT "Goodbye"
> LIST
10 PRINT "Hello"
20 PRINT "Goodbye"
> 10
> LIST
20 PRINT "Goodbye"
>
```

The program may be erased entirely from memory using the **NEW** command:

```
> 10 LET I = 10
> LIST
10 LET I = 10
> NEW
> LIST
>
```

The **EXIT** command closes Artemis.

On occasion, it might be necessary to force termination of a program, for example, because it is caught in an infinite loop. This can be achieved by using Ctrl-C to force the program to stop:

```
> 10 PRINT "Hello"
> 20 GOTO 10
> RUN
"Hello"
"Hello"
"Hello"
...
...
<Ctrl-C>
Program terminated
> LIST
10 PRINT "Hello"
20 GOTO 10
>
```

## Disk system and commands

Artemis uses a virtual disk system. By default, the disk HOME is selected. Files will be saved and loaded from the currently selected disk.

The disks contents are stored in the user's documents directory in a folder called `artemis`. There is one directory per disk.

Disk names and file names are limited to 32-characters. There is no size or file limit on disks.

Quotes around filenames are normally optional, unless a file extension is included.

The following disk commands are available:
- **LIST F** - Lists all the files on the current disk.
- **LIST D** - Lists available disks.
- **MOUNT** x - Set the current disk to *x*. If it doesn't exist, create it.
- **UNLINK** x - Delete the file called *x* on the current disk. The file extension must be included.
- **FORMAT** - Delete all files on the current disk.

## Importing and Exporting

Unlike other commands, these allow you to specify a path anywhere on your computer and are not subject to the Disk system rules above. Paths must be in quotes. The default directory is `artemis` in your Documents directory.

**IMPORT** x - Load *x*, a text file of basic instructions as a program. Note that no interpretation is done as such. Instead this file in fed in line by line, aborting on an error. The file extension must be included.

TIP: You can also drag and drop `.bas` files on to the Artemis window to import them.

**EXPORT** x - Export the current program's instructions to text file *x*. This is not a recommended way of saving a program. Uses `.bas` if an extension is not provided.

```
> 10 PRINT "HELLO WORLD"
> EXPORT "myfile.bas"
Program exported to "c:\users\you\Documents\artemis\myfile.bas"
```


# Programming language

## Operators

A limited range of arithmetic expressions are provided. Addition and subtraction have the lowest precedence,
but this can be changed with parentheses.

* **+** - Addition
* **-** - Subtraction
* **\*** - Multiplication
* **/** - Division
* **MOD** (or **%**) - Modulo

```
> 10 PRINT 2 * 3
> 20 PRINT 20 / 10
> 30 PRINT 10 + 10
> 40 PRINT 10 - 10
> 50 PRINT 15 MOD 10
> RUN
6
2
20
0
5
>
```

Additional numerical operations may be performed using numeric functions (see below).

### Statement structure

As per usual in old school BASIC, all program statements must be prefixed with a line number which indicates the order in which the
statements may be executed. There is no renumber command to allow all line numbers to be modified. A statement may be modified or
replaced by re-entering a statement with the same line number:

```
> 10 LET I = 10
> LIST
10 LET I = 10
> 10 LET I = 200
> LIST
10 LET I = 200
>
```

### Variables

Variable types follow the typical BASIC convention. *Simple* variables may contain either strings
or numbers (the latter may be integers or floating point numbers). Likewise *array* variables may contain arrays
of either strings or numbers, but they cannot be mixed in the same array.

Note that all keywords and variable names are case insensitive (and will be converted to upper case internally by the lexical analyser).
String literals will retain their case however. There is no inherent limit on the length of variable names or string literals,
this will be dictated by the limitations of Python. The range of numeric values is also dependent upon the underlying
Python implementation.

Note that variable names may only consist of alphanumeric characters and underscores. However, they
must all begin with an alphabetic character. For example:

* *MY_VAR*
* *MY_VAR6$*
* *VAR77(0, 0)*

are all valid variable names, whereas:

* *5_VAR*
* *_VAR$*
* *66$*

are all invalid.

Numeric variables have no suffix, whereas string variables are always suffixed by '$'. Note that 'I' and 'I$' are
considered to be separate variables. Note that string literals must always be enclosed within double quotes (not single quotes).
Using no quotes will result in a syntax error.

Array variables are defined using the **DIM** statement, which explicitly lists how
many dimensions the array has, and the sizes of those dimensions:

```
> REM DEFINE A THREE DIMENSIONAL NUMERIC ARRAY
> 10 DIM A(3, 3, 3)
```

Note that the index of each dimension always starts at *zero*. So in the above example, valid index values for array *A* will be *0, 1* or *2*
for each dimension. Arrays may have a maximum of three dimensions.

As for simple variables, a string array has its name suffixed by a '$' character, while a numeric array does not carry
a suffix. An attempt to assign a string value to a numeric array or vice versa will generate an error.

Note that the same variable name cannot be used for both an array and a simple variable. For example, the variables
*I$* and *I$(10)* should not be used within the same program, the results may be unpredictable. Also, array variables
with the same name but different *dimensionality* are treated as the same. For example,
using a **DIM** statement to define *I(5)* and then a second **DIM** statement to define *I(5, 5)* will
result in the second definition (the two dimensional array) overwriting the first definition (the one dimensional array).

Array values may be used within any expression, such as in a **PRINT** statement for string values, or in any numerical
expression for number values. However, you must be specific about which array element you are referencing, using the
correct number of in-range indexes. If that particular array value has not yet been assigned, then an error
message will be printed.

```
> 10 DIM MYARRAY(2, 2, 2)
> 20 LET MYARRAY(0, 1, 0) = 56
> 30 PRINT MYARRAY(0, 1, 0)
> RUN
56
> 30 PRINT MYARRAY(0, 0, 0)
> RUN
Empty array value returned in line 30
>
```

As in all implementations of BASIC, there is no garbage collection (not surprising since all variables
have global scope)!

### Program constants

Constants may be defined through the use of the **DATA** statement. They may consist of numeric or string values
and are declared in a comma separated list:

```
> 10 DATA 56, "Hello", 78
```

These values can then later be assigned to variables using the **READ** statement. Note that the type of the value
(string or numeric) must match the type of the variable, otherwise an error message will be triggered. Therefore,
attention should be paid to the relative ordering of constants and variables. Further,
there must be enough constants to fill all of the variables defined in the **READ** statement, or else an
error will be given. This is to ensure that the program is not left in a state where a variable has not been
assigned a value, but nevertheless an attempt to use that variable is made later on in the program.

The constants defined in the **DATA** statement may be consumed using several **READ** statements:

```
> 10 DATA 56, "Hello", 78
> 20 READ FIRSTNUM, STR$
> 30 PRINT FIRSTNUM, " ", STR$
> 40 READ SECONDNUM
> 50 PRINT SECONDNUM
> RUN
56 Hello
78
>
```

The supply of constants may be refreshed by defining more **DATA** statements:

```
> 10 DATA 20
> 20 READ NUM
> 30 PRINT NUM
> 40 DATA 30
> 50 READ NUM
> 60 PRINT NUM
> RUN
20
30
>
```

It is a limitation of this BASIC dialect that it is not possible to assign constants directly to array variables
within a **READ** statement, only simple variables.

### Comments

The **REM** statement is used to indicate a comment, and occupies an entire statement. It has no effect on execution:

```
> 10 REM THIS IS A COMMENT
```

Note that comments will be automatically normalised to upper case.

### Stopping a program

The **STOP** statement may be used to cease program execution. The command **END** has the same effect.

```
> 10 PRINT "one"
> 20 STOP
> 30 PRINT "two"
> RUN
one
>
```

A program will automatically cease execution when it reaches the final statement, so a **STOP** may not be necessary. However
a **STOP** *will* be required if subroutines have been defined at the end of the program, otherwise execution will continue
through to those subroutines without a corresponding subroutine call. This will cause an error when the **RETURN**
statement is processed and the interpreter attempts to return control back to the caller.

### Assignment

Assignment may be made to numeric simple variables (which can contain either integers or floating point numbers) and string simple variables
(string variables are distinguished by their dollar suffix). The interpreter will enforce this division between the two types:

```
> 10 LET I = 10
> 20 LET I$ = "Hello"
```

The **LET** keyword is also optional:

```
> 10 I = 10
```

Array variables may also have values assigned to them. The indexes can be derived from numeric
expressions:

```
> 10 DIM NUMS(3, 3)
> 20 DIM STRS$(3, 3)
> 30 LET INDEX = 0
> 40 LET NUMS(INDEX, INDEX) = 55
> 50 LET STRS$(INDEX, INDEX) = "hello"
```

Attempts to assign the wrong type (number or string) to a numeric or string array, attempts to assign a value to an array by specifying the wrong number
of dimensions, and attempts to assign to an array using an out of range index, will all result in an error.

### Printing to screen

The **PRINT** statement is used to print to the screen:

```
> 10 PRINT 2 * 4
> RUN
8
> 10 PRINT "Hello"
> RUN
Hello
>
```

Multiple items may be printed by providing a comma separated list. The items in the list will be printed immediately after one
another, so spaces must be inserted if these are required:

```
> 10 PRINT 345, " hello ", 678
> RUN
345 hello 678
>
```

A blank line may be printed by using the **PRINT** statement without arguments:

```
> 10 PRINT "Here is a blank line:"
> 20 PRINT
> 30 PRINT "There it was"
> RUN
Here is a blank line:

There it was
>
```

If the print command ends with a comma, a new-line will not be automatically added.

```
> 10 PRINT "Hello ",
> 20 PRINT "world!"
> RUN
Hello world!
```

### Additional Screen Commands

* **COL** x[, y] - Sets the text color to *x* and optionally the background color to *y*.
* **CLS** - Clears the screen. This command can also be used in the main interface.
* **BORDER** x - Set the screen's border color to *x*
* **CURSOR** x, y - Move the cursor to position *x*, *y*
* **INK** x, red, green, blue - Sets the color of palette entry *x*. *red*,*green* and *blue* can be from 0 to 4, giving a total of 125 possible colors.
* **PRINTW** t$, x1, y1, x2, y2[, wrap] - Print text *t$* to a virtual "Window" on-screen. The window's top-left position is defined by *x1* and *y1*, and it's bottom-right by *x2* and *y2*. If *wrap* is non-zero, *t$* will be wrapped cleanly - avoiding line-breaks in the middle of words. (This is the default behaviour.) If *t$* is too long, it will be cropped, if it is too short it will be padded with spaces.
* **SYMBOL** x, y$ - Redefine the bitmap of the character with the code *x*. *y$* is a string that represents the new bitmap. Each character in the string represents one pixel starting at the top-left. Use a space for the background and any other character for the foreground. If *y$* is an empty string, the character will be reset to the default.
* **SYMBOL** x, b1[, b2] ... [, b8] - Alternate syntax for above, more like classic BASIC variants. Provide 1 - 8 integers from 0 - 255. Each integer's binary value defines one row of pixels, top to bottom. Missing rows are considered empty.

Tip: if you change the symbol for character 239, you will also change Artemis' icon.

### Screen Modes

You can change the screen mode with the **MODE** x command. Calling **MODE** will also clear the screen. Different modes offer compromises between number of characters and colors on the screen.

e.g. `MODE 2` to change to mode 2.

Available modes:
Number | Characters | Colors | Pixel shape | Notes
-------|------------|--------|-------------|------
0      | 20 x 25    | 16     | 2 x 1       |
1      | 40 x 25    | 8      | 1 x 1       | Default
2      | 80 x 25    | 4      | 1 x 2       |
3      | 80 x 50    | 2      | 1 x 1       |
4      | 40 x 50    | 4      | 2 x 1       |
5      | 24 x 15    | 16     | 1 x 1       | Compromise version of mode 0
6      | 16 x 10    | 32     | 1 x 1       |

#### Direct Screen Access Commands

* **PEEKS**(x, mode) - Inspect screen cell in position *x*. Where *0* is the top-left of the screen. Return value depends on *mode*. *0*: The code of the character. *1*: The foreground color. *2*: The background color.
* **POKES** x, mode, val - Change the values of screen cell. *x* and *mode* use the same values as **PEEK**, above. *val* is the value that will be set. Note that any changes made won't be visible until the screen is next drawn.
* **DUMPS** x$ - Dump the screen to a file with name *x$*. Do not provide an extension, `.sda` will be added automatically.
* **LOADS** x$ - Load screen data from a file with name *x$*. `.sda` will be added automatically. Like **POKES** the change won't be visible until the screen is next drawn.
* **REFRESH** - Force the screen to draw.
* **REFRESH WAIT** - Prevent the screen from drawing until the next **REFRESH** or user input command.

Tip: A tool is provided to convert playscii (http://vectorpoem.com/playscii/) `.psci` files to `.sda` files, along with files to allow the tool to use the Artemis character set and palette. See tools/playscii

### Unconditional branching

Like it or loath it, the **GOTO** statement is an integral part of BASIC, and is used to transfer control to the statement with the specified line number:

```
> 10 PRINT "Hello"
> 20 GOTO 10
> RUN
Hello
Hello
Hello
...
```

### Subroutine calls

The **GOSUB** statement is used to generate a subroutine call. Control is passed back to the program at the
next statement after the call by a **RETURN** statement at the end of the subroutine:

```
> 10 GOSUB 100
> 20 PRINT "This happens after the subroutine"
> 30 STOP
> 100 REM HERE IS THE SUBROUTINE
> 110 PRINT "This happens in the subroutine"
> 120 RETURN
> RUN
This happens in the subroutine
This happens after the subroutine
>
```

Note that without use of the **STOP** statement, execution will run past the last statement
of the main program (line 30) and will re-execute the subroutine again (at line 100).

Subroutines may be nested, that is, a subroutine call may be made within another subroutine.

A subroutine may also be called using the **ON-GOSUB** statement (see Conditional branching
below).

### Loops

Bounded loops are achieved through the use of **FOR-NEXT** statements. The loop is controlled by a numeric
loop variable that is incremented or decremented from a start value to an end value. The loop terminates when
the loop variable reaches the end value. The loop variable must also be specified in the **NEXT**
statement at the end of the loop.

```
> 10 FOR I = 1 TO 3
> 20 PRINT "hello"
> 30 NEXT I
> RUN
hello
hello
hello
>
```

Loops may be nested within one another.

The **STEP** statement allows the loop variable to be incremented or decremented by
a specified amount. For example, to count down from 5 in steps of -1:

```
> 10 FOR I = 5 TO 1 STEP -1
> 20 PRINT I
> 30 NEXT I
> RUN
5
4
3
2
1
>
```

Note that the start value, end value and step value need not be integers, but can be floating
point numbers as well. If the loop variable was previously assigned in the program, its value will
be replaced by the start value, it will not be evaluated.

### Conditional branching

Conditional branches are implemented using the **IF-THEN-ELSE** statement. The expression is evaluated and the appropriate jump
made depending upon the result of the evaluation.

```
> 10 REM PRINT THE GREATEST NUMBER
> 20 LET I = 10
> 30 LET J = 20
> 40 IF I > J THEN 50 ELSE 70
> 50 PRINT I
> 60 GOTO 80
> 70 PRINT J
> 80 REM FINISHED
> RUN
20
>
```

Note that the **ELSE** clause is optional and may be omitted. In this case, the **THEN** branch is taken if the
expression evaluates to true, otherwise the following statement is executed.

You can optionally give the **GOTO** keyword before your line numbers. This is for compatibility with other BASIC dialects. e.g. `40 IF I > J THEN GOTO 50 ELSE GOTO 70`

It is also possible to call a subroutine depending upon the result of a conditional expression
using the **ON-GOSUB** statement. If the expression evaluates to true, then the subroutine is
called, otherwise execution continues to the next statement without making the call:

```
> 10 LET I = 10
> 20 LET J = 5
> 30 ON I > J GOSUB 100
> 40 STOP
> 100 REM THE SUBROUTINE
> 110 PRINT "I is greater than J"
> 120 RETURN
> RUN
I is greater than J
>
```

Allowable relational operators are:

* '=' (equal, note that in BASIC the same operator is used for assignment)
* '<' (less than)
* '>' (greater than)
* '<=' (less than or equal)
* '>=' (greater than or equal)
* '<>' / '!=' (not equal)

The logical operators **AND** and **OR** are also provided to allow you to join two or more expressions. The **NOT** operator can also be given before an expression.

*=* and *<>* can also be considered logical operators. However, unlike **AND** or **OR** they can't be used to join more than two expressions.

| Inputs |       | *AND* | *OR*  | *=*   | *<>* / *!=* |
|--------|-------|-------|-------|-------|-------------|
| FALSE  | FALSE | FALSE | FALSE | TRUE  | FALSE       |
| TRUE   | FALSE | FALSE | TRUE  | FALSE | TRUE        |
| TRUE   | TRUE  | TRUE  | TRUE  | TRUE  | FALSE       |

| Input | NOT   |
|-------|-------|
| TRUE  | FALSE |
| FALSE | TRUE  |

Example:

```
> 10 a = 10
> 20 b = 20
> 30 IF NOT a > b AND b = 20 OR a >= 5 THEN 60
> 40 PRINT "Test failed!"
> 50 STOP
> 60 PRINT "Test passed!"
> RUN
Test passed!
```

Expressions can be inside brackets to change the order of evaluation. Compare the output when line 30 is changed:

```
> 30 IF NOT a > b AND (b = 20 OR a >= 5) THEN 60
> RUN
Test failed!
```

### Ternary Functions

As an alternative to branching, Ternary functions are provided.

* **IFF**(x, y, z) - Evaluates *x* and returns *y* if true, otherwise returns *z*. *y* and *z* are expected to be numeric.
* **IF$**(x, y$, z$) - As above, but *y$* and *z$* are expected to be strings.

```
> 10 LET I = 10
> 20 LET J = 5
> 30 PRINT IF$(I > J, "I is greater than J", "I is not greater than J")
> 40 K = IFF(I > J, 20, 30)
> 50 PRINT K
> RUN
I is greater than J
20
```

### User input

The **INPUT** statement is used to solicit input from the user:

```
> 10 INPUT A
> 20 PRINT A
> RUN
? 22
22
>
```

The default input prompt of '? ' may be changed by inserting a prompt string, which must be terminated
by a colon, thus:

```
> 10 INPUT "Input a number - ": A
> 20 PRINT A
> RUN
Input a number - 22
22
>
```

Multiple items may be input by supplying a comma separated list. Input variables will be assigned
to as many input values as supplied at run time. If there are more input values supplied than input
variables, excess commas will be left in place. Conversely, if not enough input values are
supplied, then the excess input variables will not be initialised (and will trigger an error if
an attempt is made to evaluate those variables later in the program).

Further, numeric input values must be valid numbers (integers or floating point).

```
> 10 INPUT "Num, Str, Num: ": A, B$, C
> 20 PRINT A, B$, C
> RUN
Num, Str, Num: 22, hello!, 33
22 hello!33
>
```

A mismatch between the input value and input variable type will trigger an error.

It is a limitation of this BASIC dialect that it is not possible to assign constants directly to array variables
within an **INPUT** statement, only simple variables.

#### Other User Input functions

- **WAITKEY** [x] - Pauses execution until the user presses a key. If variable *x* is provided, it will be set to the key-code of the pressed key.
- **KEY** x - As **WAITKEY**, but only waits one tick (see timing below). If no key is pressed, gives -1

### Numeric functions

Selected numeric functions are provided, and may be used with any numeric expression. For example,
the square root function, **SQR**, can be applied expressions consisting of both literals and variables:

```
> 10 LET I = 6
> 20 PRINT SQR(I - 2)
> RUN
2.0
>
```

Allowable numeric functions are:

* **ABS**(x) - Calculates the absolute value of *x*

* **ATN**(x) - Calculates the arctangent of *x*

* **COS**(x) - Calculates the cosine of *x*, where *x* is an angle in radians

* **EXP**(x) - Calculates the exponential of *x*, *e^x* where *e*=2.718281828

* **INT**(x) - Rounds down numbers to the lowest whole integer less than or equal to *x*

* **LOG**(x) - Calculates the natural logarithm of *x*

* **MAX**(x, y[, z]...) - Returns the highest value from a list of expressions

* **MIN**(x, y[, z]...) - Returns the lowest value from a list of expressions

```
> 10 PRINT MAX(-2, 0, 1.5, 4)
> 20 PRINT MIN(-2, 0, 1.5, 4)
> RUN
> 4
> -2
```

* **POW**(x, y) - Calculates *x* to the power *y*

* **RND** - Generates a pseudo random number N, where *0 <= N < 1*. Can be
reset using the **RANDOMIZE** instruction with an optional seed value: e.g.

```
> 10 RANDOMIZE 100
> 20 PRINT RND
> RUN
0.1456692551041303
>
```

Random integers can be generated by combining **RND** and **INT**: e.g.

```
> 10 PRINT INT(RND * 6) + 1
> RUN
3
> RUN
6
>
```

Seeds may not produce the same result on another platform.

* **ROUND**(x) - Rounds number to the nearest integer.

* **SIN**(x) - Calculates the sine of *x*, where *x* is an angle in radians

* **SQR**(x) - Calculates the square root of *x*

* **TAN**(x) - Calculates the tangent of *x*, where *x* is an angle in radians

### String functions

Some functions are provided to help you manipulate strings. Functions that return a string
have a '$' suffix like string variables.

Note that unlike some other BASIC variants, string positions start at *0*.

The functions are:

* **ASC**(x$) - Returns the character code for *x$*. *x$* is expected to be a single character.
Note that despite the name, this function can return codes outside the ASCII range.
* **CHR$**(x) - Returns the character specified by character code *x*.
* **INSTR**(x$, y$[, start[, end]]) - Returns position of *y$* inside *x$*, optionally start searching
at position *start* and end at *end*. Returns -1 if no match found.
* **LEN**(x$) - Returns the length of *x$*.
* **LOWER$**(x$) - Returns a lower-case version of *x$*.
* **MID$**(x$, y[, z]) - Returns part of *x$* starting at position *y* and ending at *z*. *z* can
be omitted to get the rest of the string.  If *y* or *z* are negative, the position is counted
backwards from the end of the string.
* **STR$**(x) - Returns a string representation of numeric value *x*.
* **UPPER$**(x$) - Returns an upper-case version of *x$*
* **VAL**(x$) - Attempts to convert *x$* to a numeric value. If *x$* is not numeric, returns 0.

Examples for **ASC**, **CHR$** and **STR$**
```
> 10 I = 65
> 20 J$ = CHR$(I) + " - " + STR$(I)
> 30 PRINT J$
> 40 PRINT ASC("Z")
RUN
A - 65
90
```

### Saving and Loading from disk

Variables can be saved and retrieved from disk using a similar method to the **DATA** and **READ** commands. This can be used for example for savegames, or referencing pre-created data you don't wish to define in code.

Datafiles are simply json text files, allowing easy creation outside of artemis.

- **FILEOUT** fn$, mode, value[, value$]... - Write a file with a list of values
    - *fn$* is the file you wish to write. It will be automatically given the `.dfa` extension. Filenames are case insensitive and will always been written to the local filesystem UPPERCASE
    - *mode* is the file overwrite mode. *0* replaces an existing file, *1* appends to an existing file
    - A list of values you want to write to the file. These can be either numeric or string expressions.
- **FILEIN** fn$[, start[, end]] - Retrieve a list of values from a file and store them
    - *fn$* is as above. Don't include the extension.
    - *start* the position of the first value to read. If omitted 0 is used.
    - *end* the position of the last value to read. If omitted, the rest of the file is read.
- **FILEREAD** variable[, variable$]... - Read variables retrieved by **FILEIN**. This command works exactly the same way as the **READ** command.

### Music

Commands are provided to play very basic music.

- **MUSICPLAY** note$[, mode] - Play some music
    - *note$* a string representing the music to play. This is a subset of MML format and is described below.
    - *mode* the play mode. *0*: Music will play in the background. *1*: Execution will halt until music playback is complete. *2*: As 0, but the music loops until **MUSICSTOP** is called.
- **MUSICSTOP** - Stop any currently playing music.

Music is actually played via pygame which uses your system's midi. It may sound different depending on platform.

#### MML format
- `cdefgab` - Play the given note. Appending `+` or `#` makes the note sharp, `-` is makes it flat. The length of the note can be altered by appending a number. The number will be the fraction of the whole note. Finally a `.` can be appended to make a dotted note. e.g. `c#2` plays a c sharp for 1/2 note.
- `p`/`r` - A pause/rest. Length works as above.
- `o[N]` - Sets the octave to *N*. Default octave is 5. Octaves 0 - 9 are provided.
- `>` - Step up one octave
- `<` - Step down one octave
- `l[N]` - Set the default note length to 1/*N*. Default is 4, or quarter note.
- `t[N]` - Set the tempo to *N* beats per minute. Default is 120.

### Timing

* **WAIT** x - Pauses execution for *x* seconds. *x* can include a decimal point to allow sub-second waiting. Note: this command is not particularly accurate and you should expect the actual wait time to be +/-0.04 seconds at the least.
* **SYSTIME** - Return the time the system has been active in seconds. This value includes fractions of a second.

### A note about system timing

The screen can be drawn at most 30 times a second. This is a 'tick'. The **PRINT**, **BORDER**, **KEY** and **CLS** commands cause a tick, unless **REFRESH WAIT** is called first. Executing 10,000 lines of code since the last tick will also cause a tick.

JiBASIC is not particularly optimised. Your program may get far less than 30 ticks/second. You should NOT assume you can draw the screen in a timely manner.

Commands that halt execution of the program such as **INPUT** and **WAIT** will cause many ticks before control is handed back to the program.

## Example programs

TODO

## License

Artemis / JiBASIC is made available under the GNU General Public License, version 3.0 or later (GPL-3.0-or-later).
