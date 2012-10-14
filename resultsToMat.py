#!/usr/bin/env python
'''
CREATED:2012-04-02 17:50:05 by Brian McFee <bmcfee@cs.ucsd.edu>
 
Convert performance metrics into .mat format

Only stores the scores

Usage:

./resultsToMat.py perf.pickle results_out.mat
'''

import cPickle as pickle
import numpy
import scipy.io
import sys


def convert(inpickle, outmat):

    with open(inpickle, 'r') as f:
        P = pickle.load(f)['scores']
        pass

    labels = P.keys()

    labels.sort()

    n = len(labels)
    m = len(P[labels[0]][labels[0]])

    Xall    = numpy.zeros((n,m))
    Xspec   = numpy.zeros((n,m))

    for (i, l) in enumerate(labels):
        Xall[i]     = P['ALL'][l]
        Xspec[i]    = P[l][l]
        pass

    scipy.io.savemat(outmat, {'labels': labels, 'Xall': Xall, 'Xspec': Xspec}, oned_as='column')
    pass

if __name__ == '__main__':
    convert(sys.argv[1], sys.argv[2])
    pass
