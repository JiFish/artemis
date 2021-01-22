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

__MIDI_BUILDER = None
__POSITION = 0
__CURRENT_OCTAVE = 5
__CURRENT_NOTE_LEN = 1
__NOTES_UNSORTED = {'C':0,  'C#':1, 'C+':1,  'D-':1,  'D':2,   'D#':3, 'D+':3,   'E-': 3,
                    'E':4,  'F':5,  'F#':6,  'F+':6,  'G-':6,  'G':7,  'G#':8,   'G+':8,
                    'A-':8, 'A':9,  'A#':10, 'A+':10, 'B-':10, 'B':11, 'P':-999, 'R':-999}

# Since python 3.6 dicts remember insert order
# So we can sort just once here
__NOTES = {}
for k in sorted(__NOTES_UNSORTED, key=len, reverse=True):
    __NOTES[k] = __NOTES_UNSORTED[k]

def __pull_number(s):
    numbstr = ""
    while len(s)>0 and s[0].isdigit():
        numbstr += s[0]
        s = s[1:]
    if numbstr == "": return -1, s
    return int(numbstr), s

def __new_song():
    global midi_file, __MIDI_BUILDER, __POSITION, __CURRENT_OCTAVE
    __MIDI_BUILDER = midiutil.MIDIFile(numTracks=1, file_format=1)
    __MIDI_BUILDER.addTempo(0,0,120)
    __MIDI_BUILDER.addProgramChange(0, 0, 0, 80)
    __POSITION = 0
    __CURRENT_OCTAVE = 5
    __CURRENT_NOTE_LEN = 1

def __add_tempo(tempo):
    if (__MIDI_BUILDER == None): __new_song()
    __MIDI_BUILDER.addTempo(0, __POSITION, tempo)

def __add_note(pitch, length = 1, volume = 127):
    if pitch < 0: return __add_pause(length)
    if pitch > 131:
        raise ValueError("Pitch too high!")
    global __POSITION, __MIDI_BUILDER
    if (__MIDI_BUILDER == None): __new_song()
    __MIDI_BUILDER.addNote(0, 0, pitch, __POSITION, length, volume)
    __POSITION += length

def __add_pause(length):
    global __POSITION, __MIDI_BUILDER
    if (__MIDI_BUILDER == None): __new_song()
    __POSITION += length

def process_string(s):
    global __CURRENT_OCTAVE, __CURRENT_NOTE_LEN
    if (__MIDI_BUILDER == None): __new_song()
    # Remove all whitespace
    s = ''.join(s.split()).upper()
    while len(s) > 0:
        starting_len = len(s)
        # notes
        foundnote = False
        for note in __NOTES:
            if s.startswith(note):
                # Remove from string
                s = s[len(note):]
                # Add to song
                # Look for length
                notelen, s = __pull_number(s)
                if notelen < 0:
                    notelen = __CURRENT_NOTE_LEN
                else:
                    notelen = 4/notelen
                # Look for 'dot'
                if len(s)>0 and s[0]=='.':
                    notelen *= 1.5
                    s = s[1:]
                # Get pitch
                pitch = ((__CURRENT_OCTAVE)*12)+__NOTES[note]
                #print("addnote"+str(pitch)+","+str(notelen)+" oct:"+str(__CURRENT_OCTAVE))
                __add_note(pitch, notelen)
                foundnote = True
                break
        if foundnote: continue

        # Octaves
        if s[0] == '>':
            __CURRENT_OCTAVE = min(9,__CURRENT_OCTAVE+1)
            s = s[1:]
        elif s[0] == '<':
            __CURRENT_OCTAVE = max(0,__CURRENT_OCTAVE-1)
            s = s[1:]
        elif s[0] == 'O':
            s = s[1:]
            oct, s = __pull_number(s)
            if oct < 0 or oct > 9:
                raise ValueError("Invalid octave in music string "+str(oct))
            __CURRENT_OCTAVE = oct
        # Tempo
        elif s[0] == "T":
            s = s[1:]
            tempo, s = __pull_number(s)
            if tempo < 1:
                raise ValueError("Invalid Tempo")
            __add_tempo(tempo)
            #print("tempo"+str(__POSITION)+","+str(tempo))
        # Default length
        elif s[0] == "L":
            s = s[1:]
            notelen, s = __pull_number(s)
            if notelen < 1:
                raise ValueError("Invalid Length")
            __CURRENT_NOTE_LEN =4/notelen

        # Check we processed something
        if starting_len == len(s):
            #print(s)
            raise ValueError("Invalid music string")

def play(loops):
    global __POSITION, __MIDI_BUILDER
    if (__MIDI_BUILDER == None): __new_song()
    midi_file = tempfile.TemporaryFile()
    __MIDI_BUILDER.writeFile(midi_file)
    __MIDI_BUILDER = None
    __POSITION = 0
    midi_file.seek(0)
    pygame.mixer.music.load(midi_file)
    pygame.mixer.music.play(loops)

def stop():
    pygame.mixer.music.stop()

def wait_for_song():
    try:
        while pygame.mixer.music.get_busy():
            artemis.tick()
    finally:
        pygame.mixer.music.stop()
