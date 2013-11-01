import sys
import datetime

import ccgraph as cg
import cctrack as ct
import ccpath as cp
import ccgeojson as cj
import ccdb as cdb

import alg_bn as abn
import alg_st as ast
import alg_iv as aiv
import alg_ut as aut
import alg_uti as auti

import networkx as nx
#import matplotlib.pyplot as plt

TRACKS_FROM_ROW = 1
TRACKS_TO_ROW = 1000

TRACKS_FROM_TID = 1
TRACKS_TO_TID = 1000

#METHOD = 'bn'
#METHOD = 'st'
METHOD = 'iv'
#METHOD = 'ut'
#METHOD = 'uti'

algs = {'bn':abn, 'st':ast, 'iv':aiv, 'ut':aut, 'uti':auti}
alg = algs[METHOD]

gw = cg.new_gw()
trd = cdb.new_track_reader_for_purpose(purpose="mm")
pwd = cdb.new_path_writer_for_method(method = METHOD)
pawd = cdb.new_path_attr_writer_for_method(method = METHOD)
pt2j = cj.new_pt2geojson(method = METHOD)

def match(track):
    # print "t2json..",
    # pt2j.write_t_geojson(track)
    
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
    start_at = datetime.datetime.now()
    print (' start at ' + str(start_at) + ' ').center(70, '-')

    print 'preparing..',
    alg.prepare(gw)
    print 'end'

    tracks_num = 0
    paths_failed = 0
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
        
        print "track",str(track.tid).ljust(10)," ",
        if not match(track):
            paths_failed += 1

        ## if METHOD == "UT":
            ## aut.update_graph(tracks_num, gw)

    end_match_at = datetime.datetime.now()
    print (' end matching at ' + str(end_match_at) + ' ').center(70, '-'),'elapsed time',str(end_match_at - start_match_at)

    print "fetched tracks: %s, tracks in (%s, %s): %s, paths failed: %s" % (trd.fetched_num, TRACKS_FROM_TID, TRACKS_TO_TID, tracks_num, paths_failed)
    
    print ''.center(70, '-')

    if METHOD == "UT":
        # print 'writing ways statistics..',
        # aut.write_ways_attrs()
        # print 'end'
        pass
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
    alg.summary.printme()

