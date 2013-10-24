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

gdag = None
gpdag = list()
ges = list()

ways_weight = None
ways_used_times = None

paths_buffer = dict()

def prepare(gw):
    wadb = cdb.new_way_attr_db(tbname="ways_ut_attr")
    global ways_weight
    global ways_used_times
    ways_weight = wadb.read_attr('weight')
    ways_used_times = wadb.read_attr('used_times')
    del wadb
    set_graph_weight(gw)

def set_graph_weight(gw):
    global ways_weight
    global ways_used_times

    max_used_times = max(ways_used_times) + 1
    max_used_times = float(max_used_times)
    max_used_times_log = math.log(max_used_times)

    ## for (wid, weight) in enumerate(ways_weight):
    for (wid, used_times) in enumerate(ways_used_times):
        wid = wid + 1
        s,t = gw.st[wid]
        used_times = float(used_times)
        used_times_log = math.log(1+used_times)

        edge_time = gw.G[s][t]['length'] / gw.G[s][t]['speed']
        edge_length = gw.G[s][t]['length']
        
        ## edge_w = 1
        ## edge_w = edge_time / (2 - math.exp(-weight))
        ## edge_w = edge_time / (2 - math.exp(-used_times))
        ## edge_w = 1 / (0.1 + 0.9*(used_times / max_used_times))
        ## edge_w = edge_time / (1 + used_times / max_used_times)
        ## edge_w = edge_length / (0.01 + used_times / max_used_times)
        ## edge_w = edge_length / (1 + math.atan(0.003*(used_times - 210))/math.pi + 0.5)
        edge_w = edge_length
        ## edge_w = edge_time
        
        gw.G[s][t]['weight'] = edge_w
        try:
            gw.G[t][s]['weight'] = edge_w
        except KeyError, e:
            pass

def update_ways_weight(path, track):
    global ways_weight
    global ways_used_times
    wids = path.get_ways()
    conf = path.confidence(track)
    for wid in wids:
        ways_weight[wid-1] += conf
        ways_used_times[wid-1] += 1
        
def update_ways_weight_proj(path, track):
    global ways_weight
    global ways_used_times
    ways_ds = path.get_ways_ds_proj(track)
    conf = path.confidence()
    for (wid, d) in ways_ds:
        ways_weight[wid-1] += conf / d
        ways_used_times[wid-1] += 1

def update_graph(tracks_num, gw):
    if tracks_num == 5000 or (tracks_num > 5000 and tracks_num % 1000 == 0):
        set_graph_weight(gw)
        # write_ways_attrs()    

def write_ways_attrs():
    wadb = cdb.new_way_attr_db("ways_ut_attr")
    wadb.update_attr("weight", ways_weight)
    wadb.update_attr("used_times", ways_used_times)
    del wadb

def init_ways_ut_attr():
    wadb = cdb.new_way_attr_db("ways_ut_attr")
    wadb.init_tb(attrs_values={"used_times":0, "weight":0})
    del wadb

def best_path_from_to_slow(gw, origin, destination):

    def weight_of_path(path):
        wids = [gw.G[e[0]][e[1]]['way_id'] for e in path]
        weight = sum([ways_used_times[wid-1] for wid in wids]) / len(wids)
        return weight
    
    global paths_buffer
    try:
        path = paths_buffer[(origin, destination)]
        return path
    except KeyError, e:
        pass

    shortest_path = gw.shortest_path_from_to(origin, destination)
    print "shortest:",len(shortest_path)
    if len(shortest_path) == 0:
        return ()
    shortest = sum([gw.G[e[0]][e[1]]['length'] for e in shortest_path])
    paths = gw.paths_from_to_shorter_than(origin, destination, 1.5 * shortest)
    if len(paths) < 2:
        return shortest_path
    weights = [weight_of_path(p) for p in paths]
    max_weight = max(weights)
    path = paths[weights.index(max_weight)]
    paths_buffer[(origin, destination)] = path
    return path

def best_path_from_to(gw, origin, destination):
    
    # try to retrive the best path between origin and dest is in buffer
    global paths_buffer
    try:
        path = paths_buffer[(origin, destination)]
        return path
    except KeyError, e:
        pass

    # Euclid distance between origin and destination
    euclid = gw.d_between_nodes(origin, destination)

    # compute shortest path between origin and dest
    # Paths whose length not much longer than shortest length will be considered below
    shortest_path = gw.shortest_path_from_to(origin, destination)
    shortest = sum([gw.G[e[0]][e[1]]['length'] for e in shortest_path])
    
    if abs(shortest - euclid) < euclid * 0.01 and len(shortest_path) < 3:
        return shortest_path
        pass

    max_l = shortest * 1.2

    # visited = {node_id:(
    # 0) pre node_id, 
    # 1) length of prior path, 
    # 2) sum of used_times, 
    # 3) sum of time, 
    # 4) sum of used_times*length of way
    # 5) num of ways
    # )}
    visited = {origin:(-1,0,0,0,0,0)}
    added = [origin,]
    
    # visit all nodes like dijkstra, and find the best path
    iscontinue = True
    while iscontinue:
        iscontinue = False

        added_nodes = added[::]
        added = []
        for v in added_nodes:
            (pre, s_l, s_u, s_t, s_lu, n_e) = visited[v]
            
            for e in gw.G.out_edges(nbunch = v):
                # assert v == e[0]
                # visiting cv via e
                cv = e[1]
                
                # attributes of e
                e_wid = gw.G[e[0]][e[1]]['way_id']
                e_l = gw.G[e[0]][e[1]]['length']
                e_u = float(int(ways_used_times[e_wid-1]))
                e_t = e_l / (e_u + 1)
                e_lu = e_l * e_u

                # check if cv will cause a loop
                isloop = False
                tmp_cv = v
                tmp_pv = visited[tmp_cv][0]
                if cv == origin:
                    isloop = True
                while tmp_pv >= 0:
                    if tmp_cv == cv or tmp_pv == cv:
                        isloop = True
                        break
                    tmp_cv = tmp_pv
                    tmp_pv = visited[tmp_cv][0]
                if isloop:
                    continue
               
                debug_cvs = []
                tmp_p = []
                if False and cv in debug_cvs:
                    tmp_cv = cv
                    tmp_pv = v
                    while tmp_pv >= 0:
                        tmp_p.append((tmp_pv,tmp_cv))
                        tmp_cv = tmp_pv
                        tmp_pv = visited[tmp_cv][0]
                    tmp_p.reverse()
                    print tmp_p
                    print cv_s_l, cv_s_u, cv_s_t, cv_s_lu, cv_n_e
                    print ""

                # check if destination is reachable from cv within max_l
                cv_pre = v
                cv_s_l = s_l + e_l
                cv_s_u = s_u + e_u
                cv_s_t = s_t + e_t
                cv_s_lu = s_lu + e_lu
                cv_n_e = n_e + 1
                if cv_s_l > max_l:
                    # unreachable
                    if cv in debug_cvs:
                        print "l > max"
                    continue
                d_cv2dest = gw.d_between_nodes(cv, destination)
                if cv_s_l + d_cv2dest > max_l:
                    if cv in debug_cvs:
                        print "l+d > max"
                    # unreachable
                    continue
                
                # if cv is visited, update it if necessary 
                # else, add cv to added and visited_dict

                # Greedy strategy is employed to select the best path so far
                # WHAT IS THE BEST?
                # Considering attributes of ways and evaluation of pathsi based on our trip module, 
                # other than length, which has been considered via max_l

                

                if visited.has_key(cv):
                    cv_s_l_before = visited[cv][1]
                    cv_s_u_before = visited[cv][2]
                    cv_s_t_before = visited[cv][3]
                    cv_s_lu_before = visited[cv][4]
                    cv_n_e_before = visited[cv][5]
                    # if cv_n_e_before > 0 and float(cv_s_u) / cv_n_e > float(cv_s_u_before) / cv_n_e_before:
                    # if cv_s_t < cv_s_t_before:
                    # if cv_s_l < cv_s_l_before:
                    if cv_s_lu / (cv_s_l+0.0000001) > cv_s_lu_before / (cv_s_l_before+0.0000001): 
                        if cv not in added:
                            added.append(cv)
                        visited[cv] = (cv_pre, cv_s_l, cv_s_u, cv_s_t, cv_s_lu, cv_n_e)

                        if False and cv in debug_cvs:
                            print "update",cv
                            print tmp_p
                            print visited[cv]
                            print ""
                else:
                    if cv not in added:
                        added.append(cv)
                    visited[cv] = (cv_pre, cv_s_l, cv_s_u, cv_s_t, cv_s_lu, cv_n_e)
                    if False and cv in debug_cvs:
                        print "add",cv
                        print tmp_p
                        print visited[cv]
                        print ""
                    iscontinue = True
                    continue

    path = []
    # destination has not been visited, this is impossible
    if not visited.has_key(destination):
        return shortest_path

    # backward from destination to origin and return the path founded
    cv = destination
    pv = visited[cv][0]
    i = 1
    while pv >= 0 and i < 100:
        path.append((pv,cv))
        cv = pv
        pv = visited[cv][0]
        i += 1
    path.reverse()
    
    # store path founded in buffer
    paths_buffer[(origin, destination)] = paths_buffer[(origin, destination)] = path

    return path

def match(gw, track, debug = False):
    dag = create_dag(gw, track)
    if dag is None:
        print 'failed creating DAG',
        return None
    # p_dag = cdagm.longest_path_dag(dag, init_weight_with, combine_weight_with)
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

    update_ways_weight(p, track)
    # update_ways_weight_proj(p, track)

    if debug:
        global gdag
        gdag = dag.copy()
        global gpag
        gpdag = list(p_dag)
        global ges
        ges = list(es)
    return p

def create_dag(gw, track, k=5, r=0.1, sigma=0.02):
    dag = nx.DiGraph()
    ## rds = list(track.rds)
    rds = track.aggre_records()
    projss = []

    # for every gps-record in track, find its valid projection candidates
    for rd in rds:
        lonlat_rds = rd['gps_lonlat']
        projs = gw.find_projs_within(lonlat_rds, r)
        # if no projection candidates found, remove the gps-record from track
        if len(projs) == 0:
            rds.remove(rd)
        elif len(projs) > k:
            ordered_projs = list(projs)
            ordered_projs.sort(key = operator.itemgetter('d_proj'))
            projs = tuple(ordered_projs[0:k])
            projss.append(projs)
        else:
            projss.append(projs)
    
    min_sw_dict = {}

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
                    # weight = norm(0,sigma).pdf(proj['d_proj']))
                    weight = 0)
            min_sw_dict[(i,ii)] = 0

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
                    w_tii_sjj = ii_proj['l_t'] + jj_proj['l_s']
                
                elif t_ii == t_jj and s_ii == s_jj:
                    p_tii_sjj = ()
                    w_tii_sjj = jj_proj['l_s'] - ii_proj['l_s']
                    
                    if w_tii_sjj < 0:
                        ## p_tii_sjj = gw.shortest_path_from_to(t_ii, s_jj)
                        ## p_tii_sjj = best_path_from_to_slow(gw, t_ii, s_jj)
                        p_tii_sjj = best_path_from_to(gw, t_ii, s_jj)

                        if not len(p_tii_sjj) > 0:
                            w_tii_sjj = INF
                        else:
                            w_tii_sjj = gw.weight_of_edges(p_tii_sjj) + ii_proj['l_t'] + jj_proj['l_s']
                
                else:
                    ## p_tii_sjj = gw.shortest_path_from_to(t_ii, s_jj)
                    ## p_tii_sjj = best_path_from_to_slow(gw, t_ii, s_jj)
                    p_tii_sjj = best_path_from_to(gw, t_ii, s_jj)

                    if not len(p_tii_sjj) > 0:
                        w_tii_sjj = INF
                    else:
                        w_tii_sjj = gw.weight_of_edges(p_tii_sjj) + ii_proj['l_t'] + jj_proj['l_s']
                
                # add edge between ii and jj to DAG
                # w_tii_sjj = math.exp(-w_tii_sjj)
                dag.add_edge((i, ii), (j, jj), path = p_tii_sjj, weight = w_tii_sjj)
        
        for jj in range(0,len(j_projs)):
            min_sw_j_jj = INF
            for (tmp_i, tmp_ii),(tmp_j, tmp_jj) in dag.in_edges((j, jj)):
                min_sw_i_ii = min_sw_dict[(tmp_i, tmp_ii)] 
                tmp_sw_j_jj = min_sw_i_ii + dag[(tmp_i,tmp_ii)][(j,jj)]['weight']
                if tmp_sw_j_jj < min_sw_j_jj:
                    min_sw_j_jj = tmp_sw_j_jj
            min_sw_dict[(j,jj)] = min_sw_j_jj
                
    return dag

def combine_weight_with(sw_cv, w_cv_nv, w_nv):
    # return sw_cv * w_cv_nv * w_nv
    return sw_cv + w_cv_nv + w_nv

def init_weight_with(w_source_v):
    return w_source_v


