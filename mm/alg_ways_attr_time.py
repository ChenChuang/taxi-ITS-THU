import sys
import operator
import time
import math
from scipy.stats import norm
import networkx as nx
import cctrack as ct
import ccpath as cp
import ccdagmodel as cdagm
import ccgraph as cg
import ccdb as cdb
from ccdef import *

import alg_bn as alg


intervals = [0.0, 1.0]
resolution = 0.1

ways_freq = None
ways_sf = None
ways_npick = None
ways_ndrop = None

ways_length = None

freq_tbname = "ways_freq"
sf_tbname = "ways_sf"
npick_tbname = "ways_npick"
ndrop_tbname = "ways_ndrop"

WAYS_NUM = 49122

def prepare(gw, isreaddb=True, icore=0): 
    def transpose(amat):
        return [[amat[i][j] for i in range(0,len(amat))] for j in range(0,len(amat[0]))]
   
    global ways_freq
    global ways_sf
    global ways_npick
    global ways_ndrop

    if not isreaddb:
        ways_freq = [[0 for j in range(WAYS_NUM)] for i in range(24)]
        ways_sf = [[[0 for k in range(10)] for j in range(WAYS_NUM)] for i in range(24)] 
        ways_npick = [[0 for j in range(WAYS_NUM)] for i in range(24)]
        ways_ndrop = [[0 for j in range(WAYS_NUM)] for i in range(24)]

    # read freq
    print "reading freq ...",
    if ways_freq is None:
        ways_freq = read_freq(icore) 

    # read sf
    print "reading sf ...",
    if ways_sf is None:
        ways_sf = read_sf(icore)    

    # read npick
    print "reading npick ...",
    if ways_npick is None:
        ways_npick = read_npick(icore) 
    
    # read ndrop
    print "reading ndrop ...",
    if ways_ndrop is None:
        ways_ndrop = read_ndrop(icore)

    # read ways' length
    print "reading length ..."
    global ways_length
    wdb = cdb.new_way_db()
    ways_length = wdb.read_attr('km')
    del wdb
    
    alg.prepare(gw)

def read_freq(icore=0, glo=True):
    global freq_tbname
    if icore > 0:
        tbname = freq_tbname + "_c" + str(icore)
    else:
        tbname = freq_tbname
    if glo:
        freq_tbname = tbname
    res = []
    wadb = cdb.new_way_attr_db(tbname = tbname)
    for i in range(0,24):
        res.append(wadb.read_attr('h%02d' % i))
    del wadb
    return res

def read_sf(icore=0, glo=True):
    def str2sf(ls_strs):
        return [map(int, strs.split(",")) for strs in ls_strs]

    global sf_tbname
    if icore > 0:
        tbname = sf_tbname + "_c" + str(icore)
    else:
        tbname = sf_tbname
    if glo:
        sf_tbname = tbname
    res = []
    wadb = cdb.new_way_attr_db(tbname = tbname)
    for i in range(0,24):
        res.append( str2sf( wadb.read_attr('h%02d' % i) ) )
    del wadb
    return res

def read_npick(icore=0, glo=True):
    global npick_tbname
    if icore > 0:
        tbname = npick_tbname + "_c" + str(icore)
    else:
        tbname = npick_tbname
    if glo:
        npick_tbname = tbname
    res = []
    wadb = cdb.new_way_attr_db(tbname = tbname)
    for i in range(0,24):
        res.append(wadb.read_attr('h%02d' % i))
    del wadb
    return res

def read_ndrop(icore=0, glo=True):
    global ndrop_tbname
    if icore > 0:
        tbname = ndrop_tbname + "_c" + str(icore)
    else:
        tbname = ndrop_tbname
    if glo:
        ndrop_tbname = tbname
    res = []
    wadb = cdb.new_way_attr_db(tbname = tbname)
    for i in range(0,24):
        res.append(wadb.read_attr('h%02d' % i))
    del wadb
    return res

def reduce_attrs(attrs, mi):
    if mi == 3:
        si = range(3, 25, 3)
    if mi == 4:
        si = range(-2+4, 25, 4)
    lj = len(attrs[0])
    try:
        lk = len(attrs[0][0])
        return [[[attrs[i-mi][j][k] + attrs[i-mi+1][j][k] + attrs[i-mi+2][j][k] for k in range(lk)] for j in xrange(lj)] for i in si]
    except:
        return [[attrs[i-mi][j] + attrs[i-mi+1][j] + attrs[i-mi+2][j] for j in xrange(lj)] for i in si]

def update_ways_attrs(path, track):
    global ways_freq
    global ways_sf
    global ways_npick
    global ways_ndrop
 
    h = track.mid_time('hour')
    wids = path.get_ways()
    ls = path.precise_length_by_wid(track.rds[0]['gps_lonlat'], track.rds[-1]['gps_lonlat'])
    path_length = sum(ls)

    s = intervals[0]
    resol = resolution
    max_s = intervals[1]

    for wid, l in zip(wids, ls):
        si = math.floor(s/resol)
        sw = s
        
        s = s + l/path_length
        
        ti = min(max_s/resol - 1, math.floor(s/resol))
        tw = s
       
        h = path.get_time_at((sw+tw) / 2 * path_length, 'h')
        ways_freq[h][wid-1] += 1
        for i in range(int(si), int(ti)+1):
            h = path.get_time_at((max(sw, i*resol) + min(tw, (i+1)*resol)) / 2 * path_length, 'h')
            ways_sf[h][wid-1][i] += 1

    h = track.orig_time('hour')
    ways_npick[h][wids[0]-1] += 1
    
    h = track.dest_time('hour')
    ways_ndrop[h][wids[-1]-1] += 1

def write_ways_attrs():
    # write freq
    print ""
    print "writing " + freq_tbname + " ...",
    wadb = cdb.new_way_attr_db(tbname = freq_tbname)
    wadb.update_attr_all(ways_freq)
    del wadb

    # write sf
    print ""
    print "writing " + sf_tbname + " ...",
    wadb = cdb.new_way_attr_db(tbname = sf_tbname)
    wadb.update_attr_all([[(("%s,"*10)[0:-1] % tuple(x)) for x in hx] for hx in ways_sf])
    del wadb

    # write npick
    print ""
    print "writing " + npick_tbname + " ...",
    wadb = cdb.new_way_attr_db(tbname = npick_tbname)
    wadb.update_attr_all(ways_npick)
    del wadb
    
    # write ndrop
    print ""
    print "writing " + ndrop_tbname + " ...",
    wadb = cdb.new_way_attr_db(tbname = ndrop_tbname)
    wadb.update_attr_all(ways_ndrop)
    del wadb

def result():
    return {'freq': ways_freq, \
            'sf': ways_sf, \
            'npick': ways_npick, \
            'ndrop': ways_ndrop}

def match(gw, track):
    print "   weekday %d, %d   " % (track.orig_time('weekday'), track.dest_time('weekday')),
    if track.orig_time('weekday') in [6,0] or track.dest_time('weekday') in [6,0]:
        return None

    p = alg.match(gw, track, is_projs=True) 
    if p is not None:
        update_ways_attrs(p, track)
        # update_ways_weight_proj(p, track)
    return p

def collect(core_num):
    def add2(m1, m2):
        for i in xrange(0,len(m1)):
            for j in range(0,len(m1[i])):
                m1[i][j] += m2[i][j]
        return m1
     
    def add3(m1, m2):
        for i in xrange(0,len(m1)):
            for j in range(0,len(m1[i])):
                for k in range(0,len(m1[i][j])):
                    m1[i][j][k] += m2[i][j][k]
        return m1   

    global ways_freq
    global ways_sf
    global ways_npick
    global ways_ndrop

    print "reading freq 0",
    ways_freq = read_freq(0) 

    print "reading sf 0",
    ways_sf = read_sf(0)    

    print "reading npick 0",
    ways_npick = read_npick(0) 
    
    print "reading ndrop 0",
    ways_ndrop = read_ndrop(0)


    for icore in range(1, core_num+1):
        ways_freq  = add2(ways_freq,  read_freq(icore, False)) 
        ways_sf    = add3(ways_sf,    read_sf(icore, False))
        ways_npick = add2(ways_npick, read_npick(icore, False))
        ways_ndrop = add2(ways_ndrop, read_ndrop(icore, False))

    write_ways_attrs()
