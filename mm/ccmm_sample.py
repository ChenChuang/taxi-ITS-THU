import sys
import networkx as nx
import matplotlib.pyplot as plt
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

algs = {'bn':abn, 'st':ast, 'iv':aiv, 'uti':auti}
## algs = {'uti':auti}
intervals = [2,4,6,8]

track_tbname = "taxi_tracks_gt_1"
path_tbname = "taxi_paths_gt_1"
result_fname = "sample_gt_1.txt"

tids = []
## tids = [84]
## tids = [28,69,96,97,451,464,476,477,479,481,483,501,505,548,550,658,662,691,724,727,735,768,891,940]
## tids = [28,69,96,97,464,476,477,479,483,505,548,550,662,691,724,727,735,768]

def mm(gw, trd, method, tid, interval):

    alg = algs[method]

    pt2j = cj.new_pt2geojson(method = method)

    track = trd.fetch_by_id(tid)
    if interval > 1:
        track.sample(interval)
        path = alg.match(gw, track)
        if path is not None:
            pt2j.write_p_geojson(path, sample=interval)
    else:
        path = alg.match(gw, track)
        if path is not None:
            pt2j.write_p_geojson(path)

    return path
    #return None


matched_length = {}
missed_length  = {}
false_length   = {}

def compare():
    gw = cg.new_gw()
    trd = cdb.new_track_reader(tbname = track_tbname, offset = 0)
    # trd = cdb.new_track_reader(offset = 0)
    prd = cdb.new_path_reader(gw = gw, tbname = path_tbname)
    # prd = cdb.new_path_reader(gw=gw, tbname="taxi_paths_truth")


    global tids
    tids = prd.get_all_tids()

    global matched_length, missed_length, false_length

    matched_length = {}
    missed_length  = {}
    false_length   = {}
   
    for method in algs.iterkeys():
        matched_length[method] = {}
        missed_length[method] = {}
        false_length[method] = {}
        for interval in intervals:
            matched_length[method][interval] = []
            missed_length[method][interval] = []
            false_length[method][interval] = []

    for method in algs.iterkeys():
        alg = algs[method]
        alg.prepare(gw)
        for tid in tids:
            print method,tid,
            gt_path = prd.fetch_path_by_tid(tid)
            for interval in intervals:
                print interval,
                
                try:
                    path = mm(gw, trd, method, tid, interval)
                except:
                    path = None

                if path is None:
                    print "failed"
                    continue
                result = path.compare(gt_path)

                matched_length[method][interval].append(result['matched_length'])
                missed_length[method][interval].append(result['missed_length'])
                false_length[method][interval].append(result['false_length'])
            print ""

        with open(result_fname, 'a') as f:
            for interval in intervals:
                f.write(' '.join([
                    method, 
                    str(interval), 
                    str(sum(matched_length[method][interval])), 
                    str(sum(missed_length[method][interval])), 
                    str(sum(false_length[method][interval])), '\n']))

    for method in algs.iterkeys():
        for interval in intervals:
            print method,interval,
            print sum(matched_length[method][interval]),
            print sum(missed_length[method][interval]),
            print sum(false_length[method][interval])
             

if __name__ == "__main__":
    compare()


