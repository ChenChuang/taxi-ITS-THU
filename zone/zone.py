import psycopg2 as pg
import psycopg2.extras as pgextras
import pprocess as pp

import datetime
import random
import math

import sys, os
mmpath = os.path.join(os.getcwd(), '..', 'mm')
sys.path.insert(0, mmpath)
import ccgraph as cg
del sys.path[0]

import ccdbzone as cdbz

def read_clust():
    wcdb = cdbz.WayClustDB()
    return [int(x) for x in wcdb.read_clust()]

def read_cato():
    wcdb = cdbz.WayCatoDB()
    return [int(x) for x in wcdb.read_cato()]

def write_zone(lbs):
    wzdb = cdbz.WayZoneDB()
    wzdb.update_zone(lbs)
    return True

def extract_zone(clust=None, seeds=None, glue=None, is_write=False):
    if clust is None:
        clust = read_clust()

    gw = cg.new_gw()
    nr = len(clust)
    lbs = [-1] * nr
    clb = 0
    radius = 0.03
    
    if seeds is None:
        seeds = [1]
    if glue is None:
        glue = [2]
    seeds_glue = seeds + glue
    for i in xrange(len(lbs)):
        if lbs[i] > 0 or clust[i] not in seeds:
            continue
        clb += 1
        lbs[i] = clb
        queue = [i]
        while len(queue) > 0:
            q = queue.pop(0)
            ngbs = [x-1 for x in gw.find_ws_near_w_fast(q+1, radius)]
            for ngb in ngbs:
                if lbs[ngb] > 0 or clust[ngb] not in seeds_glue:
                    continue
                lbs[ngb] = clb
                queue.append(ngb)        

    if is_write:
        return write_zone(lbs)
    else:
        return lbs

def diff_glue(clust):
    nlbs = []
    seeds = [1]
    glues = [2,3,6,4,7,5,8]
    for i in range(len(glues)+1):
        print glues[:i]
        lbs = extract_zone(clust, seeds, glues[:i])
        nlbs += [max(lbs)]
    return nlbs

def get_one_leaf(atree):
    if isinstance(atree, list):
        return get_one_leaf(atree[0])
    else:
        return atree
    
def get_leaf_num(atree):
    if isinstance(atree, list):
        return sum([get_leaf_num(x) for x in atree])
    else:
        return 1

def is_single_tree(atree):
    if isinstance(atree, list):
        if len(atree) == 1:
            return is_single_tree(atree[0])
        else:
            return False
    else:
        return True

def remove_single_tree(atree):
    if not isinstance(atree, list):
        return atree
    tmp_tree = [x for x in atree if (not isinstance(x, list)) or (not is_single_tree(x))]
    tmp_tree = [remove_single_tree(x) for x in tmp_tree]
    return tmp_tree

def remove_tree_leaf_less(atree, num):
    if not isinstance(atree, list):
        return atree
    tmp_tree = [x for x in atree if (not isinstance(x, list)) or (get_leaf_num(x) >= num)]
    tmp_tree = [remove_tree_leaf_less(x, num) for x in tmp_tree]
    tmp_tree = [x for x in tmp_tree if x != []]
    return tmp_tree



def zone_tree(clust):
    seeds = [1]
    glues = [2,3,6,4,7,5,8]
    tree = [[i+1] for i,c in enumerate(clust) if c in seeds]
    for i in range(len(glues)+1):
        print glues[:i]
        lbs = extract_zone(clust, seeds, glues[:i])
        tmp_tree = [[] for x in range(max(lbs))]
        for subtree in tree:
            tmp_tree[lbs[get_one_leaf(subtree) - 1] - 1].append(subtree)
            # tmp_tree[lbs[get_leafs(subtree)[0] - 1] - 1].append(subtree)
        if i > 0:
            for j,lb in enumerate(lbs):
                if clust[j] == glues[i-1]:
                    tmp_tree[lb - 1].append(j+1)
        tree = tmp_tree
    return tree






