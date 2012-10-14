#!/usr/bin/env python
'''
CREATED:2012-03-27 20:43:37 by Brian McFee <bmcfee@cs.ucsd.edu>

Merge flattened playlist pickles

Usage:

./mergeFlat.py OUTPUT.pickle INPUT1.pickle [INPUT2.pickle ...]

'''

import cPickle as pickle
import sys

def flattenPickle(outfile, infiles):
    
    def loadPickle(fname):
        with open(fname, 'r') as f:
            P = pickle.load(f)
        return P

    P = []

    for f in infiles:
        Pnew = loadPickle(f)
        if len(P) == 0:
            P = [None] * len(Pnew)
            for q in range(len(Pnew)):
                P[q] = []
                pass
            pass
        for q in range(len(P)):
            P[q].extend(Pnew[q])
            pass
        pass

    with open(outfile, 'w') as f:
        pickle.dump(P, f)
        pass
    pass

if __name__ == '__main__':
    flattenPickle(sys.argv[1], sys.argv[2:])
    pass
