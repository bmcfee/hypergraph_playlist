#!/usr/bin/env python
'''
CREATED:2012-03-20 20:26:12 by Brian McFee <bmcfee@cs.ucsd.edu>
 
Load an MML latent-factor model and save as a pickle

Usage:
./buildCFmatrix.py cfdata.pickle item_mapping.txt cfmodel.mml playlist.pickle 

'''

import sys
import numpy
import cPickle as pickle


def loadPlaylistSongs(infile):

    with open(infile, 'r') as f:
        X = pickle.load(f)
        pass
    return X['songs']


def loadItemMap(infile, songs):

    itemmap = {}

    with open(infile, 'r') as f:
        for line in f:
            (internal, external) = line.strip().split('\t', 2)
            if external in songs:
                itemmap[int(internal)] = external
                pass
            pass
        pass
    return itemmap

def loadCFdata(itemmap, infile):

    X = {}
    with open(infile, 'r') as f:
        # skip the first two lines
        f.readline()
        f.readline()
        (nUsers, nDim) = map(int, f.readline().strip().split(' ', 2))
        # chew up the next zillion lines
        for i in xrange(nUsers * nDim + 1):
            f.readline()
            pass
        nItems = int(f.readline().strip())

        for i in xrange(nItems + 1):
            f.readline()
            pass

        # now to load the vector data
        for i in xrange(nItems):
            data = numpy.zeros(nDim)
            for j in xrange(nDim):
                data[j] = float(f.readline().strip().split(' ', 3)[-1])
                pass
            if i in itemmap:
                X[itemmap[i]] = data
                pass
            pass
        pass
    return X
    pass

def saveData(outfile, cfdata):
    with open(outfile, 'w') as f:
        pickle.dump({'X': cfdata}, f)
        pass
    pass

# ./buildCFmatrix.py cfdata.pickle item_mapping.txt cfmodel.mml playlist.pickle 
if __name__ == '__main__':
    songset     = loadPlaylistSongs(sys.argv[4])
    itemMapping = loadItemMap(sys.argv[2], songset)
    cfdata      = loadCFdata(itemMapping, sys.argv[3])
    saveData(sys.argv[1], cfdata)
    pass
