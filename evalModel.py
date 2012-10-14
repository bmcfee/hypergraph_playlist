#!/usr/bin/env python
'''
CREATED:2012-03-27 20:48:48 by Brian McFee <bmcfee@cs.ucsd.edu>
 
Model evaluator

Usage:

./evalModel.py results_OUT.pickle model_IN.pickle /path/to/playlist/directory [-s] [-u]

'''

import argparse
import sys
import glob, os
import cPickle as pickle
import hypergraph
import numpy

def processArguments():
    parser = argparse.ArgumentParser(description='Playlist model evalutron')

    parser.add_argument(    'results_out',
                            nargs       =   1,
                            help        =   'Path to results output')

    parser.add_argument(    'model_in',
                            nargs       =   1,
                            help        =   'Path to model input')

    parser.add_argument(    'playlist_dir',
                            nargs       =   1,
                            help        =   'Path to playlist directory')

    parser.add_argument(    '-a',
                            nargs       =   1,
                            type        =   float,
                            default     =   1.0,
                            required    =   False,
                            dest        =   'a',
                            help        =   'Alpha (shape) parameter for weight prior (default=1.0)')

    parser.add_argument(    '-l',
                            nargs       =   '+',
                            type        =   float,
                            default     =   [1e0],
                            required    =   False,
                            dest        =   'lam',
                            help        =   'List of lambda (scale) parameters for weight prior (default=1e0)')

    parser.add_argument(    '-d',
                            nargs       =   1,
                            type        =   int,
                            default     =   -1,
                            required    =   False,
                            dest        =   'DEBUG',
                            help        =   'Debug level (-1,0,1,2) (default=-1')

    parser.add_argument(    '-m',
                            nargs       =   1,
                            type        =   int,
                            default     =   30,
                            required    =   False,
                            dest        =   'm',
                            help        =   'L-BFGS basis size (default=30)')

    parser.add_argument(    '-s',
                            required    =   False,
                            dest        =   'markov',
                            default     =   True,
                            action      =   'store_false',
                            help        =   'Learn stationary edge weights')

    parser.add_argument(    '-v',
                            required    =   False,
                            dest        =   'val',
                            default     =   0.00,
                            type        =   float,
                            help        =   '% of data to use for validation (default: 0.0)')

    parser.add_argument(    '-u',
                            required    =   False,
                            dest        =   'weighted',
                            default     =   True,
                            action      =   'store_false',
                            help        =   'Evaluate uniform edge weights')

    return vars(parser.parse_args(sys.argv[1:]))

def loadModel(params):
    with open(params['model_in'][0], 'r') as f:
        G = pickle.load(f)['G']
        pass
    return G

def getFiles(params, suffix):
    """
    Generator to walk a basedir and grab all files of the specified extension
    """
    F = glob.glob(os.path.join(params['playlist_dir'][0], '*_'+suffix+'.pickle'))
    F.sort()
    for f in F:
        with open(os.path.abspath(f), 'r') as infile:
            P = pickle.load(infile)
            pass
        yield (P, os.path.basename(f).replace('_'+suffix+'.pickle',''))
    pass


def evaluateModel(params):

    weights = {}
    scores  = {}

    # 1: load the model
    print 'Loading model...'
    G = loadModel(params)

    # Reset edge weights
    G.unlearn()

    for (P, name) in getFiles(params, 'train'):
        nFolds  = len(P)
        print 'Training on %20s... ' % name,
        weights[name]   = [None] * nFolds

        for fold in xrange(nFolds):
            if params['weighted']:
                G.learn(P[fold], 
                    MARKOV  =   params['markov'], 
                    a       =   params['a'], 
                    lam     =   params['lam'],
                    DEBUG   =   params['DEBUG'],
                    m       =   params['m'],
                    val     =   params['val'])
                pass
            weights[name][fold]     = G.getWeights()
            scores[name]            = {}
        print ' done.'
        pass

    for (P, name) in getFiles(params, 'test'):
        nFolds  = len(P)
        K = list(set(['ALL', name]))
        K.sort()
        for trainDist in K:
            print 'Testing G(%20s) on %20s\t' % (trainDist, name),
            s = numpy.zeros(nFolds)
            for fold in xrange(nFolds):
                G.setWeights(weights[trainDist][fold])
                s[fold] = G.avglikelihood(P[fold], MARKOV=params['markov'])
                pass
            scores[trainDist][name] = s
            print 'LL: %.4f +- %.4f' % (numpy.mean(s), numpy.std(s))
            pass
        pass

    results = {'weights': weights, 'scores': scores, 'params': params}
    return results


if __name__ == '__main__':
    params  = processArguments()
    results = evaluateModel(params)
    with open(params['results_out'][0], 'w') as f:
        pickle.dump(results, f)
        pass
    pass
