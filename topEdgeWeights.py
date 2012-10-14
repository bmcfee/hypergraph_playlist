#!/usr/bin/env python
'''
CREATED:2012-03-28 12:54:50 by Brian McFee <bmcfee@cs.ucsd.edu>

Extract the top k edges (by weight) from each playlist model

Usage:

./topEdgeWeights.py results_IN.pickle PLAYLIST_CATEGORIES.txt k topweights_OUT.csv

'''

import sys
import cPickle as pickle


def topEdgeWeights(results_IN, cats_IN, k, weights_OUT):

    with open(results_IN, 'r') as f:
        weights = pickle.load(f)['weights']
        pass

    with open(cats_IN, 'r') as f:
        cats = [s.strip() for s in f.readlines()]
        pass

    with open(weights_OUT, 'w') as f:
        for c in cats:
            W = [(weight, edge) for (edge, weight) in weights[c].iteritems()]
            W.sort(reverse=True)
            edges = [edge for (weight,edge) in W]
            f.write('%s,%s\n' % (c, ','.join(edges[:k])))
            pass
        pass
    pass


if __name__ == '__main__':
    topEdgeWeights(sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4])
    pass
