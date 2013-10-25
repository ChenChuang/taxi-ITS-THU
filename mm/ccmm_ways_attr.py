import sys
import datetime

import ccgraph as cg
import cctrack as ct
import ccpath as cp
import ccdb as cdb

import alg_ways_attr as alg

TRACKS_FROM_TID = 150001
TRACKS_TO_TID = 350000

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
    print (' start at ' + str(start_at) + ' ').center(70, '-')

    print 'preparing..',
    alg.prepare(gw)
    print 'end'

    tracks_num = 0
    paths_failed = 0

    start_match_at = datetime.datetime.now()
    print (' start matching at ' + str(start_match_at) + ' ').center(70, '-') 

    max_fetched = TRACKS_TO_TID
    while trd.fetched_num < max_fetched:
        if tracks_num >= TRACKS_TO_TID - TRACKS_FROM_TID + 1:
            break

        track = trd.fetch_one()

        if trd.fetched_num % 1000 == 0:
            print "fetched",trd.fetched_num
        if track is None:
            break
        if track.length() == 0 or track.tid < TRACKS_FROM_TID or track.tid > TRACKS_TO_TID:
            continue
        else:
            tracks_num += 1
        
        print "track",str(track.tid).ljust(10)," ",
        if not match(track):
            paths_failed += 1

    end_match_at = datetime.datetime.now()
    print (' end matching at ' + str(end_match_at) + ' ').center(70, '-'),'elapsed time',str(end_match_at - start_match_at)

    print "fetched tracks: %s, tracks in (%s, %s): %s, paths failed: %s" % (trd.fetched_num, TRACKS_FROM_TID, TRACKS_TO_TID, tracks_num, paths_failed)
    
    print ''.center(70, '-')

    print 'writing ways statistics..',
    alg.write_ways_attrs()
    print 'end'
    clear()

    end_at = datetime.datetime.now() 
    print (' end at ' + str(end_at) + ' ').center(70, '-'),'elapsed time',str(end_at - start_at)

def clear():
    print 'clearing..',
    global gw,trd
    del gw,trd
    print 'end'

if __name__ == "__main__":
    mm()

