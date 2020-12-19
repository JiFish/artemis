# Convert psci file to sda file

import json, sys

if (len(sys.argv) < 2):
    print("Example usage: ")
    print(" {} screen.psci > screen.sda".format(sys.argv[0]))
    sys.exit()

with open(sys.argv[1]) as f:
    sf = f.read()

sf = json.loads(sf)

output = []
for i in sf['frames'][0]['layers'][0]['tiles']:
    output.append([i['char'],i['fg']-1,i['bg']-1])

print(json.dumps(output, separators=(',', ':')))
