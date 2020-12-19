# Artemis - TASS: Totally Awful Sound System
# (or: The Artemis Sound System)
#
# Music stuff, written by a programmer who knows next to nothing about music.
#
# A temporary midi file is constructed using midiutil and then played via pygame.
# One instrument (81 - Synth Lead Square), one voice. Pretty simplistic.
#
# If anything, it sounds _too_ good. An actual square-wave generator would be
# prefered, but this is much faster.
#

import pygame, os, tempfile
import artemis
import midiutil

midi_build = None
position = 0
_c_oct = 5
_c_len = 0.25
notes_unordered = {'C':0,  'C#':1, 'C+':1,  'D-':1,  'D':2,   'D#':3, 'D+':3,   'E-': 3,
                   'E':4,  'F':5,  'F#':6,  'F+':6,  'G-':6,  'G':7,  'G#':8,   'G+':8,
                   'A-':8, 'A':9,  'A#':10, 'A+':10, 'B-':10, 'B':11, 'P':-999, 'R':-999}

# Since python 3.6 dicts remember insert order
# So we can sort just once here
notes = {}
for k in sorted(notes_unordered, key=len, reverse=True):
    notes[k] = notes_unordered[k]

def pull_number(s):
    numbstr = ""
    while len(s)>0 and s[0].isdigit():
        numbstr += s[0]
        s = s[1:]
    if numbstr == "": return -1, s
    return int(numbstr), s

def process_string(s):
    global _c_oct, _c_len
    if (midi_build == None): new_song()
    # Remove all whitespace
    s = ''.join(s.split()).upper()
    while len(s) > 0:
        starting_len = len(s)
        # notes
        foundnote = False
        for note in notes:
            if s.startswith(note):
                # Remove from string
                s = s[len(note):]
                # Add to song
                # Look for length
                notelen, s = pull_number(s)
                if notelen < 0:
                    notelen = _c_len
                else:
                    notelen = 4/notelen
                # Look for 'dot'
                if len(s)>0 and s[0]=='.':
                    notelen *= 1.5
                    s = s[1:]
                # Get pitch
                pitch = ((_c_oct)*12)+notes[note]
                #print("addnote"+str(pitch)+","+str(notelen)+" oct:"+str(_c_oct))
                add_note(pitch, notelen)
                foundnote = True
                break
        if foundnote: continue

        # Octaves
        if s[0] == '>':
            _c_oct = min(9,_c_oct+1)
            s = s[1:]
        elif s[0] == '<':
            _c_oct = max(0,_c_oct-1)
            s = s[1:]
        elif s[0] == 'O':
            s = s[1:]
            oct, s = pull_number(s)
            if oct < 0 or oct > 9:
                raise ValueError("Invalid octave in music string "+str(oct))
            _c_oct = oct
        # Tempo
        elif s[0] == "T":
            s = s[1:]
            tempo, s = pull_number(s)
            if tempo < 1:
                raise ValueError("Invalid Tempo")
            add_tempo(tempo)
            #print("tempo"+str(position)+","+str(tempo))
        # Default length
        elif s[0] == "L":
            s = s[1:]
            notelen, s = pull_number(s)
            if notelen < 1:
                raise ValueError("Invalid Length")
            _c_len =4/notelen

        # Check we processed something
        if starting_len == len(s):
            #print(s)
            raise ValueError("Invalid music string")



def new_song():
    global midi_file, midi_build, position, _c_oct
    midi_build = midiutil.MIDIFile(numTracks=1, file_format=1)
    midi_build.addTempo(0,0,120)
    midi_build.addProgramChange(0, 0, 0, 80)
    position = 0
    _c_oct = 5
    _c_len = 0.25

def wait_for_song():
    try:
        while pygame.mixer.music.get_busy():
            artemis.tick()
    finally:
        pygame.mixer.music.stop()

def add_tempo(tempo):
    if (midi_build == None): new_song()
    midi_build.addTempo(0, position, tempo)

def add_note(pitch, length = 1, volume = 127):
    if pitch < 0: return add_pause(length)
    if pitch > 131:
        raise ValueError("Pitch too high!")
    global position, midi_build
    if (midi_build == None): new_song()
    midi_build.addNote(0, 0, pitch, position, length, volume)
    position += length

def add_pause(length):
    global position, midi_build
    if (midi_build == None): new_song()
    position += length

def play(loops):
    global position, midi_build
    if (midi_build == None): new_song()
    midi_file = tempfile.TemporaryFile()
    midi_build.writeFile(midi_file)
    midi_build = None
    position = 0
    midi_file.seek(0)
    pygame.mixer.music.load(midi_file)
    pygame.mixer.music.play(loops)

def stop():
    pygame.mixer.music.stop()
