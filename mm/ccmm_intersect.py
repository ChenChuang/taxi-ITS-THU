import sys
import datetime

import ccgraph as cg
import cctrack as ct
import ccpath as cp
import ccgeojson as cj
import ccdb as cdb
from ccdef import *

import alg_bn as abn

TRACKS_FROM_ROW = 1
TRACKS_TO_ROW = -1

# There are 2638410 tracks in table taxi_tracks, id from 1-2638410
TRACKS_FROM_TID = 1
TRACKS_TO_TID = 2638410

TID_DP_TBNAME = "taxi_tid_dp_1"

METHOD = 'bn'
alg = abn

gw = cg.new_gw()
trd = cdb.new_track_reader_for_purpose(purpose="mm")
pwd = cdb.new_path_writer_for_method(method = METHOD)
pawd = cdb.new_path_attr_writer_for_method(method = METHOD)
tdpdb = cdb.new_tid_dp_db(tbname=TID_DP_TBNAME)
pt2j = cj.new_pt2geojson(method = METHOD)

req_nodes = [19808,12055,19800,19943,28533,19804,19801,23737,23736,23739]

def rect_of_nodes(nodes, r=1):
    latgap = cg.km2latgap(r)
    longap = cg.km2longap(r, 39.0)
    min_lon = INF
    min_lat = INF
    max_lon = -INF
    max_lat = -INF
    for v in nodes:
        (lon, lat) = gw.nodes_pos[v]
        min_lon = min(min_lon, lon)
        max_lon = max(max_lon, lon)
        min_lat = min(min_lat, lat)
        max_lat = max(max_lat, lat)
    return (min_lon - longap, min_lat - latgap, max_lon + longap, max_lat + latgap)

def is_intersect(a, b):
    vs = [(a[0],a[1]), (a[0],a[3]), (a[2],a[1]), (a[2],a[3])]
    for (lon, lat) in vs:
        if b[0] <= lon <= b[2] and b[1] <= lat <= b[3]:
            return True
    vs = [(b[0],b[1]), (b[0],b[3]), (b[2],b[1]), (b[2],b[3])]
    for (lon, lat) in vs:
        if a[0] <= lon <= a[2] and a[1] <= lat <= a[3]:
            return True
    return False

def is_path_contains(path, nodes):
    es = path.get_es()
    vs = [e[0] for e in es]
    vs.append(es[-1][1])
    for v in nodes:
        if v in vs:
            return True
    return False

def match(track):
        
    print "t2json..",
    pt2j.write_t_geojson(track)
    
    print "Matching..",
    path = alg.match(gw, track)

    if path is not None:  
        if not is_path_contains(path, req_nodes):
            print "invalid path"
            return False

        print "p2db..",
        pwd.insert(path)
        pawd.insert(path, track)
        tdpdb.insert(path.tid)

        print "p2json..",
        pt2j.write_p_geojson(path)

        print "end   ",    
        path.summary()
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

    print ''.center(70, '-')
    req_rect = rect_of_nodes(req_nodes)
    print ''.center(70, '-')

    tracks_num = 0
    tracks_invalid_num = 0
    paths_failed = 0
    paths_succeed = 0
    max_fetched = TRACKS_TO_ROW - TRACKS_FROM_ROW + 1

    start_match_at = datetime.datetime.now()
    print (' start matching at ' + str(start_match_at) + ' ').center(70, '-') 

    while TRACKS_TO_ROW < 0 or trd.fetched_num < max_fetched:
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
        

        t_rect = track.rect()
        if not is_intersect(req_rect, t_rect):
            tracks_invalid_num += 1
            # print "invalid rect",str(t_rect)
            continue
        else:
            print "track",str(track.tid).ljust(10)," ",

        if not match(track):
            paths_failed += 1
        else:
            paths_succeed += 1

        ## if METHOD == "UT":
            ## aut.update_graph(tracks_num, gw)

    end_match_at = datetime.datetime.now()
    print (' end matching at ' + str(end_match_at) + ' ').center(70, '-'),'elapsed time',str(end_match_at - start_match_at)

    print "fetched tracks: %s, \ntracks in (%s, %s): %s, \ntracks invalid: %s, \npaths failed: %s, \npaths succeed: %s" % \
            (trd.fetched_num, TRACKS_FROM_TID, TRACKS_TO_TID, tracks_num, tracks_invalid_num, paths_failed, paths_succeed)
    
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
