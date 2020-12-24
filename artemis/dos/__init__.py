# Artemis - DOS: Disk OrganiSing
#
# A collection of functions dealing with writing to the disk.
# Tries to limit operations to inside the ~/Documents/artemis dir for safety.
#
# Filenames are limited to 32 UPPERCASE alpha-numeric characters, plus extension.
#

import os
import json
import pickle
import zlib
from shutil import copy

__HOME = os.path.expanduser('~/Documents/artemis')
#_disc_capacity = 360 * 1024
__MAX_NAME_SIZE = 32
__DEFAULT_DISK = "HOME"
__CURRENT_DISK = __DEFAULT_DISK
__EXAMPLES_PATH = 'examples/'

def change_disk(diskname):
    global __CURRENT_DISK
    __CURRENT_DISK = clean_filename(diskname)
    if not os.path.exists(__HOME+"/"+__CURRENT_DISK):
        os.makedirs(__HOME+"/"+__CURRENT_DISK)
    os.chdir(__HOME+"/"+__CURRENT_DISK)

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

def list_disk():
    filelist = []
    filelist.append('Listing contents of "'+__CURRENT_DISK+'".')
    filelist.append('')
    tsize = 0
    fcount = 0
    for f in get_valid_files():
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

def file_get_contents(filename, ext = None):
    filename = clean_filename(filename)
    filename += "." + ext
    if not os.path.isfile(filename):
        raise OSError("File not found")
    with open(filename) as f:
        return f.read()

def file_put_contents(filename, ext, data):
    filename = clean_filename(filename)
    with open(filename + "." + ext, 'w') as f:
        f.write(data)

def file_remove(filename):
    test_filename(filename)
    if not os.path.isfile(filename):
        raise OSError("File not found")
    os.remove(filename)

def file_unpickle(filename, ext):
    filename = clean_filename(filename)
    filename += "." + ext
    if not os.path.isfile(filename):
        raise OSError("File not found")
    with open(filename, 'rb') as infile:
        obj = infile.read()
        infile.close()
    try:
        obj = zlib.decompress(obj)
    except: pass # Allow loading of PyBasic files... for now
    obj = pickle.loads(obj)
    return obj

def file_pickle(filename, ext, obj):
    filename = clean_filename(filename)
    obj = pickle.dumps(obj)
    obj = zlib.compress(obj)
    with open(filename + "." + ext, 'wb') as outfile:
        outfile.write(obj)
        outfile.close()

# Tester userinputted filename, INCLUDING extension
def test_filename(filename):
    if filename.count(".") > 1:
        raise OSError("Invalid filename")
    if not filename.replace(".","").isalnum():
        raise OSError("Invalid filename")

def clean_filename(filename):
    if not filename.isalnum() or len(filename) > __MAX_NAME_SIZE:
        raise OSError("Invalid filename")
    return filename.upper()

def read_data_file(filename, ext = "dfa"):
    return json.loads(file_get_contents(filename, ext))

def write_data_file(data, filename, ext = "dfa"):
    file_put_contents(filename, ext,
                      json.dumps(data, separators=(',', ':')))

def append_data_file(data, filename, ext = "dfa"):
    if os.path.isfile(filename+"."+ext):
        data = read_data_file(filename, ext) + data
    write_data_file(data, filename, ext)

# Update examples disk
if not os.path.exists(__HOME+"/EXAMPLES"):
    os.makedirs(__HOME+"/EXAMPLES")
if os.path.exists(__EXAMPLES_PATH):
    for entry in os.scandir(__EXAMPLES_PATH):
        copy(__EXAMPLES_PATH+"/"+entry.name, __HOME+"/EXAMPLES")

# Switch to, and create, HOME disk
change_disk(__CURRENT_DISK)
