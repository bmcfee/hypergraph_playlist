#!/usr/bin/env python
'''
CREATED:2012-03-21 20:12:02 by Brian McFee <bmcfee@cs.ucsd.edu>

Usage: ./buildTagmatrix.py data_tags.pickle playlistSet.pickle /1mil/ 
'''

import sys, os, numpy
import cPickle as pickle
import pprint
import sqlite3

def getVocab(dbc):
    vocab = []
    cur = dbc.cursor()
    cur.execute('''SELECT tag FROM tags''')
    for (term,) in cur:
        vocab.append(term)
        pass
    return vocab

def getTrackIds(song_ids, basedir):

    track_ids = {}

    with open('%s/AdditionalFiles/unique_tracks.txt' % basedir, 'r') as f:
        for line in f:
            (t, s, artist, title) = line.strip().split('<SEP>', 4)
            if s in song_ids:
                track_ids[s] = t
            pass

    return track_ids

def getTrackRows(dbc, track_ids):

    cur         = dbc.cursor()
    tid         = {}
    cur.execute('''SELECT tid FROM tids''')
    for (i, (track,)) in enumerate(cur, 1):
        tid[track] = i
        pass
    return tid


def getTags(dbc, tid, track_id, vocab):
    cur = dbc.cursor()

    terms = []
    if track_id in tid:
        cur.execute('''SELECT tag FROM tid_tag WHERE tid = ? AND val > 0 ORDER BY val DESC limit 10''', (tid[track_id],))
        for (tag,) in cur:
            terms.append(vocab[tag-1])
    return terms


def crunchData(dbc, basedir, p_playlist, p_output):

    print 'Loading songs'
    with open(p_playlist, 'r') as f:
        song_ids = pickle.load(f)['songs']
        pass

    print 'Mapping to track ids'
    track_ids   = getTrackIds(song_ids, basedir)
    print 'Mapping to row numbers'
    tid         = getTrackRows(dbc, track_ids)

    print 'Building vocabulary'
    vocab       = getVocab(dbc)

    print 'Loading data'
    data = {}
    for (i, s) in enumerate(song_ids):
        print '%6d/%6d %s' % (i, len(song_ids), s)
        TAGS = getTags(dbc, tid, track_ids[s], vocab)
        if len(TAGS) > 0:
            data[s] = TAGS
            pass
        pass

    print 'Saving'
    with open(p_output, 'w') as f:
        pickle.dump({'X': data}, f)
        pass
    print 'Done'
    pass

if __name__ == '__main__':
    with sqlite3.connect(sys.argv[3] + '/AdditionalFiles/lastfm_tags.db') as dbc:
        crunchData(dbc, sys.argv[3], sys.argv[2], sys.argv[1])
    pass
