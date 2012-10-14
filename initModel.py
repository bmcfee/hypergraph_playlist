#!/usr/bin/env python
'''
CREATED:2012-03-22 14:52:20 by Brian McFee <bmcfee@cs.ucsd.edu>

Initialize a hypergraph playlist model from a collection of edge sets

'''

import sys
import hypergraph
import cPickle as pickle
import argparse


def processArguments():
    parser = argparse.ArgumentParser(description='HyperGraph playlist model constructor')

    parser.add_argument(    '-m',
                            required    = False,
                            dest        = 'm',
                            type        = int,
                            default     = 512,
                            help        = 'Minimum edge size')

    parser.add_argument(    '-r',
                            required    = False,
                            dest        = 'rho',
                            type        = float,
                            default     = 0.5,
                            help        = 'Maximum fraction of input sets to retain in quadratic expansion')

    parser.add_argument(    '-q',
                            required    = False,
                            dest        = 'quadratic',
                            default     = False,
                            action      = 'store_true',
                            help        = 'Enable quadratic edge expansion')
    parser.add_argument(    'outfile',
                            nargs       = 1,
                            help        = 'Path to output pickle')
    parser.add_argument(    'infiles',
                            nargs       = '+',
                            help        = 'Path to input pickles')
    return vars(parser.parse_args(sys.argv[1:]))

def constructModel(params):
    
    G = hypergraph.Hypergraph()
    for infile in params['infiles']:
        print 'Loading ', infile
        with open(infile, 'r') as f:
            G.importEdge(pickle.load(f)['X'])
            pass
        pass
    print 'Pruning edges'
    G.pruneEdges(params['m'])
    if params['quadratic']:
        print 'Expanding edges'
        G.quadraticExpansion(MIN_SIZE=params['m'], rho=params['rho'])
        pass
    return G

if __name__ == '__main__':
    params  = processArguments()
    model   = constructModel(params)
    with open(params['outfile'][0], 'w') as f:
        pickle.dump({'G': model}, f)
        pass
    pass
