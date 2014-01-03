import sys
import datetime

import ccgraph as cg
import cctrack as ct
import ccpath as cp
import ccgeojson as cj
import ccdb as cdb

import alg_uti as alg

from_tid = 1
to_tid = 10000000
max_fetched = 10000

method = 'uti'

gw = cg.new_gw()
trd = cdb.new_track_reader(tbname = "taxi_tracks_gt_1")
pwd = cdb.new_path_writer(tbname = "taxi_paths_gt_1")
pawd = cdb.new_path_attr_writer(tbname = "taxi_paths_gt_1_attr")
pt2j = cj.new_pt2geojson(method = method)

def match(track):
    print "Matching..",
    path = alg.match(gw, track)

    if path is not None and path.is_valid():
        print "p2db..",
        pwd.insert_update(path)
        pawd.insert_update(path, track)

        print "p2json..",
        pt2j.write_p_geojson(path)

        print "end   ",    
        path.summary()
        print ""
        return True
    else:
        print ""
        return False

def mm():
    print ''
    print 'generating ground truth','----','method',method,'----'
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

    while max_fetched < 0 or trd.fetched_num < max_fetched:
        if tracks_num >= to_tid - from_tid + 1:
            break

        track = trd.fetch_one()

        if trd.fetched_num % 1000 == 0:
            print "fetched",trd.fetched_num
        if track is None:
            break
        if track.length() == 0 or track.tid < from_tid or track.tid > to_tid:
            continue
        else:
            tracks_num += 1
        
        print "track",str(track.tid).ljust(10)," ",
        if not match(track):
            paths_failed += 1

    end_match_at = datetime.datetime.now()
    print (' end matching at ' + str(end_match_at) + ' ').center(70, '-'),'elapsed time',str(end_match_at - start_match_at)

    print "fetched tracks: %s, tracks in (%s, %s): %s, paths failed: %s" % (trd.fetched_num, from_tid, to_tid, tracks_num, paths_failed)
    
    print ''.center(70, '-')

    clear()

    end_at = datetime.datetime.now()
    print (' end at ' + str(end_at) + ' ').center(70, '-'),'elapsed time',str(end_at - start_at)

def clear():
    print 'clearing..',
    global gw,trd,pwd,pawd,pt2j
    del gw,trd,pwd,pawd,pt2j
    print 'end'

if __name__ == "__main__":
    mm()
    if hasattr(alg, 'summary'):
        alg.summary.printme()

