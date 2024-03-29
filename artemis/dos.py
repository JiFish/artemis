# Artemis - DOS: Disk OrganiSing
#
# A collection of functions dealing with writing to the disk.
# Tries to limit operations to inside the ~/Documents/artemis dir for safety.
#
# Filenames are limited to 32 UPPERCASE alpha-numeric characters, plus extension.
#

import os
import json
import zipfile
from shutil import copy

__HOME = os.path.expanduser('~/Documents/artemis')
__MAX_NAME_SIZE = 32
__DEFAULT_DISK = "home"
__CURRENT_DISK = __DEFAULT_DISK
__EXAMPLES_PATH = 'examples/'
__MAZE_PATH = 'maze/'

def change_disk(diskname):
    global __CURRENT_DISK
    test_filename(diskname)
    path = __HOME+"/"+diskname
    if os.path.isfile(path):
        raise OSError("Given diskname is a file.")
    if not os.path.exists(path):
        os.makedirs(path)
    os.chdir(path)
    __CURRENT_DISK = diskname

def disk_exists(diskname):
    return os.path.isdir(__HOME+"/"+diskname)

def get_valid_files():
    files = []
    for entry in os.scandir('.'):
        if not entry.is_file(): continue
        fn, ext = os.path.splitext(entry.name)
        if len(fn) > __MAX_NAME_SIZE: continue
        if not fn.isalnum(): continue

        # If we get this far, we recongise the file
        size = os.path.getsize(entry.name)
        files.append({'name':fn+ext,'size':size})
    return files

# Hmm, dangerous
def format_disk():
    for f in get_valid_files():
        os.remove(f['name'])

def list_disk(ext = ""):
    ext = ext.lower()
    filelist = []
    filelist.append('Listing contents of "'+__CURRENT_DISK+'".')
    filelist.append('')
    tsize = 0
    fcount = 0
    for f in get_valid_files():
        if not f['name'].lower().endswith(ext):
            continue
        fcount += 1
        tsize += f['size']
        size = "{:,} B".format(f['size'])
        filelist.append(f['name'].ljust(30)+size.rjust(9))
    filelist.append("")
    filelist.append("{:,} File{}, {:,} Bytes in total.".format(
                    fcount, 's' if fcount != 1 else '', tsize))
    return filelist

def list_all_disks():
    filelist = []
    filelist.append('Listing diskettes.')
    filelist.append('')
    fcount = 0
    for entry in os.scandir(__HOME):
        if not entry.is_dir(): continue
        fn = entry.name
        if len(fn) > __MAX_NAME_SIZE: continue
        if not fn.isalnum(): continue

        # If we get this far, we recongise the disk
        fcount += 1
        filelist.append(fn)
    filelist.append("")
    filelist.append("{:,} Diskette{}.".format(
                    fcount, 's' if fcount != 1 else ''))
    return filelist

def file_get_contents(filename):
    test_filename(filename)
    if not os.path.isfile(filename):
        raise OSError("{}: File not found".format(filename))
    with open(filename, 'r', encoding="latin-1") as f:
        return f.read()

def file_put_contents(filename, data):
    test_filename(filename)
    with open(filename, 'w', encoding="latin-1") as f:
        f.write(data)

def file_remove(filename):
    test_filename(filename)
    if not os.path.isfile(filename):
        raise OSError("File not found")
    os.remove(filename)

# Tester userinputted filename, INCLUDING extension
def test_filename(filename):
    if filename.count(".") > 1:
        raise OSError("Invalid filename")
    if not filename.replace(".","").isalnum():
        raise OSError("Invalid filename")

def read_data_file(filename, ext = "dfa"):
    return json.loads(file_get_contents(filename+"."+ext))

def write_data_file(data, filename, ext = "dfa"):
    file_put_contents(filename+"."+ext,
                      json.dumps(data, separators=(',', ':')))

def append_data_file(data, filename, ext = "dfa"):
    if os.path.isfile(filename+"."+ext):
        data = read_data_file(filename, ext) + data
    write_data_file(data, filename, ext)

def disk_has_autorun():
    return os.path.isfile("autorun.bas")

def disk_export(fn = None):
    if fn == None: fn = __HOME+'/'+__CURRENT_DISK+'.adi'
    with zipfile.ZipFile(fn, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
        chdir_disk() # Switch to the current disk
        for f in get_valid_files():
            zipf.write(f['name'])

def disk_import(fn):
    if not os.path.isfile(fn):
        raise OSError("File not found")
    diskname = os.path.basename(fn)
    diskname = os.path.splitext(diskname)[0]
    change_disk(diskname)
    try:
        with zipfile.ZipFile(fn, 'r') as zipf:
            zipf.extractall()
    except:
        raise Exception("File is invalid.")

def get_current_disk():
    return __CURRENT_DISK

def chdir_home():
    os.chdir(__HOME)

def chdir_disk():
    os.chdir(__HOME+"/"+__CURRENT_DISK)

# Import examples disk
if not os.path.exists(__HOME+"/examples") and os.path.exists(__EXAMPLES_PATH):
    os.makedirs(__HOME+"/examples")
    for entry in os.scandir(__EXAMPLES_PATH):
        copy(__EXAMPLES_PATH+"/"+entry.name, __HOME+"/examples")

# Import MAZE disk
if not os.path.exists(__HOME+"/maze") and os.path.exists(__MAZE_PATH):
    os.makedirs(__HOME+"/maze")
    for entry in os.scandir(__MAZE_PATH):
        copy(__MAZE_PATH+"/"+entry.name, __HOME+"/maze")

# Switch to, and create, HOME disk
change_disk(__CURRENT_DISK)
