#!/usr/bin/env python
'''
CREATED:2012-03-28 08:26:04 by Brian McFee <bmcfee@cs.ucsd.edu>

Analyze the edge weights in a hypergraph model

Usage:

./analyzeEdgeWeights.py results_IN.pickle CATEGORIES weight_distribution_out.csv
'''

import sys
import re
import cPickle as pickle
import collections
import pprint

def buildREs():
    # first, check to see if it's a compound edge: grep for -&-

    # if not, it's one of the following:
    #   __UNIFORM                       =>      Uniform
    #   (YEAR|DECADE)_XXXX              =>      Era
    #   LYRICS-XX.XX                    =>      Lyrics
    #   AUDIO-XXXX.XXXX                 =>      Audio
    #   FAMILIAR_(LOW|MED|HIGH)         =>      Familiarity
    #   CF-XXXX.XXXX                    =>      CF
    #   ???                             =>      Tags
    #
    # if it is compound, it's the following:
    #   (YEAR|DECADE)_XXXX-&-(YEAR|DECADE)_XXXX     => Era
    #   Lyrics-XX.XX-&-Lyrics-XX.XX                 => Lyrics
    #   ...
    #

    # Order in this dictionary is important
    P = {}
    P[' Uniform']       =   '__UNIFORM'
    P['Audio']          =   'AUDIO-\d{4}\.\d{4}'
    P['CF']             =   'CF-\d{4}\.\d{4}'
    P['Era']            =   '(YEAR|DECADE)_\d{4}'
    P['Familiarity']    =   'FAMILIARITY_(LOW|MED|HIGH)'
    P['Lyrics']         =   'LYRICS-\d{2}\.\d{2}'

    simple          = P.keys()
    simple.sort()
    simple  = simple[1:]

    # And now for the tag features...

    for i in xrange(len(simple)):
        P['%s-Tags' % simple[i]] = '^((.*?-&-%s)|(%s-&-.*))$' % (P[simple[i]], P[simple[i]])
        for j in xrange(i+1, len(simple)):
            P[simple[i]+'-'+simple[j]] = '^((%s-&-%s)|(%s-&-%s))$' % (P[simple[i]], P[simple[j]], P[simple[j]], P[simple[i]])
        P[simple[i]] = '^(%s|(%s-&-%s))$' % (P[simple[i]], P[simple[i]], P[simple[i]])
        pass

    P['Tags']   = '.*'

    R   = {}
    for k in P:
        R[k] = re.compile(P[k])
        pass
    return R


def parseWeights(R, weights):

    keys    = R.keys()
    keys.sort()

#     A       = {}
    A = collections.defaultdict(lambda: 0.0)
    for (edge, w) in weights.iteritems():
        found = False
        for k in keys:
            if R[k].match(edge):
                A[k] += w
                found = True
            if found:
                break
            pass
        if not found:
            print 'ERROR: could not match edge: ', edge
        pass
    return A

def crunchWeights(R, model_in, categories_in, csv_out):

    with open(model_in, 'r') as f:
        weights = pickle.load(f)['weights']
        pass

    with open(categories_in, 'r') as f:
        cats = [s.strip() for s in f.readlines()]
        pass

    edges = R.keys()
    edges.sort()

    with open(csv_out, 'w') as f:
        f.write('CATEGORY\\EDGE,%s\n' % ','.join(edges))
        for c in cats:
#             W = parseWeights(R, weights[c])
            W = parseWeights(R, weights[c][0])
            s =','.join(['%f' % W[x] for x in edges])
            f.write('%s,%s\n' % (c, s))
            pass
        pass
    pass


if __name__ == '__main__':
    R = buildREs()
    crunchWeights(R, sys.argv[1], sys.argv[2], sys.argv[3])
    pass
