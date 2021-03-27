import yaml, json, os
from shutil import copy2

outpath = 'build/maze/'

if not os.path.exists(outpath):
    os.makedirs(outpath)

stream = open('data.yml', 'r')
y = yaml.load(stream)
out = []
itemlist = []

def lu(path, default):
    try:
        t = y
        for i in path:
            t = t[i]
        return t
    except KeyError:
        return default

def add(path, default, upper = False, lower = False):
    global out
    o = lu(path, default)
    if upper: o = o.capitalize()
    if lower: o = o.lower()
    out.append(o)

def item(path):
    global out, itemlist
    name = lu(path, False)
    if not name or name == -1:
        out.append(-1)
    else:
        name = name.capitalize()
        if name not in itemlist:
            itemlist.append(name)
        out.append(itemlist.index(name))


# Rooms
for i in y:
    out = []
    add([i,'name'], i)
    add([i,'desc'], "")
    item([i,'item_give'])
    add([i,'item_desc'], "")
    item([i,'puzzle','item'])
    add([i,'puzzle','use_desc'], "")
    add([i,'puzzle','new_desc'], "")
    item([i,'puzzle','reward'])
    for d in list("nesw"):
        add([i,'exits',d,'load'], "", lower=True)
        add([i,'exits',d,'desc'], "")
        item([i,'exits',d,'prereq'])

    # Import image
    try:
        with open('miniscreens/'+y[i]['img']) as json_file:
            data = json.load(json_file)
        for c in data['frames'][0]['layers'][0]['tiles']:
            out.append(c['char'])
            out.append(c['fg']-1)
            out.append(c['bg']-1)
    except:
        out += [0]*5*5*3

    with open(outpath+i.lower()+".dfa", 'w') as f:
        f.write(json.dumps(out, separators=(',', ':')))

# Items
itemlist = [len(itemlist)] + itemlist
with open(outpath+"items.dfa", 'w') as f:
    f.write(json.dumps(itemlist, separators=(',', ':')))

# Other files
copy2('ui.sda', outpath)
copy2('autorun.bas', outpath)
