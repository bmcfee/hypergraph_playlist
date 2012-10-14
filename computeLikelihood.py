#!/usr/bin/env python
'''
CREATED:2012-03-30 13:20:49 by Brian McFee <bmcfee@cs.ucsd.edu>

Compute test-set likelihoods for each playlist category from a given model

Usage:

./computeLikelihood.py likelihoods_OUT.pickle perfs_IN.pickle

'''

import sys
import cPickle as pickle
import hypergraph
import argparse
import glob, os

def processArguments():
    parser  =   argparse.ArgumentParser(description='Playlist likelihood computation')
    
    parser.add_argument(    'likelihoods_out',
                            nargs               =   1,
                            help                =   'Path to likelihood output')

    parser.add_argument(    'perf_in',
                            nargs               =   1,
                            help                =   'Path to training results file')

    return vars(parser.parse_args(sys.argv[1:]))



def loadPerfs(params):
    def loadModel(p):
        with open(p['model_in'][0], 'r') as f:
            G = pickle.load(f)['G']
            pass
        return G

    with open(params['perf_in'][0], 'r') as f:
        P = pickle.load(f)
        pass
    G = loadModel(P['params'])

    return (G, P)


def getFiles(params, suffix='test'):
    """
    Generator to walk a basedir and grab all files of the specified extension
    """
    for root, dirs, files in os.walk(params['playlist_dir'][0]):
        for f in glob.glob(os.path.join(root, '*_'+suffix+'.pickle')):
            with open(os.path.abspath(f), 'r') as infile:
                P = pickle.load(infile)
                pass
            yield (P, os.path.basename(f).replace('_'+suffix+'.pickle',''))
    pass


def computeLikelihood(params):
    # Load the perfs and model data
    (G, Perfs) = loadPerfs(params)

    L = {}
    
    LL_FUNCTION = G.loglikelihood_stateless
    if Perfs['params']['markov']:
        LL_FUNCTION = G.loglikelihood
        pass

    for (P, name) in getFiles(Perfs['params']):
        # Set the weights for this set
        print 'Testing %s' % name
        G.setWeights(Perfs['weights'][name])
        L[name] = map(LL_FUNCTION, P)
        pass

    return {'params': params, 'L': L}

if __name__ == '__main__':
    params  = processArguments()
    results = computeLikelihood(params)
    with open(params['likelihoods_out'][0], 'w') as f:
        pickle.dump(results, f)
        pass
    pass
