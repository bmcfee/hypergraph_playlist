#!/usr/bin/env python
'''
CREATED:2012-03-20 13:49:41 by Brian McFee <bmcfee@cs.ucsd.edu>

Count the number of playlist segments in a pickle

Usage:
./countPlaylists file.pickle

'''

import sys
import cPickle as pickle


def countPlaylists(X):

    nplaylists  = len(X['P'])
    nsongs      = len(X['songs'])
    nsegments   = sum(map(len, X['P'].values()))
    return (nplaylists, nsegments, nsongs)


if __name__ == '__main__':
    with open(sys.argv[1], 'r') as f:
        X = pickle.load(f)
    (npl, nseg, nsongs) = countPlaylists(X)
    print '%20s: %d playlists, %d segments, %d songs' % (sys.argv[1], npl, nseg, nsongs)
    pass
