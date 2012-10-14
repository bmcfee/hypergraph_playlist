#!/usr/bin/env python
'''
CREATED:2012-03-21 20:18:42 by Brian McFee <bmcfee@cs.ucsd.edu>

Hypergraph random walk playlist model
'''

import numpy
import random
import scipy.optimize
import scipy.sparse
import numpy.random
import re

class Hypergraph(object):

    def __init__(self):
        self.__vertex_to_edge   = dict()
        self.__edge_set         = []
        self.__edge_to_label    = []
        self.__label_to_edge    = dict()
        self.__weights          = []
        self.__edge_size        = None
        self.__Z0               = None
        self.__Zt               = None
        pass

    def importEdge(self, edgeMap):
        '''
            edgeMap is a dict: vertex -> collection of edge labels
        '''
        self.__weights = list(self.__weights)
        for v in edgeMap:
            if v not in self.__vertex_to_edge:
                # if we don't already know about this vertex, construct an edge set for it
                self.__vertex_to_edge[v] = set()
                pass
            for e in edgeMap[v]:
                # first determine whether the edge is known
                if e not in self.__label_to_edge:
                    # Add the new edge to the list
                    self.__edge_to_label.append(e)

                    # Initialize the edge set
                    self.__edge_set.append(set())

                    # Construct it's numerical mapping
                    self.__label_to_edge[e] = len(self.__edge_to_label) - 1

                    # Initialize the edge weight
                    self.__weights.append(1.0)
                    pass
                edgeNum = self.__label_to_edge[e]
                self.__vertex_to_edge[v].add(edgeNum)
                self.__edge_set[edgeNum].add(v)
                pass
            pass
        # Compute set sizes for normalization
        self.__edge_size = map(len, self.__edge_set)
        # Uniform weights over all songs in an edge
        self.__Z0       = numpy.array(self.__edge_size)
        # Uniform over all but one song in an edge
        self.__Zt       = numpy.array(self.__edge_size) - 1.0

        self.__weights  = numpy.array(self.__weights)
        pass

    def pruneEdges(self, MIN_SIZE=128):
        '''
            Remove all edges with fewer than MIN_SIZE vertices
        '''

        # First, build a list of the good edges
        retained_edges = []

        for (e, s) in enumerate(self.__edge_size):
            if s >= MIN_SIZE:
                retained_edges.append( (s, e) )
                pass
            pass

        retained_edges.sort(reverse=True)
        
        # Backup old data
        old_edge_set        = self.__edge_set
        old_edge_to_label   = self.__edge_to_label

        # re-initialize
        self.__init__()

        for (w, e) in retained_edges:
            for x in old_edge_set[e]:
                self.importEdge({x: [old_edge_to_label[e]]})
                pass
            pass
        pass


    def killEdgeExpr(self, expr):
        '''
            Remove all edges whose name matches a given pattern
        '''
        # First, build a list of the good edges
        retained_edges = []

        R = re.compile('^(%s)$' % expr)

        for (e, s) in enumerate(self.__edge_to_label):
            if not R.match(s):
                retained_edges.append( (e, s) )
                pass
            pass

        retained_edges.sort()

        old_edge_set        = self.__edge_set
        old_edge_to_label   = self.__edge_to_label

        # re-initialize
        self.__init__()

        for (e,s) in retained_edges:
            for x in old_edge_set[e]:
                self.importEdge({x: [old_edge_to_label[e]]})
                pass
            pass
        pass


    def __makeVec(self, song_id):
        x = numpy.zeros(len(self.__edge_set))
        for enum in self.__vertex_to_edge[song_id]:
            x[enum] = 1.0
            pass
        return x

    def unlearn(self):
        self.__weights = numpy.ones_like(self.__weights)
        self.__weights /= numpy.sum(self.__weights)
        pass

    def playlistToMarkov(self, P):
        nStates     = len(self.__weights)
        nPlaylists  = len(P)
        nTrans      = sum(map(len, P)) - nPlaylists

        X0  = scipy.sparse.lil_matrix(  (nPlaylists,    nStates)    )
        Xt  = scipy.sparse.lil_matrix(  (nTrans,        nStates)    )
        Xp  = scipy.sparse.lil_matrix(  (nTrans,        nStates)    )

        r   = 0
        for pi in xrange(nPlaylists):
            # Initial state vector
            for enum in self.__vertex_to_edge[P[pi][0]]:
                X0[pi, enum] = 1.0 / self.__Z0[enum]
                pass
            pass

            for t in xrange(len(P[pi]) - 1):
                edgePrev    = self.__vertex_to_edge[P[pi][t]]
                edgeCur     = self.__vertex_to_edge[P[pi][t+1]]
                for enum in edgePrev:
                    Xp[r, enum] = 1.0
                    pass
                for enum in edgePrev & edgeCur:
                    Xt[r, enum] = 1.0 / self.__Zt[enum]
                    pass
                r += 1
                pass
            pass
        X0  = X0.tocsr()
        Xt  = Xt.tocsr()
        Xp  = Xp.tocsr()

        return (X0, Xt, Xp)

    def playlistToStateless(self, P):
        nStates     = len(self.__weights)
        nPlaylists  = len(P)
        nSongs      = sum(map(len, P))

        X0          = scipy.sparse.lil_matrix( (nSongs,    nStates)    )
        Xt          = []
        Xp          = []
        r           = 0

        for pi in xrange(nPlaylists):
            for t in xrange(len(P[pi])):
                for enum in self.__vertex_to_edge[P[pi][t]]:
                    X0[r, enum] = 1.0 / self.__Z0[enum]
                    pass
                r += 1
                pass
            pass
        X0  = X0.tocsr()
        return (X0, Xt, Xp)

    def learn(self, P, lam=1, a=1, DEBUG=-1, MARKOV=True, m=30, val=0.10, initialWeights=None, transOnly=False):
        '''
            Optimize the edge weights

            P:      list of vertex sequences [ [v1, v2, ... vk], [v1, v2, ... vl], ...]
            lam:    rate of the gamma weight prior (default: 1)
                    (lam=0 gives a dirichlet prior)
            a:      shape of the gamma weight prior (default: 1)
            val:    fraction of playlists to use for validation (default: 0.10)
            DEBUG:  show training output (default: -1)
        '''

        MIN_WEIGHT  =   1e-15

        if isinstance(lam, float) and lam < 0:
            raise ValueError('Rate parameter (lam) must be a non-negative scalar')
        if a <= 0:
            raise ValueError('Shape parameter (a) must be a positive scalar')

        def __ll_markov(w, X0, Xt, Xp, lam, a):
            # CREATED:2012-03-26 17:43:33 by Brian McFee <bmcfee@cs.ucsd.edu>
            #   inputs X0 Xt Xp are now sparse matrices

            ones        =   numpy.ones_like(w)
            nlists      =   X0.shape[0]
            ntrans      =   Xt.shape[0]
            d           =   len(w)

            f           =   numpy.sum(lam * w       - (a-1.0) * numpy.log(w))
            g           =   lam * ones              - (a-1.0) / w

            weightSum   =   numpy.sum(w)

            # Initial state likelihood
            #   P(x0 | w)           = sum_e P(x0 | e) P(e | w)
            #   -log P(x0 | w)      = - log sum_e [x0 in e] * Z0 * w_e  + log sum(w_e)
            #   grad[-log P(x0|w)]  = - [x0 in e] * Z0 * w_e /(sum_f [x0 in f] * w_f * Z0) + w_e / sum(w_f)

            if not transOnly:
                f           += nlists * numpy.log(weightSum)
                g           += nlists * ones / weightSum

                X0w         =   X0 * w
                f           += -numpy.sum(numpy.log(X0w))

                g           +=  -((1.0/X0w).T * X0)
                pass

            # Transition likelihoods
            #   P(x1 | x0, w)           = sum_e P(x1 | e, x0) P(e | x0, w)
            #   -log P(x1 | x0, w)      = -log sum_e [x1 in e] * [x0 in e] * Zt * w_e  + log sum_e [x0 in e] w_e
            #   grad[-log P(x1|x0,w)]   = -[x1 in e] * [x0 in e] * Zt * w_e / sum(prev) + [x0 in e] * w_e / sum(prev)
            Xtw         =   Xt * w
            Xpw         =   Xp * w
            f           +=  numpy.sum(numpy.log(Xpw)  -     numpy.log(Xtw))

            g           +=  (1.0/Xpw).T * Xp - (1.0/Xtw).T * Xt

            return (f, g)

        def __ll_stateless(w, X0, Xt, Xp, lam, a):
            ones        =   numpy.ones_like(w)
            nsongs      =   X0.shape[0]

            # Initial state likelihood
            #   P(x0 | w)           = sum_e P(x0 | e) P(e | w)
            #   -log P(x0 | w)      = - log sum_e [x0 in e] * Z0 * w_e  + log sum(w_e)
            #   grad[-log P(x0|w)]  = - [x0 in e] * Z0 * w_e /(sum_f [x0 in f] * w_f * Z0) + w_e / sum(w_f)

            f           =   numpy.sum(lam * w       - (a-1.0) * numpy.log(w))
            g           =   lam * ones              - (a-1.0) / w

            weightSum   =   numpy.sum(w)

            f           +=  nsongs * numpy.log(weightSum)
            g           +=  nsongs * ones / weightSum

            X0w         =   X0 * w
            f           += -numpy.sum(numpy.log(X0w))

            g           += -(1.0/X0w).T * X0
            return (f, g)


        bounds              = [(MIN_WEIGHT, None)] * len(self.__weights)

        # Pre-compute feature vectors
        if MARKOV:
            obj         = __ll_markov
            plprocess   = self.playlistToMarkov
        else:
            obj         = __ll_stateless
            plprocess   = self.playlistToStateless
            pass

        if initialWeights is not None:
            self.setWeights(initialWeights)
            w0 = self.__weights
        else:
            w0 = numpy.ones_like(self.__weights) / len(self.__weights)
            pass

        # Carve into train and validation
        nVal    = int(numpy.floor(val * len(P)))
        Pval    = P[:nVal]
        Ptrain  = P[nVal:]

        (X0, Xt, Xp)        = plprocess(Ptrain)


        if not isinstance(lam, list):
            lam = [lam]
            pass

        BEST_SCORE      = -numpy.inf
        BEST_LAM        = None

        for l in lam:
            w, f, d = scipy.optimize.fmin_l_bfgs_b(     func    =   obj,
                                                        x0      =   w0,
                                                        args    =   (X0, Xt, Xp, l, a),
                                                        fprime  =   None,
                                                        bounds  =   bounds,
                                                        m       =   m,
                                                        factr   =   1e7,
                                                        iprint  =   DEBUG)

            self.__weights  = w
            self.__weights  /= numpy.sum(self.__weights)
            if val > 0:
                score = self.avglikelihood(Pval)
            else:
                score = self.avglikelihood(Ptrain)
                pass
            if score > BEST_SCORE:
                BEST_SCORE      = score
                BEST_LAM        = l
                w0              = self.__weights
                pass
            pass

        self.__weights = w0
        if DEBUG >= 0:
            print 'Best lambda: %e' % BEST_LAM
        pass

    def loglikelihood(self, plist):
        '''
            Compute the log-likelihood of a playlist segment
            Output is normalized by length
        '''
        
        x0      = self.__makeVec(plist[0])
        # Update f
        xzw     = x0 * self.__weights / self.__Z0
        sxzw    = numpy.sum(xzw)
        ll      = numpy.log(sxzw) - numpy.log(numpy.sum(self.__weights))
        for next_song in plist[1:]:
            x1      = self.__makeVec(next_song)

            x0w     = x0 * self.__weights
            x01zw   = x0w * x1 / self.__Zt 

            sx01zw  = numpy.sum(x01zw)
            sx0w    = numpy.sum(x0w)

            # Update f
            ll      += numpy.log(sx01zw)   - numpy.log(sx0w)
            pass

        ll /= len(plist)
        return ll

    def loglikelihood_stateless(self, plist):
        '''
            Compute the stateless log-likelihood of a playlist segment
            Output is normalized by length
        '''
        
        ll = 0
        for x in plist:
            x0      = self.__makeVec(x)
            # Update f
            xzw     = x0 * self.__weights / self.__Z0
            sxzw    = numpy.sum(xzw)
            ll      += numpy.log(sxzw) - numpy.log(numpy.sum(self.__weights))

        ll /= len(plist)
        return ll

    def avglikelihood(self, P, MARKOV=True):
        if MARKOV:
            return numpy.mean(map(self.loglikelihood, P))
        else:
            return numpy.mean(map(self.loglikelihood_stateless, P))
        pass


    def showWeights(self, k=10):
        A = zip(self.__weights, self.__edge_to_label)
        A.sort(reverse=True)
        for (w, t) in A[:k]:
            print '%.4e: %s' % (w, t)
        pass

    def quadraticExpansion(self, MIN_SIZE=128, rho=0.5):
        '''
        quadratic edge expansion:
            construct edges by intersecting all pairs of edges
            for each pair E1, E2
                add edge E1*E2 <=> min(|E1|, |E2|) * rho > |E1*E2| >= MIN_SIZE
        '''
        Q   = {}
        for e1 in range(len(self.__edge_set)):
            se1 = self.__edge_size[e1]
            if se1 * rho < MIN_SIZE:
                continue
            for e2 in range(e1+1, len(self.__edge_set)):
                se2 = self.__edge_size[e2]
                if se2 * rho < MIN_SIZE:
                    continue
                newlabel    = self.__edge_to_label[e1] + '-&-' + self.__edge_to_label[e2]
                newedge     = self.__edge_set[e1] & self.__edge_set[e2]

                # First check to make sure we're shrinking
                # Second check to make sure the result is big enough
                if min(se1, se2) * rho > len(newedge) >= MIN_SIZE:
                    for v in newedge:
                        if v not in Q:
                            Q[v] = []
                            pass
                        Q[v].append(newlabel)
                    pass
                pass
            pass
        self.importEdge(Q)
        self.pruneEdges(MIN_SIZE)
        pass

    def getEdgeLabel(self, e):
        return self.__edge_to_label[e]


    def setWeights(self, W):
        '''
            Set the edge weights:
            W dict : edge labels -> weights
        '''
        for (label, weight) in W.iteritems():
            self.__weights[self.__label_to_edge[label]] = weight
            pass
        # Normalize
        self.__weights /= numpy.sum(self.__weights)
        pass

    def getWeights(self):
        '''
            Get the edge weights:
            returns W dict : edge labels -> weights
        '''
        W = {}
        for (e, w) in enumerate(self.__weights):
            W[self.__edge_to_label[e]] = w
            pass
        return W

    def sample(self, m=10):
        '''
        Sample a length-m playlist from the model
        '''

        def __categoricalSample(p):
            return numpy.argmax(numpy.random.multinomial(1,p))

        # Sample an intial edge set
        edges   = [__categoricalSample(self.__weights)]

        # Sample a song from the edge
        songs   = random.sample(self.__edge_set[edges[-1]], 1)

        for i in range(m):
            x0      = self.__makeVec(songs[-1])
            x0w     = x0 * self.__weights
            x0w     /= numpy.sum(x0w)

            # Sample the next edge
            edges.append(__categoricalSample(x0w))
            # Sample the next song
            songs.extend(random.sample(self.__edge_set[edges[-1]] - set([songs[-1]]), 1))
            pass

        return (songs, edges)

