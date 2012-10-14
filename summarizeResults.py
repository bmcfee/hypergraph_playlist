#!/usr/bin/env python
'''
CREATED:2012-03-28 15:27:58 by Brian McFee <bmcfee@cs.ucsd.edu>

Summarize likelihood results for a collection of playlist files

Usage:
./summarizeResults.py OUTPUT.csv PLAYLIST_CATEGORIES.txt results_IN1.pickle results_IN2.pickle ...
'''


import cPickle as pickle
import sys
import os

def loadCats(infile):
    with open(infile, 'r') as f:
        cats = [s.strip() for s in f.readlines()]
        pass
    return cats


def summarize(outf, cats, infiles):
    
    outf.write('MODEL\\CATEGORY,%s\n' % ','.join(cats))

    for inf in infiles:
        with open(inf, 'r') as f:
            scores = pickle.load(f)['scores']
            pass
        
        vals = []
        for c in cats:
            vals.append('%f+-%f' % (numpy.mean(scores[c][c]), numpy.std(scores[c][c])))
            pass

        desc = os.path.basename(inf).replace('perf_', '').replace('.pickle', '')
        outf.write('%s,%s\n' % (desc, ','.join(vals)))
        pass
    pass


if __name__ == '__main__':
    cats = loadCats(sys.argv[2])
    with open(sys.argv[1], 'w') as f:
        summarize(f, cats, sys.argv[3:])
    pass
