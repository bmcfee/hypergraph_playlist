#!/usr/bin/env python
'''
CREATED:2012-03-21 17:44:29 by Brian McFee <bmcfee@cs.ucsd.edu>
 
Construct a song=>year/era mapping

Usage:
./buildYearmap.py output.pickle playlist.pickle /path/to/track_metadata.db

'''


import sys
import sqlite3
import numpy
import cPickle as pickle


def loadSongs(infile):

    with open(infile, 'r') as f:
        songs = pickle.load(f)['songs']
        pass
    return songs

def getYearMap(songs, dbc):

    X = {}

    cur = dbc.cursor()

    cur.execute('''SELECT song_id, year FROM songs WHERE year > 0''')

    for (song_id, year) in cur:
        if song_id not in songs:
            continue
        X[song_id] = {'YEAR_%4d' % year, 'DECADE_%4d' % int(10 * numpy.floor(float(year) / 10)), 'DECADE_%4d' % int(10 * numpy.floor((float(year) + 5)/10) - 5)}
        pass
    return X

if __name__ == '__main__':
    songs = loadSongs(sys.argv[2])
    with sqlite3.connect(sys.argv[3]) as dbc:
        yearmap = getYearMap(songs, dbc)
        pass
    with open(sys.argv[1], 'w') as f:
        pickle.dump({'X': yearmap}, f)
        pass
    pass
