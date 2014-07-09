import sys
import datetime

import ccgraph as cg
import cctrack as ct
import ccpath as cp
import ccdb as cdb

import alg_ways_attr_time as alg

def mm(params):
    icore = params[0]
    TRACKS_FROM_TID = params[1]
    TRACKS_TO_TID = params[2]
    
    print ''
    gw = cg.new_gw()
    trd = cdb.new_track_reader_for_purpose(purpose="mm")

    start_at = datetime.datetime.now()
    print ('core ' + str(icore) + ':' + ' start at ' + str(start_at) + ' ').center(70, '-')

    print 'core ' + str(icore) + ':' + 'preparing..',
    alg.prepare(gw, False)
    print 'end'

    tracks_num = 0
    paths_failed = 0

    start_match_at = datetime.datetime.now()
    print ('core ' + str(icore) + ':' + ' start matching at ' + str(start_match_at) + ' ').center(70, '-') 

    max_fetched = TRACKS_TO_TID
    while trd.fetched_num < max_fetched:
        if tracks_num >= TRACKS_TO_TID - TRACKS_FROM_TID + 1:
            break

        track = trd.fetch_one()

        if trd.fetched_num % 1000 == 0:
            print 'core ' + str(icore) + ':' + "fetched",trd.fetched_num
        if track is None:
            break
        if track.length() == 0 or track.tid < TRACKS_FROM_TID or track.tid > TRACKS_TO_TID:
            continue
        else:
            tracks_num += 1
        
        print 'core ' + str(icore) + ':' + "track",str(track.tid).ljust(10)," ",
        try:
            print "Matching..",
            path = alg.match(gw, track)

            if path is not None:
                print "end   ",    
                path.summary()
                print ""
            else:
                print ""
                paths_failed += 1
        except:
            print ""
            paths_failed += 1

    end_match_at = datetime.datetime.now()
    print ('core ' + str(icore) + ':' + ' end matching at ' + str(end_match_at) + ' ').center(70, '-'),'elapsed time',str(end_match_at - start_match_at)

    print 'core ' + str(icore) + ':' + "fetched tracks: %s, tracks in (%s, %s): %s, paths failed: %s" % (trd.fetched_num, TRACKS_FROM_TID, TRACKS_TO_TID, tracks_num, paths_failed)

    end_at = datetime.datetime.now() 
    print ('core ' + str(icore) + ':' + ' end at ' + str(end_at) + ' ').center(70, '-'),'elapsed time',str(end_at - start_at)

    print 'core ' + str(icore) + ':' + 'clearing..',
    del gw,trd
    print 'end'

    return alg.result()
