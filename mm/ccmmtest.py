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


algs = {'BN':abn, 'ST':ast, 'IV':aiv, 'UT':aut}

def mm(tid, method):
    alg = algs[method]

    gw = cg.new_gw()
    trd = cdb.new_track_reader(offset = 0)
    pwd = cdb.new_path_writer_for_method(method = method)
    pt2j = cj.new_pt2geojson(method = method)

    track = trd.fetch_by_id(tid)
    track.summary()
    pt2j.write_t_geojson(track)

    alg.prepare(gw)

    path = alg.match(gw, track)

    pt2j.write_p_geojson(path)

    if METHOD != 'UT':
        vds = dag.nodes(True)
        vdsd = {}
        for vd in vds:
            vdsd[vd[0]] = vd[1]

    ## pwd.insert_update(path)

    path.summary()

    del trd,pwd

    return path

