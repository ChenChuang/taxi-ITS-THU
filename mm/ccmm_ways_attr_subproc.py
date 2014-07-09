import sys
import datetime

import ccgraph as cg
import cctrack as ct
import ccpath as cp
import ccdb as cdb

import alg_ways_attr_time as alg

def match(track):
    
    path = alg.match(gw, track)

    if path is not None:
        return True
    else:
        return False

def mm():
    start_at = datetime.datetime.now()
    print 'core ' + str(ICORE) + ':' + (' start at ' + str(start_at) + ' ').center(70, '-')

    print 'core ' + str(ICORE) + ':' + 'preparing..'
    alg.prepare(gw, isreaddb = True, icore = ICORE)

    tracks_succ = 0
    tracks_failed = 0
    paths_failed = 0

    for track in trd.tracks_between(TRACKS_FROM_TID, TRACKS_TO_TID):
        print 'core' + str(ICORE) + ':' + "track " + str(track.tid).ljust(10)
        if track is None or track.length() == 0:
            tracks_failed += 1
            continue
        else:
            tracks_succ += 1
        try:
            if not match(track):
                paths_failed += 1
        except:
            paths_failed += 1

    end_match_at = datetime.datetime.now()

    print 'core ' + str(ICORE) + ':' + " %s succ tracks, %s failed tracks in (%s, %s), paths failed: %s" % (tracks_succ, tracks_failed, TRACKS_FROM_TID, TRACKS_TO_TID, paths_failed)
    print 'core ' + str(ICORE) + ':' + 'writing ways statistics..'
#     alg.write_ways_attrs()
    clear()

    end_at = datetime.datetime.now() 
    print 'core ' + str(ICORE) + ':' + (' end at ' + str(end_at) + ' ').center(70, '-'),'elapsed time',str(end_at - start_at)

def clear():
    print 'core ' + str(ICORE) + ':' + 'clearing..',
    global gw,trd
    del gw,trd
    print 'end'

if __name__ == "__main__":
    if len(sys.argv) != 4:
        exit(-1)
    ICORE = int(sys.argv[1])
    TRACKS_FROM_TID = int(sys.argv[2])
    TRACKS_TO_TID = int(sys.argv[3])
   
    print 'core ' + str(ICORE) + ':' + ''.center(70, '-')
    print 'core ' + str(ICORE) + ':' + " from %s to %s" % (TRACKS_FROM_TID, TRACKS_TO_TID)
    print 'core ' + str(ICORE) + ':' + ''.center(70, '-')

    gw = cg.new_gw()
    trd = cdb.new_track_reader_for_purpose(purpose="mm")
    
    mm()



