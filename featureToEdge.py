#!/usr/bin/env python
'''
CREATED:2012-03-22 09:00:19 by Brian McFee <bmcfee@cs.ucsd.edu>

Convert a set of vector-valued data into an edge clustering

Usage:
./featureToEdge.py edge_OUT.pickle centers_OUT.pickle data_IN.pickle NUM_EDGES DESCRIPTION

'''


import sys
import numpy
import cPickle as pickle
import sparsecoding

NORMALIZE = False

def loadData(infile):
    with open(infile, 'r') as f:
        X = pickle.load(f)['X']
        pass

    if NORMALIZE:
        for q in X:
            X[q] /= numpy.sqrt(numpy.sum(X[q]**2))
            pass
    return X

def makeEdges(X, k, DESC):

    # 1. learn the cluster centers
    print 'Learning cluster centers... ',
    # Convert X to matrix format
    W = numpy.zeros((len(X), len(X[X.keys()[0]])))
    for (i, z) in enumerate(X.values()):
        W[i] = z
        pass
    D = sparsecoding.dictionary_kmeans(W, k=k, num_steps=2*len(X))
    print 'done.'

    # 2. Construct edge labels
    edge_labels = ['%s-%04d.%04d' % (DESC, k, z) for z in range(k)]

    # 3. encode
    print 'Encoding vertex->edge mappings... ',
    E = {}
    for v in X:
        i       = numpy.argmax(sparsecoding.vq(D, X[v]))
        E[v]    = [edge_labels[i]]
        pass
    print 'done.'
    return (E, D)

if __name__ == '__main__':
# ./featureToEdge.py edge_OUT.pickle centers_OUT.pickle data_IN.pickle NUM_EDGES DESCRIPTION
    X       = loadData(sys.argv[3])
    k       = int(sys.argv[4])
    DESC    = sys.argv[5]
    (E,D)   = makeEdges(X, k, DESC)
    with open(sys.argv[1], 'w') as f:
        pickle.dump({'X': E}, f)
        pass
    with open(sys.argv[2], 'w') as f:
        pickle.dump({'D': D, 'desc': DESC}, f)
        pass
    pass
