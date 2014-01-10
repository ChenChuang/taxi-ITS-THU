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
intervals = [2,3,4,5,6,7,8]

a = [x/2.0 for x in range(0,20)]
breaks = zip(a[:-1],a[1:])

track_tbname = "taxi_tracks"
# path_tbname = "taxi_paths_gt_1"
path_tbname = "taxi_paths_truth"
result_fname = "sample_result_4.txt"

## tids = []
## tids = [84]
tids = [28,69,96,97,451,464,476,477,479,481,483,501,505,548,550,658,662,691,724,727,735,768,891,940]
## tids = [28,69,96,97,464,476,477,479,483,505,548,550,662,691,724,727,735,768]

def mm(gw, trd, method, track, interval):
    alg = algs[method]
    path = alg.match(gw, track)
    return path


matched_length = {}
missed_length  = {}
false_length   = {}

def in_break(x):
    for b in breaks:
        if x >= b[0] and x <= b[1]:
            return b
    return breaks[-1]

def compare():
    gw = cg.new_gw()
    trd = cdb.new_track_reader(tbname = track_tbname, offset = 0)
    # trd = cdb.new_track_reader(offset = 0)
    prd = cdb.new_path_reader(gw = gw, tbname = path_tbname)
    # prd = cdb.new_path_reader(gw=gw, tbname="taxi_paths_truth")


    # global tids
    # tids = prd.get_all_tids()

    global matched_length, missed_length, false_length

    matched_length = {}
    missed_length  = {}
    false_length   = {}
   
    for method in algs.iterkeys():
        matched_length[method] = {}
        missed_length[method] = {}
        false_length[method] = {}
        for b in breaks:
            matched_length[method][b] = []
            missed_length[method][b] = []
            false_length[method][b] = []

    for method in algs.iterkeys():
        alg = algs[method]
        alg.prepare(gw)
        for tid in tids:
            print method,tid,
            gt_path = prd.fetch_path_by_tid(tid)
            for interval in intervals:
                print interval,': s =',
                
                for s in range(0,interval):
                    print s,
                    track = trd.fetch_by_id(tid)
                    track.sample(interval, s)
                    if len(track.rds) < 3:
                        continue
                    try:
                        path = mm(gw, trd, method, track, interval)
                    except:
                        path = None

                    if path is None:
                        print "failed"
                        continue
                    result = path.compare(gt_path)

                    b = in_break(track.max_d())
                    matched_length[method][b].append(result['matched_length'])
                    missed_length[method][b].append(result['missed_length'])
                    false_length[method][b].append(result['false_length'])
                print ':',
            print ""

    with open(result_fname, 'a') as f:
        for method in algs.iterkeys():
            for b in breaks:
                f.write(' '.join([
                    method, 
                    str(b[0]),
                    str(b[1]),
                    str(sum(matched_length[method][b])), 
                    str(sum(missed_length[method][b])), 
                    str(sum(false_length[method][b])), '\n']))

    for method in algs.iterkeys():
        for b in breaks:
            print method,b[0],b[1],
            print sum(matched_length[method][b]),
            print sum(missed_length[method][b]),
            print sum(false_length[method][b])
             

if __name__ == "__main__":
    compare()


