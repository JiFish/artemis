* TOC
{:toc}

# The Main Interface

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

Actually writing a large program in this interface is not recommended. See the **IMPORT** command below to load a text file of program statements.

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

If you're writing a complex program, you'll probably want to use an external editor. See "Importing and Exporting" below for help on getting externally written code in to Artemis.

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

## Screen commands

A couple of screen commands can be typed in to the main interface.

- **CLS** - Clear the screen.
- **RSTS** - Resets the screen. Some programs may redefine colors, text mode and symbols. This command resets everything back to normal.

## Disk system and commands

Artemis uses a virtual disk system. By default, the disk HOME is selected. Files will be saved and loaded from the currently selected disk. Disk names and file names are limited to 32-characters. There are no directories.

The disk's contents are stored in your documents directory in a folder called `artemis`. There is one directory per disk.

The following disk commands are available:

- **LIST F** - Lists all the files on the current disk.
- **LIST S** - Lists all saved programs on the current disk.
- **LIST D** - Lists available disks.
- **MOUNT** x - Set the current disk to *x*. If it doesn't exist, you will be asked if you want to create it.
- **UNLINK** x - Delete the file called *x* on the current disk. The file extension must be included.
- **FORMAT** - Delete all files on the current disk.

## Importing and Exporting

Unlike other commands, these allow you to specify a path anywhere on your computer and are not subject to the Disk system rules above. Paths must be in quotes. The default directory is `artemis` in your Documents directory.

**IMPORT** x - Load *x*, a text file of basic instructions as a program. Note that no interpretation is done as such. Instead this file in fed in line by line, aborting on an error. The file extension must be included.

**TIP: You can also drag and drop `.bas` files on to the Artemis window to import them.**

**EXPORT** x - Export the current program's instructions to text file *x*. This is not a recommended way of saving a program. Uses `.bas` if an extension is not provided.

```
> 10 PRINT "HELLO WORLD"
> EXPORT "myfile.bas"
Program exported to "c:\users\you\Documents\artemis\myfile.bas"
```

**DSKIMPORT** x - Imports *x*, an `.dia` Artemis disk file. This will overwrite an existing disk with the same name if one exists. Once the disk has been imported, it is automatically mounted.

**DSKEXPORT** [x] - Exports the currently selected disk to an file called *x*. This is intended method for sharing your software. All filenames recognised by Artemis will be included. This means no subdirectories. If *x* is not provided, the current disk's name will be used. Uses `.dia` if an extension is not provided.

TIP: `.dia` files are simply zip files, allowing easy creation outside Artemis. **You can also drag and drop `.dia` and `.zip` files on to the Artemis window to import them.**
