#!/usr/bin/env python
'''
CREATED:2012-03-20 13:26:12 by Brian McFee <bmcfee@cs.ucsd.edu>
 

Merge two or more playlist pickles into a single pickle

Usage:
./mergePlaylists.py output.pickle input1.pickle input2.pickle [input3.pickle ...]

'''

import sys
import pickle

def loadPlaylist(infile):
    with open(infile, 'r') as f:
        X = pickle.load(f)
        pass
    return (X['P'], X['songs'])


def mergePlaylists(outfile, infiles):

    P       =  {}
    songs   =  set()

    for f in infiles:
        (Pnew, songsnew) = loadPlaylist(f)
        P.update(Pnew)
        songs.update(songsnew)
        pass

    with open(outfile, 'w') as f:
        pickle.dump({'P': P, 'songs': songs}, f)
    pass


if __name__ == '__main__':
    outfile = sys.argv[1]
    infiles = sys.argv[2:]

    mergePlaylists(outfile, infiles)
    pass


