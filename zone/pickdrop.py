import psycopg2 as pg
import psycopg2.extras as pgextras

import datetime
import random
import math

import ccdbzone as cdbz

import sys, os
mmpath = os.path.join(os.getcwd(), '..', 'mm')
sys.path.insert(0, mmpath)
import ccgraph as cg
import cctrack as ct
import ccdb as cdb
del sys.path[0]

gw = cg.new_gw()
trd = cdb.new_track_reader_for_purpose(purpose="mm")
wpd = cdbz.WayPickDropDB()
maxr = 0.2

nw = 49122
# [wp, wd] = wpd.read_picks_drops()
wp = [0] * nw
wd = [0] * nw

for tid in xrange(0, 200000):
    print tid,
    track = trd.fetch_by_id(tid)
    if track is None:
        print ""
        continue
    
    p_proj = gw.find_projs_nearest(track.rds[0]['gps_lonlat'], maxr)
    if p_proj is not None:
        p_wid = gw.G[p_proj['s']][p_proj['t']]['way_id']
        wp[p_wid-1] = wp[p_wid-1] + 1

    d_proj = gw.find_projs_nearest(track.rds[-1]['gps_lonlat'], maxr)
    if d_proj is not None:
        d_wid = gw.G[d_proj['s']][d_proj['t']]['way_id']
        wd[d_wid-1] = wd[d_wid-1] + 1

    print p_wid, d_wid

wpd.update_picks_drops(wp, wd)
