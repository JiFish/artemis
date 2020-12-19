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

_home = os.path.expanduser('~/Documents/artemis')
#_disc_capacity = 360 * 1024
_max_name_size = 32
_default_disk = "HOME"
_current_disk = _default_disk
_examples_path = os.path.dirname(os.path.realpath(__file__))+'/../../examples'

# Update examples disk
if not os.path.exists(_home+"/EXAMPLES"):
    os.makedirs(_home+"/EXAMPLES")
for entry in os.scandir(_examples_path):
    copy(_examples_path+"/"+entry.name, _home+"/EXAMPLES")

def change_disk(diskname):
    global _current_disk
    _current_disk = clean_filename(diskname)
    if not os.path.exists(_home+"/"+_current_disk):
        os.makedirs(_home+"/"+_current_disk)
    os.chdir(_home+"/"+_current_disk)

def get_valid_files():
    files = []
    for entry in os.scandir('.'):
        if not entry.is_file(): continue
        fn, ext = os.path.splitext(entry.name)
        if len(fn) > _max_name_size: continue
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
    filelist.append('Listing contents of "'+_current_disk+'".')
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
    for entry in os.scandir(_home):
        if not entry.is_dir(): continue
        fn = entry.name
        if len(fn) > _max_name_size: continue
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
    if not filename.isalnum() or len(filename) > _max_name_size:
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

change_disk(_current_disk)
