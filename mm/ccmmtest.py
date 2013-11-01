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

algs = {'bn':abn, 'st':ast, 'iv':aiv, 'ut':aut, 'uti':auti}

def mm(tid, method, interval=1):
    alg = algs[method]

    gw = cg.new_gw()
    trd = cdb.new_track_reader(offset = 0)
    pwd = cdb.new_path_writer_for_method(method = method)
    pt2j = cj.new_pt2geojson(method = method)

    track = trd.fetch_by_id(tid)
    track.sample(interval)
    track.summary()
    pt2j.write_t_geojson(track)

    alg.prepare(gw)

    path = alg.match(gw, track)

    pt2j.write_p_geojson(path)

    # pwd.insert_update(path)

    path.summary()

    del trd,pwd

    return path

