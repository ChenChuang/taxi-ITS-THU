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
from ccdef import *

gdag = None
gpdag = list()
ges = list()


def prepare(gw):
    pass

def match(gw, track, debug = False):
    dag_rds = create_dag_rds(gw, track)
    if dag_rds is None:
        # print 'failed creating DAG',
        return None
    dag = dag_rds['dag']
    rds = dag_rds['rds']
    vote_dict = voting(dag, rds)
    
    p_dag = path_from_vote(dag, vote_dict, rds)


    if p_dag is None:
        # print 'failed finding path in DAG',
        return None
    es = cdagm.pdag2es(dag, p_dag)
    if es is None:
        # print 'failed generating edge list in Graph'
        return None
    p = cp.new_path_from_es(gw, track.tid, es)
    if p is None:
        # print 'failed creating Path instance'
        return None
    if debug:
        global gdag
        gdag = dag.copy()
        global gpag
        gpdag = list(p_dag)
        global ges
        ges = list(es)
    return p


def create_vote_dict(dag):
    vote_dict = {}
    for v in dag.nodes():
        vote_dict[v] = 0
    return vote_dict

def influence_dag(dag, wi, rds):
    idag = dag.copy()
    es = dag.edges()
    for e in es:
        i = e[0][0]
        if i == wi:
            continue
        d_wi_i = cg.lonlats2km( rds[wi]['gps_lonlat'], rds[i]['gps_lonlat'] )
        idag[e[0]][e[1]]['weight'] = dag[e[0]][e[1]]['weight'] * ( 2**(-d_wi_i) )
    return idag

def clip_dag(dag, v):
    cdag = dag.copy()
    es = dag.edges()
    vi = v[0]
    vii = v[1]
    for e in es:
        i = e[0][0]
        ii = e[0][1]
        j = e[1][0]
        jj = e[1][1]
        if i == vi and ii != vii:
            cdag[e[0]][e[1]]['weight'] = -INF
        if j == vi and jj != vii:
            cdag[e[0]][e[1]]['weight'] = -INF
    return cdag

def voting(dag, rds):
    vote_dict = create_vote_dict(dag)
    for wi in range(0, len(rds)):
        # print wi,
        idag = influence_dag(dag, wi, rds)
        cii = 0
        while True:
            if not dag.has_node((wi, cii)):
                break
            #print (wi, cii),
            cdag = clip_dag(idag, (wi, cii))
            p_cdag = cdagm.longest_path_dag(cdag, init_weight_with, combine_weight_with)
            for v in p_cdag:
                vote_dict[v] = vote_dict[v] + 1
            cii = cii + 1
    # print ""
    return vote_dict

def path_from_vote(dag, vote_dict, rds):
    vds_dict = {}
    for v,d in dag.nodes(True):
        vds_dict[v] = d

    p_dag = []
    for i in range(0, len(rds)):
        max_vote_ii = -1
        max_vote = -1
        d_proj_max_vote_ii = INF
        ii = 0
        while True:
            v = (i,ii)
            if not vote_dict.has_key(v):
                break
            vote_v = vote_dict[v]
            d_proj_v = vds_dict[v]
            if vote_v > max_vote or (vote_v == max_vote and d_proj_v < d_proj_max_vote_ii):
                max_vote_ii = ii
                max_vote = vote_v
                d_proj_max_vote_ii = d_proj_v
            ii = ii + 1
        if max_vote_ii < 0:
            return None
        p_dag.append((i,max_vote_ii))
    if len(p_dag) == 0:
        return None
    return p_dag

def create_dag_rds(gw, track, k=5, r=0.1, sigma=0.02):
    dag = nx.DiGraph()
    rds = []
    projss = []

    # for every gps-record in track, find its valid projection candidates
    for i in range(0,len(track.rds)):
        rd = track.rds[i]
        if i > 0:
            if time.mktime(track.rds[i]['time']) - time.mktime(track.rds[i-1]['time']) <= 0:
                continue
        lonlat_rds = rd['gps_lonlat']
        projs = gw.find_projs_within(lonlat_rds, r)
        # max candidates of each gps-record is k
        if len(projs) > k:
            ordered_projs = list(projs)
            ordered_projs.sort(key = operator.itemgetter('d_proj'))
            projs = tuple(ordered_projs[0:k])
            

        # if no projection candidates found, remove the gps-record from track
        if len(projs) > 0:
            rds.append(rd)
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
                    weight = norm(0,sigma).pdf(proj['d_proj']))

    # for every pair of contiguous gps-records
    for i in range(0,len(projss)-1):
        j = i + 1
        i_projs = projss[i]
        j_projs = projss[j]
        d_i_j = cg.lonlats2km(rds[i]['gps_lonlat'], rds[j]['gps_lonlat'])
        time_i_j = (time.mktime(rds[j]['time']) - time.mktime(rds[i]['time'])) / 3600.0   # in hour
        if time_i_j <= 0:
            time_i_j = 0.0001

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

                w_tii_sjj = 0
                if t_ii == s_jj:
                    p_tii_sjj = ()
                    ls_tii_sjj = [ii_proj['l_t'], jj_proj['l_s']]
                    vs_tii_sjj = [speed_ii, speed_jj]

                elif t_ii == t_jj and s_ii == s_jj:
                    p_tii_sjj = ()
                    ls_tii_sjj = [jj_proj['l_s'] - ii_proj['l_s'],]
                    vs_tii_sjj = [speed_ii, ]

                    if abs(ls_tii_sjj[0]) < 0.00000001:
                        ls_tii_sjj = [d_i_j,]
                    elif ls_tii_sjj[0] < 0:
                        p_tii_sjj = gw.shortest_path_from_to(t_ii, s_jj, 'time')

                        if not len(p_tii_sjj) > 0:
                            w_tii_sjj = -INF
                        else:
                            ls_tii_sjj = [ii_proj['l_t'],] + list(gw.get_edges_attr(p_tii_sjj, 'length')) + [jj_proj['l_s'],]
                            vs_tii_sjj = [speed_ii, ] + list(gw.get_edges_attr(p_tii_sjj, 'speed')) + [speed_jj, ]
                else:
                    p_tii_sjj = gw.shortest_path_from_to(t_ii, s_jj, 'time')

                    if not len(p_tii_sjj) > 0:
                        w_tii_sjj = -INF
                    else:
                        ls_tii_sjj = [ii_proj['l_t'],] + list(gw.get_edges_attr(p_tii_sjj, 'length')) + [jj_proj['l_s'],]
                        vs_tii_sjj = [speed_ii, ] + list(gw.get_edges_attr(p_tii_sjj, 'speed')) + [speed_jj, ]


                if w_tii_sjj != 0:
                    dag.add_edge((i, ii), (j, jj), path = p_tii_sjj, weight = w_tii_sjj)
                    continue
                # add edge between ii and jj to DAG
                N_jj = norm(0,sigma).pdf(jj_proj['d_proj'])
                #ts = []
                #for a in range(0,len(ls_ii_jj)):
                #    ts.append(ls_ii_jj[a] / vs_ii_jj[a])
                #V_ii_jj = sum(ts)
                t_tii_sjj = 0
                for ilv in range(0,len(ls_tii_sjj)):
                    t_tii_sjj = t_tii_sjj + ls_tii_sjj[ilv] / vs_tii_sjj[ilv]
                l_tii_sjj = sum(ls_tii_sjj)
                if l_tii_sjj <= 0:
                    V_tii_sjj = 1
                else:
                    V_tii_sjj = d_i_j / l_tii_sjj
                Fs_tii_sjj = V_tii_sjj * N_jj
                avg_v = l_tii_sjj / time_i_j
                Ft_tii_sjj = sum(vs_tii_sjj) / math.sqrt(sum([v**2 for v in vs_tii_sjj])) / math.sqrt(len(vs_tii_sjj))
                #Ft_tii_sjj = math.sqrt(sum([(v-avg_v)**2, for v in vs_tii_sjj]))
                F_tii_sjj = Fs_tii_sjj * Ft_tii_sjj
                dag.add_edge((i, ii), (j, jj), path = p_tii_sjj, weight = F_tii_sjj)

    return {'dag':dag, 'rds':rds}

def combine_weight_with(sw_cv, w_cv_nv, w_nv):
    return sw_cv + w_cv_nv

def init_weight_with(w_source_v):
    return w_source_v







