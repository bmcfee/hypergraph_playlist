#!/usr/bin/env python
'''
CREATED:2012-03-30 14:10:51 by Brian McFee <bmcfee@cs.ucsd.edu>

Get the most and least-likely test example playlists per category

Usage:

./getBestWorst.py /path/to/songhash.pickle /path/to/likelihoods.pickle /path/to/playlist/directory

'''

import sys
import cPickle as pickle
import samplePlaylist
import numpy

def getBestWorst(songs, L, plpath):

    cats = L.keys()
    cats.sort()

    for c in cats:
        with open('%s/%s_test.pickle' % (plpath, c), 'r') as f:
            P = pickle.load(f)
            pass
        print 'Category: %s' % c
        i   = numpy.argmax(L[c])
        print 'Best playlist: %.4f\n-----------------------' % L[c][i]
        samplePlaylist.printPlaylist(P[i], songs)
        j   = numpy.argmin(L[c])
        print 'Worst playlist: %.4f\n-----------------------' % L[c][j]
        samplePlaylist.printPlaylist(P[j], songs)
        print
        pass
    pass


if __name__ == '__main__':
    with open(sys.argv[1], 'r') as f:
        songs = pickle.load(f)
        pass

    with open(sys.argv[2], 'r') as f:
        L = pickle.load(f)
        pass

    getBestWorst(songs, L['L'], sys.argv[3])
    pass
