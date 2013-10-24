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

ways_weight = None
ways_used_times = None
ways_used_interval = None

ways_length = None

ways_attrs_tbname = "ways_ut_attr_2"

def prepare(gw):
    def used_intervals2ints(ls_strs):
        return [map(int, strs.split(",")) for strs in ls_strs]
    
    global ways_weight
    global ways_used_times
    global ways_used_interval

    wadb = cdb.new_way_attr_db(tbname=ways_attrs_tbname)
    ways_weight = wadb.read_attr('weight')
    ways_used_times = wadb.read_attr('used_times')
    ways_used_interval = used_intervals2ints(wadb.read_attr('used_interval'))
    del wadb

    global ways_length

    wdb = cdb.new_way_db()
    ways_length = wdb.read_attr('km')
    del wdb
    
    alg.prepare(gw)

def update_ways_attrs(path, track):
    global ways_weight
    global ways_used_times
    global ways_used_interval
    
    wids = path.get_ways()
    conf = path.confidence(track)

    s = intervals[0]
    resol = resolution
    max_s = intervals[1]
    path_length = path.length()

    for wid in wids:
        ways_weight[wid-1] += conf
        ways_used_times[wid-1] += 1
        
        l = ways_length[wid-1]
        si = math.floor(s/resol)
        s = s + l/path_length
        ti = min(max_s/resol - 1, math.floor(s/resol))
        for i in range(int(si), int(ti)+1):
            ways_used_interval[wid-1][i] += 1

    # deprecated
def update_ways_attrs_proj(path, track):
    global ways_weight
    global ways_used_times
    ways_ds = path.get_ways_ds_proj(track)
    conf = path.confidence()
    for (wid, d) in ways_ds:
        ways_weight[wid-1] += conf / d
        ways_used_times[wid-1] += 1

def write_ways_attrs():
    wadb = cdb.new_way_attr_db(tbname=ways_attrs_tbname)
    wadb.update_attr("weight", ways_weight)
    wadb.update_attr("used_times", ways_used_times)
    ways_used_interval_strs = [str(x)[1:-1].replace(" ","") for x in ways_used_interval]
    wadb.update_attr("used_interval", ways_used_interval_strs)
    del wadb

def init_ways_attrs_tb():
    wadb = cdb.new_way_attr_db(tbname=ways_attrs_tbname)
    interval_num = int((intervals[1] - intervals[0]) / resolution)
    wadb.init_tb(attrs_values={"used_times":0, "weight":0, "used_interval":','.join(['0']*intervals_num)})
    del wadb

def match(gw, track):
    p = alg.match(gw, track) 
    if p is not None:
        update_ways_attrs(p, track)
        # update_ways_weight_proj(p, track)
    return p


