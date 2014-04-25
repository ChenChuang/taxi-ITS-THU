import sys
import operator
import time
import math
import traceback
from scipy.stats import norm
import networkx as nx
import cctrack as ct
import ccpath as cp
import ccdagmodel as cdagm
import ccgraph as cg
import ccdb as cdb
from ccdef import *

from alg_ways_attr import intervals as awa_intervals
from alg_ways_attr import resolution as awa_resolution

awa_intervals_num = int((awa_intervals[1] - awa_intervals[0]) / awa_resolution)

ways_attrs_tbname = "ways_ut_attr_2"

ways_used_times = None
ways_used_interval = None

best_paths_buffer = dict()
shortest_t_paths_buffer = dict()
shortest_l_paths_buffer = dict()
shortest_t_cv_buffer = dict()
shortest_l_cv_buffer = dict()

summary = Summary(
        forced_shortest = 0,
        best_path_called = 0)

def prepare(gw):
    wadb = cdb.new_way_attr_db(tbname=ways_attrs_tbname)
    global ways_used_times
    ways_used_times = wadb.read_attr('used_times')

    ###########################################
    global ways_used_interval
    ways_used_interval = [map(int, strs.split(",")) for strs in wadb.read_attr('used_interval')]

    def normalize(xs):
        m = max(xs)+1
        return [float(x+1) / m for x in xs]

    ways_used_interval = [normalize(xs) for xs in ways_used_interval]
    ##########################################
    
    del wadb
    set_graph_weight(gw)

def set_graph_weight(gw):
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
        
        edge_w = 1
        ## edge_w = edge_time / (2 - math.exp(-weight))
        ## edge_w = edge_time / (2 - math.exp(-used_times))
        ## edge_w = 1 / (0.1 + 0.9*(used_times / max_used_times))
        ## edge_w = edge_time / (1 + used_times / max_used_times)
        ## edge_w = edge_length / (0.01 + used_times / max_used_times)
        ## edge_w = edge_length / (1 + math.atan(0.003*(used_times - 210))/math.pi + 0.5)
        ## edge_w = edge_length
        ## edge_w = edge_time
        
        gw.G[s][t]['weight'] = edge_w
        try:
            gw.G[t][s]['weight'] = edge_w
        except KeyError, e:
            pass

def shortest_path_from_to(gw, origin, destination, **kwargs):
    weight = kwargs['weight']
    return gw.shortest_path_from_to(origin, destination, weight)

def best_path_from_to(gw, origin, destination, **kwargs):

    global summary

    current = kwargs['current']
    whole = kwargs['whole']
    from_edge = kwargs['from_edge']
    to_edge = kwargs['to_edge']
    orig_lonlat = kwargs['orig_lonlat']
    dest_lonlat = kwargs['dest_lonlat']
    
    if current == INF:
        return []

    # try to retrive the best path between origin and dest is in buffer
    global best_paths_buffer, shortest_t_paths_buffer, shortest_l_paths_buffer
    try:
        best_path = best_paths_buffer[(origin, destination)]
        return best_path
    except KeyError, e:
        pass

    # compute shortest path between origin and dest
    # Paths whose length not much longer than shortest length will be considered below
    try:
        shortest_t_path = shortest_t_paths_buffer[(origin, destination)]
    except KeyError, e:
        shortest_t_path = gw.shortest_path_from_to(origin, destination, 'time')
        shortest_t_paths_buffer[(origin, destination)] = shortest_t_path
    try:
        shortest_l_path = shortest_l_paths_buffer[(origin, destination)]
    except KeyError, e:
        shortest_l_path = gw.shortest_path_from_to(origin, destination, 'length')
        shortest_l_paths_buffer[(origin, destination)] = shortest_l_path
    
    if len(shortest_t_path) == 0:
        return ()
    if len(shortest_l_path) == 0:
        return ()
    
    tmp_path = cp.new_path_from_es(gw, 0, [from_edge] + shortest_t_path + [to_edge])
    shortest_time = tmp_path.precise_time(orig_lonlat, dest_lonlat)

    tmp_path = cp.new_path_from_es(gw, 0, [from_edge] + shortest_l_path + [to_edge])
    shortest_length = tmp_path.precise_length(orig_lonlat, dest_lonlat)

    # Euclid distance between origin and destination
    euclid = gw.d_between_nodes(origin, destination)

    if (abs(shortest_length - euclid) < euclid * 0.01 and len(shortest_t_path) < 3):
        return shortest_t_path

    if shortest_length > 20:
        summary.forced_shortest += 1
        return shortest_t_path

    summary.best_path_called += 1


    max_l = shortest_length * 1.3
    max_t = shortest_time * 1.3

    # visited = {node_id:(
    # 0) pre node_id,
    # 1) children, 
    # 2) length of prior path, 
    # 3) sum of used_times, 
    # 4) sum of time, 
    # 5) sum of used_times*length of way
    # 6) num of waysi
    # 7) num of turns
    # )}
    
    orig_wid = gw.G[from_edge[0]][from_edge[1]]['way_id']
    orig_l = gw.proj_p2edge(orig_lonlat, from_edge)['l_t']
    orig_u = float(int(ways_used_times[orig_wid-1]))
    orig_t = orig_l / gw.G[from_edge[0]][from_edge[1]]['speed']
    orig_lu = orig_l * orig_u

    visited = {origin:[-1, [], orig_l, orig_u, orig_t, orig_lu, 0, 0]}    
    added = [origin,]
    
    # visit all nodes like using BFS, and find the best path
    iscontinue = True
    while iscontinue:
        iscontinue = False

        added_nodes = added[::]
        added = []
        for v in added_nodes:
            try:
                (pre, childs, s_l, s_u, s_t, s_lu, n_e, n_tr) = visited[v]
            except:
                continue

            for e in gw.G.out_edges(nbunch = v):
                # assert v == e[0]
                # visiting cv via e
                cv = e[1]
                # attributes of e
                e_wid = gw.G[e[0]][e[1]]['way_id']
                e_l = gw.G[e[0]][e[1]]['length']
                e_u = float(int(ways_used_times[e_wid-1]))
                e_t = gw.G[e[0]][e[1]]['time']
                e_lu = e_l * e_u
                if pre == -1:
                    if gw.is_turn_between_es((from_edge[0],v), (v,cv)):
                        e_tr = 1
                    else:
                        e_tr = 0
                else:
                    if gw.is_turn_between_es((pre,v),(v,cv)):
                        e_tr = 1
                    else:
                        e_tr = 0
                if cv == destination:
                    if gw.is_turn_between_es((v,cv), (cv,to_edge[1])):
                        e_tr += 1

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
               
                # print some debug infos
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
                    print ""

                # check if destination is reachable from cv within max_l
                cv_pre = v
                cv_s_l = s_l + e_l
                cv_s_t = s_t + e_t

                ####################################
                e_u = e_u * ways_used_interval[e_wid-1][min(awa_intervals_num-1, int(math.floor((cv_s_l + current) / whole)))]
                e_lu = e_u * e_l
                ####################################

                cv_s_u = s_u + e_u                
                cv_s_lu = s_lu + e_lu
                cv_n_e = n_e + 1
                cv_n_tr = n_tr + e_tr

                # check if it is possible to reach destination from cv within constrained travel time and length
                if cv_s_l > max_l and cv_s_t > max_t:
                    # unreachable
                    if cv in debug_cvs:
                        print cv_s_l, cv_s_t, "cv_s_l and t > max", max_l, max_t
                    continue

                try:
                    shortest_l_cv = shortest_l_cv_buffer[(cv, destination)]
                except KeyError, e:
                    tmp_path = gw.shortest_path_from_to(cv, destination, 'length')
                    if len(tmp_path) == 0 and cv != destination:
                        shortest_l_cv = -1
                    else:
                        shortest_l_cv = gw.length_of_edges(tmp_path)
                    shortest_l_cv_buffer[(cv, destination)] = shortest_l_cv
                if shortest_l_cv < 0:
                    if cv in debug_cvs:
                        print "disconnected from dest"
                    continue

                try:
                    shortest_t_cv = shortest_t_cv_buffer[(cv, destination)]
                except KeyError, e:
                    tmp_path = gw.shortest_path_from_to(cv, destination, 'time')
                    if len(tmp_path) == 0 and cv != destination:
                        shortest_t_cv = -1
                    else:
                        shortest_t_cv = gw.time_of_edges(tmp_path)
                    shortest_t_cv_buffer[(cv, destination)] = shortest_t_cv
                if shortest_t_cv < 0:
                    if cv in debug_cvs:
                        print "disconnected from dest"
                    continue

                if cv_s_l + shortest_l_cv > max_l and cv_s_t + shortest_t_cv > max_t:
                    if cv in debug_cvs:
                        print "l and t > max"
                    continue
                
                # if cv is visited, update it if necessary 
                # else, add cv to added and visited_dict

                is_to_add = False
                
                if not visited.has_key(cv):
                    is_to_add = True
                else:
                    [cv_pre_b, cv_childs_b, cv_s_l_b, cv_s_u_b, cv_s_t_b, cv_s_lu_b, cv_n_e_b, cv_n_tr_b]  = visited[cv]

                    # find the shared part of path of cv and visited[cv][0], we compare the turns number of the rest.
                    tmp_cv_share_n_tr = 0
                    tmp_cv_share_s_l = 0
                    if True or (cv_n_tr > 0 and cv_n_tr_b > 0):
                        tmp_cv = cv_pre
                        tmp_cv_path = []
                        while tmp_cv >= 0:
                            tmp_cv_path.append(tmp_cv)
                            tmp_cv = visited[tmp_cv][0]
                    
                        tmp_cv = visited[cv][0]
                        while tmp_cv >= 0:
                            if tmp_cv in tmp_cv_path:
                                tmp_cv_share_n_tr = visited[tmp_cv][7]
                                tmp_cv_share_s_l = visited[tmp_cv][2]
                                break
                            tmp_cv = visited[tmp_cv][0]
                    tmp_cv_n_tr = cv_n_tr - tmp_cv_share_n_tr
                    tmp_cv_n_tr_b = cv_n_tr_b - tmp_cv_share_n_tr
                    tmp_cv_s_l = cv_s_l - tmp_cv_share_s_l
                    tmp_cv_s_l_b = cv_s_l_b - tmp_cv_share_s_l

                    if tmp_cv_s_l < 0.05 and tmp_cv_s_l < tmp_cv_s_l_b:
                        is_to_add = True
                    elif tmp_cv_s_l_b < 0.05 and tmp_cv_s_l_b < tmp_cv_s_l:
                        is_to_add = False
                    elif tmp_cv_n_tr == 0 and tmp_cv_n_tr_b > 0:
                        is_to_add = True
                    elif tmp_cv_n_tr > 0 and tmp_cv_n_tr_b == 0:
                        is_to_add = False
                    elif cv_s_lu / (cv_s_l+0.0000001) > cv_s_lu_b / (cv_s_l_b+0.0000001): 
                        is_to_add = True
                
                if is_to_add:
                    iscontinue = True

                    # empty the traverse-tree rooted by cv
                    if visited.has_key(cv):
                        [cv_pre_b, cv_childs_b, cv_s_l_b, cv_s_u_b, cv_s_t_b, cv_s_lu_b, cv_n_e_b, cv_n_tr_b]  = visited[cv]
                        tmp_tree = cv_childs_b
                        while True:
                            try:
                                tmp_tree_v = tmp_tree.pop(0)
                            except IndexError, e:
                                break
                            tmp_tree = tmp_tree + visited[tmp_tree_v][1]
                            del visited[tmp_tree_v]
                            if tmp_tree_v in added:
                                added.remove(tmp_tree_v)
                        # remove cv from previous parent's childs
                        if cv in visited[cv_pre_b][1]:
                            visited[cv_pre_b][1].remove(cv)

                    # update cv's attributes, its childs set is empty now
                    visited[cv] = [cv_pre, [], cv_s_l, cv_s_u, cv_s_t, cv_s_lu, cv_n_e, cv_n_tr]
                    # add cv to current parent's childs
                    if cv not in visited[cv_pre][1]:
                        visited[cv_pre][1].append(cv)
    
                    if cv not in added:
                        added.append(cv)

                    if False and cv in debug_cvs:
                        print "add/update",cv
                        print tmp_p
                        print visited[cv]
                        print ""
                # Greedy strategy is employed to select the best path so far
                # WHAT IS THE BEST?
                # Considering attributes of ways and evaluation of pathsi based on our trip module, 
                # other than length, which has been considered via max_l
 

    path = []
    # destination has not been visited, this is impossible
    if not visited.has_key(destination):
        return shortest_t_path

    # backward from destination to origin and return the path founded
    cv = destination
    pv = visited[cv][0]
    while pv >= 0:
        path.append((pv,cv))
        cv = pv
        pv = visited[cv][0]
    path.reverse()
    
    # store path found in buffer
    best_paths_buffer[(origin, destination)] = path

    return path

def match(gw, track):
    global best_paths_buffer, shortest_t_paths_buffer, shortest_l_paths_buffer
    best_paths_buffer = dict()
    shortest_t_paths_buffer = dict()
    shortest_l_paths_buffer = dict()
    shortest_t_cv_buffer = dict()
    shortest_l_cv_buffer = dict()

    shortest_p = track2path(gw, track, shortest_path_from_to, weight = 'length')
    if shortest_p is None:
        # print 'failed shortest'
        return None
    shortest_length = shortest_p.precise_length(track.rds[0]['gps_lonlat'], track.rds[-1]['gps_lonlat'])

    # print shortest, shortest_p.es

    best_p = track2path(gw, track, best_path_from_to, whole = shortest_length)
    if best_p is None:
        # print 'failed best'
        return None

    # update_ways_weight(p, track)
    # update_ways_weight_proj(p, track)

    best_p.smooth()
    return best_p

def track2path(gw, track, path_selector, k=5, r=0.1, sigma=0.02, **kwargs):
    dag = nx.DiGraph()
    rds = track.aggre_records()
    ## rds = track.rds
    projss = []

    # for every gps-record in track, find its valid projection candidates
    for rd in list(rds):
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
  
    if len(projss) == 0:
        return None

    # minimum length of path from source to vertex(i,ii) in DAG
    min_sw_dict = {}
    # previous vertex in path with minimum length(above) in DAG
    pre_dict = {}

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
                    weight = 10*proj['d_proj'])
                    ## weight = -math.log(norm(0,sigma).pdf(proj['d_proj'])))
                    ## weight = 0)
            # the source vertexes
            if i == 0:
                min_sw_dict[(i,ii)] = 0
                pre_dict[(i,ii)] = -1
            else:
                min_sw_dict[(i,ii)] = INF
                pre_dict[(i,ii)] = None
   
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
            sw_ii = min_sw_dict[(i,ii)]
            
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
                        p_tii_sjj = path_selector(gw, t_ii, s_jj, 
                                current = sw_ii, 
                                orig_lonlat = ii_proj['proj_lonlat'], 
                                dest_lonlat = jj_proj['proj_lonlat'], 
                                from_edge = (s_ii, t_ii), 
                                to_edge = (s_jj, t_jj), 
                                **kwargs)

                        if not len(p_tii_sjj) > 0:
                            w_tii_sjj = INF
                        else:
                            w_tii_sjj = gw.length_of_edges(p_tii_sjj) + ii_proj['l_t'] + jj_proj['l_s']
                
                else:
                    ## p_tii_sjj = gw.shortest_path_from_to(t_ii, s_jj)
                    ## p_tii_sjj = best_path_from_to_slow(gw, t_ii, s_jj)
                    p_tii_sjj = path_selector(gw, t_ii, s_jj, 
                            current = sw_ii, 
                            orig_lonlat = ii_proj['proj_lonlat'], 
                            dest_lonlat = jj_proj['proj_lonlat'], 
                            from_edge = (s_ii, t_ii), 
                            to_edge = (s_jj, t_jj), 
                            **kwargs)

                    if not len(p_tii_sjj) > 0:
                        w_tii_sjj = INF
                    else:
                        w_tii_sjj = gw.length_of_edges(p_tii_sjj) + ii_proj['l_t'] + jj_proj['l_s']
                
                # add edge between ii and jj to DAG
                # w_tii_sjj = math.exp(-w_tii_sjj)
                dag.add_edge((i, ii), (j, jj), path = p_tii_sjj, weight = w_tii_sjj)
        
        for jj in range(0,len(j_projs)):
            min_sw_j_jj = INF
            min_ii = None
            for tmp_ii in range(0,len(i_projs)):
                min_sw_i_ii = min_sw_dict[(i, tmp_ii)] 
                tmp_sw_j_jj = min_sw_i_ii + dag[(i,tmp_ii)][(j,jj)]['weight']

                if tmp_sw_j_jj < min_sw_j_jj:
                    min_sw_j_jj = tmp_sw_j_jj
                    min_ii = tmp_ii
            min_sw_dict[(j,jj)] = min_sw_j_jj
            pre_dict[(j,jj)] = (i, min_ii)

    


    if False:
        # find the sink vertex with minimum sum of weights
        min_sw_j_jj = INF
        j = len(projss) - 1
        min_jj = -1
        for jj in range(0,len(projss[-1])):
            sw_j_jj = min_sw_dict[(j,jj)]
            if sw_j_jj < min_sw_j_jj:
                min_sw_j_jj = sw_j_jj
                min_jj = jj

        if min_jj < 0:
            return None

        # backward from best sink vertex, generate the path in DAG
        pdag = []
        v = (j,min_jj)
        while True:
            pdag.append(v)
            pv = pre_dict[v]
            if pv is None:
                return None
            if pv == -1:
                break
            else:
                v = pv

        pdag = pdag[::-1]

    def combine_weight_with(sw_cv, w_cv_nv, w_nv):
        return sw_cv + w_cv_nv + w_nv

    def init_weight_with(w_source_v):
        return w_source_v

    pdag = cdagm.shortest_path_dag(dag, init_weight_with, combine_weight_with)

    if pdag is None:
        return None

    # generating es from pdag
    vds = dag.nodes(data = True)
    vds_dict = {}
    for vd in vds:
        vds_dict[vd[0]] = vd[1]

    es = []
    v = pdag[0]
    e = (vds_dict[v]['s'], vds_dict[v]['t'])
    es.append(e)
    for i in range(1,len(pdag)):
        v = pdag[i]
        pv = pdag[i-1]
        e = (vds_dict[v]['s'], vds_dict[v]['t'])
        pe = es[-1]
        if e == pe:
            continue
        else:
            es = es + list(dag[pv][v]['path'])
            if es[-1] != e:
                es.append(e)

    if len(es) == 0:
        return None
    
    # generating path instance from es
    path = cp.new_path_from_es(gw, track.tid, es)
    return path



