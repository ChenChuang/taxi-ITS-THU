import networkx as nx
import cctrack as ct
import ccpath as cp
import ccdagmodel as cdagm
from ccdef import *

gdag = None
gpdag = list()
ges = list()


def prepare(gw):
    pass

def match(gw, track, debug = False):
    dag = create_dag(gw, track)
    if dag is None:
        print 'failed creating DAG',
        return None
    p_dag = cdagm.shortest_path_dag(dag, init_weight_with, combine_weight_with)
    if p_dag is None:
        print 'failed finding path in DAG',
        return None
    es = cdagm.pdag2es(dag, p_dag)
    if es is None:
        print 'failed generating edge list in Graph'
        return None
    p = cp.new_path_from_es(gw, track.tid, es)
    if p is None:
        print 'failed creating Path instance'
        return None
    if debug:
        global gdag
        gdag = dag.copy()
        global gpag
        gpdag = list(p_dag)
        global ges
        ges = list(es)
    return p

def create_dag(gw, track, r=0.1):
    dag = nx.DiGraph()
    rds = list(track.rds)
    projss = []

    # for every gps-record in track, find its valid projection candidates
    for rd in rds:
        lonlat_rds = rd['gps_lonlat']
        projs = gw.find_projs_within(lonlat_rds, r)
        # if no projection candidates found, remove the gps-record from track
        if not len(projs) > 0:
            rds.remove(rd)
        else:
            projss.append(projs)
    
    # for every projection candidate of every gps-record, add vertex to DAG
    for i in range(0,len(projss)):
        projs = projss[i]
        for ii in range(0,len(projs)):
            proj = projs[ii]

            # vertex in DAG represented by tuple (i,ii)
            # 1) i is the index of gps-record in track
            # 2) ii is the index of projection candidate in i gps-record
            dag.add_node((i, ii), s = proj['s'], t = proj['t'], \
                    gps_lonlat = rds[i]['gps_lonlat'], \
                    proj_lonlat = proj['proj_lonlat'], \
                    l_s = proj['l_s'], \
                    l_t = proj['l_t'], \
                    d_proj = proj['d_proj'], \
                    weight = 1)

    # for every pair of contiguous gps-records
    for i in range(0,len(projss)-1):
        j = i + 1
        i_projs = projss[i]
        j_projs = projss[j]

        # for every projection candidate ii of i gps-record
        for ii in range(0,len(i_projs)):
            ii_proj = i_projs[ii]
            s_ii = ii_proj['s']
            t_ii = ii_proj['t']
            speed_ii = gw.G[s_ii][t_ii]['speed']
            
            # for every projection candidate jj of j=i+1 gps-record
            for jj in range(0,len(j_projs)):
                jj_proj = j_projs[jj]
                s_jj = jj_proj['s']
                t_jj = jj_proj['t']
                speed_jj = gw.G[s_jj][t_jj]['speed']
                
                # calculate:
                # 1) path on map between ii and jj
                # 2) weight of path between ii and jj
                if t_ii == s_jj:
                    p_tii_sjj = ()
                    w_tii_sjj = ii_proj['l_t']/speed_ii + jj_proj['l_s']/speed_jj
                
                elif t_ii == t_jj and s_ii == s_jj:
                    p_tii_sjj = ()
                    w_tii_sjj = (jj_proj['l_s'] - ii_proj['l_s'])/speed_ii
                    
                    if w_tii_sjj < 0:
                        p_tii_sjj = gw.shortest_path_from_to(t_ii, s_jj, 'time')
                        
                        if not len(p_tii_sjj) > 0:
                            w_tii_sjj = INF
                        else:
                            w_tii_sjj = gw.time_of_edges(p_tii_sjj) + ii_proj['l_t']/speed_ii + jj_proj['l_s']/speed_jj
                
                else:
                    p_tii_sjj = gw.shortest_path_from_to(t_ii, s_jj, 'time')
                    
                    if not len(p_tii_sjj) > 0:
                        w_tii_sjj = INF
                    else:
                        w_tii_sjj = gw.time_of_edges(p_tii_sjj) + ii_proj['l_t']/speed_ii + jj_proj['l_s']/speed_jj
                
                # add edge between ii and jj to DAG
                dag.add_edge((i, ii), (j, jj), path = p_tii_sjj, weight = w_tii_sjj)
                
    return dag

def combine_weight_with(sw_cv, w_cv_nv, w_nv):
    return sw_cv + w_cv_nv + w_nv

def init_weight_with(w_source_v):
    return w_source_v



