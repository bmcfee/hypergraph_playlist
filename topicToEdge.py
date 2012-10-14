#!/usr/bin/env python
'''
CREATED:2012-03-22 13:41:57 by Brian McFee <bmcfee@cs.ucsd.edu>
 
Convert latent topic assignment vectors to edge sets

Usage:
./topicToEdge.py edge_OUT.pickle data_IN.pickle NUM_ASSIGNMENTS DESCRIPTION
'''

import sys
import numpy
import cPickle as pickle
import heapq

def loadData(infile):
    with open(infile, 'r') as f:
        X = pickle.load(f)['X']
        pass
    return X


def makeEdges(X, k, DESC):

    d = len(X[X.keys()[0]])

    E = {}
    idx = range(d)
    edge_labels = ['%s-%02d.%02d' % (DESC, k, z) for z in idx]

    for (v, topics) in X.iteritems():
        E[v] = []
        for (score, i) in heapq.nlargest(k, zip(topics, idx)):
            E[v].append(edge_labels[i])
            pass
        pass
    return E


if __name__ == '__main__':
    X       = loadData(sys.argv[2])
    k       = int(sys.argv[3])
    DESC    = sys.argv[4]
    E       = makeEdges(X, k, DESC)
    with open(sys.argv[1], 'w') as f:
        pickle.dump({'X': E}, f)
        pass
    pass
