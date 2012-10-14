#!/usr/bin/env python
'''
CREATED:2012-03-21 10:02:40 by Brian McFee <bmcfee@cs.ucsd.edu>
 
Construct song=>LDA vector mapping

Usage:
./buildLDAmatrix.py output.pickle vw_lda_vectors.txt playlist.pickle
'''

import sys
import cPickle as pickle
import numpy

def loadSongs(infile):
    with open(infile, 'r') as f:
        songs = pickle.load(f)['songs']
        pass
    return songs

def loadLDA(songs, infile):

    X = {}
    with open(infile, 'r') as f:
        for line in f:
            garbage = line.strip().split(' ')
            songid  = garbage[-1]
            if songid not in songs:
                continue
            X[songid] = numpy.array(map(float,garbage[:-2]))
            pass
        pass
    return X

if __name__ == '__main__':
    songs = loadSongs(sys.argv[3])
    X = loadLDA(songs, sys.argv[2])
    with open(sys.argv[1], 'w') as f:
        pickle.dump({'X': X}, f)
        pass
    pass
