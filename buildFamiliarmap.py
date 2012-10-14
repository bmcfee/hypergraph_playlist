#!/usr/bin/env python
'''
CREATED:2012-03-29 21:26:27 by Brian McFee <bmcfee@cs.ucsd.edu>
  
Construct a song=>familiarity mapping

Usage:
./buildFamiliarmap.py output.pickle playlist.pickle /path/to/track_metadata.db

'''


import sys
import sqlite3
import numpy
import cPickle as pickle

import scipy.stats.mstats

def loadSongs(infile):

    with open(infile, 'r') as f:
        songs = pickle.load(f)['songs']
        pass
    return songs

def getFamiliarMap(songs, dbc):

    X = {}

    cur = dbc.cursor()

    cur.execute('''SELECT song_id, artist_familiarity FROM songs''')

    for (song_id, artist_familiarity) in cur:
        if song_id not in songs:
            continue
        X[song_id] = artist_familiarity
#         {'YEAR_%4d' % year, 'DECADE_%4d' % int(10 * numpy.floor(float(year) / 10)), 'DECADE_%4d' % int(10 * numpy.floor((float(year) + 5)/10) - 5)}
        pass

    # Compute quantiles
    q = scipy.stats.mstats.mquantiles(X.values(), [0.25, 0.75])

    # Map to descriptors
    for k in X:
        if X[k] <= q[0]:
            X[k] = {'FAMILIARITY_LOW'}
        elif q[0] < X[k] <= q[1]:
            X[k] = {'FAMILIARITY_MED'}
        else:
            X[k] = {'FAMILIARITY_HIGH'}
        pass
    return X

if __name__ == '__main__':
    songs = loadSongs(sys.argv[2])
    with sqlite3.connect(sys.argv[3]) as dbc:
        fammap = getFamiliarMap(songs, dbc)
        pass
    with open(sys.argv[1], 'w') as f:
        pickle.dump({'X': fammap}, f)
        pass
    pass
