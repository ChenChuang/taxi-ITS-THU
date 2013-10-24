import networkx as nx
from ccdef import *

def shortest_path_dag(dag, init_weight_with = None, combine_weight_with = None):
    if not nx.is_directed_acyclic_graph(dag):
        return ()
    g = dag.copy()
    vds = g.nodes(data = True)
    sources = []
    sinks = []
    vds_dict = {}
    for vd in vds:
        v = vd[0]
        vds_dict[v] = vd[1]

        g.add_node(v, pre = None, sweight = INF)
        vds_dict[v]['pre'] = None
        vds_dict[v]['sweight'] = INF

        if g.in_degree(v) == 0:
            sources.append(v)

            g.add_node(v, pre = None, sweight = 0)
            vds_dict[v]['pre'] = None
            if init_weight_with is None:
                vds_dict[v]['sweight'] = vds_dict[v]['weight']
            else:
                vds_dict[v]['sweight'] = init_weight_with(vds_dict[v]['weight'])

        if g.out_degree(v) == 0:
            sinks.append(v)

    cvs = sources
    
    while True:
        if not len(cvs) > 0:
            break

        all_nvs = []

        for cv in cvs:
            sw_cv = vds_dict[cv]['sweight']
            
            nvs = g.neighbors(cv)
            for nv in nvs:
                sw_nv = vds_dict[nv]['sweight']

                w_nv = vds_dict[nv]['weight']
                w_cv_nv = g[cv][nv]['weight']

                if combine_weight_with is None:
                    tmp_sw_nv = sw_cv + w_cv_nv + w_nv
                else:
                    tmp_sw_nv = combine_weight_with(sw_cv, w_cv_nv, w_nv)

                if tmp_sw_nv < sw_nv:
                    g.add_node(nv, pre = cv, sweight = tmp_sw_nv)
                    vds_dict[nv]['sweight'] = tmp_sw_nv
                    vds_dict[nv]['pre'] = cv

            all_nvs = list(set(all_nvs + nvs))

        cvs = all_nvs


    sw_min = INF
    v_min = None
    for v in sinks:
        sw_v = vds_dict[v]['sweight']
        if sw_v < sw_min:
            sw_min = sw_v
            v_min = v

    if v_min is None:
        return None

    pdag = []
    v = v_min
    while True:
        pdag.append(v)
        pv = vds_dict[v]['pre']
        if pv is None:
            break
        else:
            v = pv

    return tuple(pdag[::-1])

def longest_path_dag(dag, init_weight_with = None, combine_weight_with = None):
    if not nx.is_directed_acyclic_graph(dag):
        return ()
    g = dag.copy()
    vds = g.nodes(data = True)
    sources = []
    sinks = []
    vds_dict = {}
    for vd in vds:
        v = vd[0]
        vds_dict[v] = vd[1]

        g.add_node(v, pre = None, sweight = 0)
        vds_dict[v]['pre'] = None
        vds_dict[v]['sweight'] = -INF

        if g.in_degree(v) == 0:
            sources.append(v)

            g.add_node(v, pre = None, sweight = 0)
            vds_dict[v]['pre'] = None
            if init_weight_with is None:
                vds_dict[v]['sweight'] = vds_dict[v]['weight']
            else:
                vds_dict[v]['sweight'] = init_weight_with(vds_dict[v]['weight'])

        if g.out_degree(v) == 0:
            sinks.append(v)

    cvs = sources
    
    while True:
        if not len(cvs) > 0:
            break

        all_nvs = []

        for cv in cvs:
            sw_cv = vds_dict[cv]['sweight']
            
            nvs = g.neighbors(cv)
            for nv in nvs:
                sw_nv = vds_dict[nv]['sweight']

                w_nv = vds_dict[nv]['weight']
                w_cv_nv = g[cv][nv]['weight']

                if combine_weight_with is None:
                    tmp_sw_nv = sw_cv + w_cv_nv + w_nv
                else:
                    tmp_sw_nv = combine_weight_with(sw_cv, w_cv_nv, w_nv)

                if tmp_sw_nv >= sw_nv:
                    g.add_node(nv, pre = cv, sweight = tmp_sw_nv)
                    vds_dict[nv]['sweight'] = tmp_sw_nv
                    vds_dict[nv]['pre'] = cv

            all_nvs = list(set(all_nvs + nvs))

        cvs = all_nvs


    sw_max = -INF
    v_max = None
    for v in sinks:
        sw_v = vds_dict[v]['sweight']
        if sw_v >= sw_max:
            sw_max = sw_v
            v_max = v

    if v_max is None:
        return None

    pdag = []
    v = v_max
    while True:
        pdag.append(v)
        pv = vds_dict[v]['pre']
        if pv is None:
            break
        else:
            v = pv

    return tuple(pdag[::-1])


def pdag2es(dag, p_dag):
    vds = dag.nodes(data = True)
    vds_dict = {}
    for vd in vds:
        vds_dict[vd[0]] = vd[1]

    es = []
    v = p_dag[0]
    e = (vds_dict[v]['s'], vds_dict[v]['t'])
    es.append(e)
    for i in range(1,len(p_dag)):
        v = p_dag[i]
        pv = p_dag[i-1]
        e = (vds_dict[v]['s'], vds_dict[v]['t'])
        pe = es[-1]
        if e == pe:
            continue
        else:
            es = es + list(dag[pv][v]['path'])
            es.append(e)

    return tuple(es)
    

def plot_dag(dag, withlabel = False):
    import matplotlib.pyplot as plt
    vs = dag.nodes()
    pos = {}
    for v in vs:
        pos[v] = v

    es_valid = [(u,v,d) for (u,v,d) in dag.edges(data = True) if d['weight'] < INF]
    
    nx.draw_networkx_nodes(dag, pos)
    nx.draw_networkx_edges(dag, pos, edgelist = es_valid, arrows = False)
    if withlabel:
        elabels = dict([((u,v,),d['weight']) for u,v,d in es_valid])
        nx.draw_networkx_edge_labels(dag, pos, edge_labels = elabels)
    #plt.axis('off')
    plt.show()
