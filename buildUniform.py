#!/usr/bin/env python
'''
CREATED:2012-03-21 20:05:12 by Brian McFee <bmcfee@cs.ucsd.edu>
  
Construct the uniform edge

Usage:
./buildUniform.py output.pickle playlist.pickle

'''


import sys
import cPickle as pickle

def loadSongs(infile):

    with open(infile, 'r') as f:
        songs = pickle.load(f)['songs']
        pass
    return songs

def getUniform(songs):
    X = {}

    for s in songs:
        X[s] = ['__UNIFORM']
    return X

if __name__ == '__main__':
    songs = loadSongs(sys.argv[2])
    uniform = getUniform(songs)
    with open(sys.argv[1], 'w') as f:
        pickle.dump({'X': uniform}, f)
        pass
    pass
