import sys
import datetime
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
intervals = range(1, 20)

result_fname = "sample_compare_result_2.txt"

def mm(gw, trd, method, tid, start, interval):

    alg = algs[method]

    pt2j = cj.new_pt2geojson(method = method)

    print "Sampling..",
    track = trd.fetch_by_id(tid)
    if interval > 1:
        track.sample(interval, start)
    print "t2json..",
    pt2j.write_t_geojson(track, start, interval)
    
    print "Matching..",
    path = alg.match(gw, track)
    if path is not None:
        print "p2json..",
        pt2j.write_p_geojson(path, start, interval)
    return path


matched_length = {}
missed_length  = {}
false_length   = {}

def compare():
    start_at = datetime.datetime.now()
    print ""
    print (' start at ' + str(start_at) + ' ').center(70, '-')
    print ""

    gw = cg.new_gw()
    trd = cdb.new_track_reader(offset = 0)
    prd = cdb.new_path_reader(gw=gw, tbname="taxi_paths_truth")

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
            gt_path = prd.fetch_path_by_tid(tid)
            for interval in intervals:
                for start in xrange(0, interval):
                    print method.ljust(3), "tid =", str(tid).ljust(5), "s =", str(start).ljust(2), "i =", str(interval).ljust(2),
                
                    try:
                        path = mm(gw, trd, method, tid, start, interval)
                    except Exception, e:
                        path = None

                    if path is None:
                        print "Failed"
                        continue
                    else:
                        path.summary()
                        print ""
                    result = path.compare(gt_path)

                    matched_length[method][interval].append(result['matched_length'])
                    missed_length[method][interval].append(result['missed_length'])
                    false_length[method][interval].append(result['false_length'])

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

    end_at = datetime.datetime.now()
    print ""
    print (' end at ' + str(end_at) + ' ').center(70, '-'),'elapsed time',str(end_at - start_at)
    print ""


if __name__ == "__main__":
    compare()


