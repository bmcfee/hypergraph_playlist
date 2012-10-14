#!/usr/bin/env python
'''
CREATED:2012-03-27 21:41:19 by Brian McFee <bmcfee@cs.ucsd.edu>
 
Convert a playlist eval results file to CSV table

Usage:

./resultsToCSV.py input.pickle output.csv CATEGORIES.txt

CATEGORIES.txt contains the categories of interest, in order
'''

import sys
import cPickle as pickle
import numpy


UNIFORM = -11.496373

def loadCats(infile):
    with open(infile, 'r') as f:
        cats = [s.strip() for s in f.readlines()]
        pass
    return cats

def processData(infile, outfile, cats):

    with open(infile, 'r') as f:
        scores = pickle.load(f)['scores']
        pass

    with open(outfile, 'w') as f:
        f.write('Category,Background,Specific,Ratio,BG vs. Uniform, Cat vs Uniform\n')
        for c in cats:
            f.write('%s,%f,%f,%f,%f,%f\n' % (c, 
                                    numpy.mean(scores['ALL'][c]), 
                                    numpy.mean(scores[c][c]),
                                    numpy.mean(1 - scores[c][c] / scores['ALL'][c]),
                                    numpy.mean(1 - scores['ALL'][c] / UNIFORM),
                                    numpy.mean(1 - scores[c][c] / UNIFORM)
                                    ))
            pass
#         values = ','.join(cats)
#         f.write('TRAIN\\TEST,%s\n' % values)
#         for c_train in cats:
#             if c_train in scores:
#                 values = []
#                 for c_test in cats:
#                     if c_test in scores:
#                         values.append('%f' % numpy.mean(scores[c_train][c_test]))
#                 f.write('%s,%s\n' % (c_train, ','.join(values)))
#                 pass
#             pass
#         pass
    pass


if __name__ == '__main__':
    processData(sys.argv[1], sys.argv[2], loadCats(sys.argv[3]))
    pass
