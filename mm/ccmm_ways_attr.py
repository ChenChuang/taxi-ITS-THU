import sys
import datetime

import ccgraph as cg
import cctrack as ct
import ccpath as cp
import ccdb as cdb

import alg_ways_attr_time as alg

# First Round
# TRACKS_FROM_TID = 150001
# TRACKS_TO_TID = 350000

# Second Round
ICORE = 3

TRACKS_FROM_TID = 3500001
TRACKS_TO_TID =   4561311


gw = cg.new_gw()
trd = cdb.new_track_reader_for_purpose(purpose="mm")

# alg.init_ways_attrs_tb()

def match(track):
    
    print "Matching..",
    path = alg.match(gw, track)

    if path is not None:
        print "end   ",    
        path.summary()
        print ""
        return True
    else:
        print ""
        return False

def mm():
    print ''
    start_at = datetime.datetime.now()
    print 'core ' + str(ICORE) + ':' + (' start at ' + str(start_at) + ' ').center(70, '-')

    print 'core ' + str(ICORE) + ':' + 'preparing..',
    alg.prepare(gw, isreaddb = True, icore = ICORE)
    print 'end'

    tracks_succ = 0
    tracks_failed = 0
    paths_failed = 0

    start_match_at = datetime.datetime.now()
    print 'core ' + str(ICORE) + ':' + (' start matching at ' + str(start_match_at) + ' ').center(70, '-') 

    for track in trd.tracks_between(TRACKS_FROM_TID, TRACKS_TO_TID):
        if track is None or track.length() == 0:
            print "track failed", track.tid
            tracks_failed += 1
            continue
        else:
            tracks_succ += 1
            print 'core ' + str(ICORE) + ':' + "track",str(track.tid).ljust(10)," ",
        try:
            if not match(track):
                paths_failed += 1
        except:
            print ""
            paths_failed += 1

    end_match_at = datetime.datetime.now()
    print 'core ' + str(ICORE) + ':' + (' end matching at ' + str(end_match_at) + ' ').center(70, '-'),'elapsed time',str(end_match_at - start_match_at)

    print 'core ' + str(ICORE) + ':' + " %s succ tracks, %s failed tracks in (%s, %s), paths failed: %s" % (tracks_succ, tracks_failed, TRACKS_FROM_TID, TRACKS_TO_TID, paths_failed)
    
    print 'core ' + str(ICORE) + ':' + ''.center(70, '-')

    print 'core ' + str(ICORE) + ':' + 'writing ways statistics..',
    alg.write_ways_attrs()
    print 'end'
    clear()

    end_at = datetime.datetime.now() 
    print 'core ' + str(ICORE) + ':' + (' end at ' + str(end_at) + ' ').center(70, '-'),'elapsed time',str(end_at - start_at)

def clear():
    print 'core ' + str(ICORE) + ':' + 'clearing..',
    global gw,trd
    del gw,trd
    print 'end'

if __name__ == "__main__":
    mm()

