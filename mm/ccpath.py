import math
import ccgraph as cg
from ccdef import *

def new_path_from_es(gw, tid, es):
    if gw is None:
        return None
    return Path(gw = gw, tid = tid, es = es, ways = None, lonlats = None)

def new_path_from_db(gw, str_tid, str_way_ids, geom):
    tid = int(str_tid)
    ways = ()

    try:
        lonlats = cg.geom2lonlats(geom)
        if not len(lonlats) > 0:
            return None

        ways = []
        for s in str_way_ids.split(','):
            if s == '':
                continue
            ways.append(int(s))
        ways = tuple(ways)
        if not len(ways) > 0:
            return None
    except Exception, e:
        return None

    return Path(gw = gw, tid = tid, es = None, ways = ways, lonlats = lonlats)

class Path:
    def __init__(self, gw, tid, es, ways, lonlats):
        self.gw = gw
        self.tid = tid
        self.es = es
        self.ways = ways
        self.lonlats = lonlats
        if self.es is None and self.gw is not None:
            self.get_es_from_ways()

    def is_valid(self, origin = None, destination = None):
        if self.es is None:
            return False

        l = len(self.es)
        if origin != None:
            if not self.es[0][0] == origin:
                return False
        if destination != None:
            if not self.es[l-1][1] == destination:
                return False

        for i in range(0, l):
            if not self.gw.G.has_edge(self.es[i][0], self.es[i][1]):
                return False
            if i < l-1 and self.es[i][1] != self.es[i+1][0]:
                return False

        return True

    def length(self):
        l = 0.0
        if len(self.es) == 0 and self.gw != None:
            self.get_es_from_ways()
        for e in self.es:
            l = l + self.gw.G[e[0]][e[1]]['length']
        return l

    def precise_length(self, orig_lonlat, dest_lonlat):
        if len(self.es) == 0 and self.gw != None:
            self.get_es_from_ways()

        if len(self.es) == 0:
            l = 0
        if len(self.es) == 1:            
            l = self.gw.proj_p2edge(orig_lonlat, self.es[0])['l_t'] - self.gw.proj_p2edge(dest_lonlat, self.es[0])['l_t']
        else:
            l = self.gw.proj_p2edge(orig_lonlat, self.es[0])['l_t'] + self.gw.proj_p2edge(dest_lonlat, self.es[-1])['l_s']
            for e in self.es[1:-1]:
                l += self.gw.G[e[0]][e[1]]['length']
        return l

    def precise_length_by_wid(self, orig_lonlat, dest_lonlat):
        if len(self.es) == 0 and self.gw != None:
            self.get_es_from_ways()

        if len(self.es) == 0:
            l = []
        if len(self.es) == 1:            
            l = [self.gw.proj_p2edge(orig_lonlat, self.es[0])['l_t'] - self.gw.proj_p2edge(dest_lonlat, self.es[0])['l_t'],]
        else:
            l = [self.gw.proj_p2edge(orig_lonlat, self.es[0])['l_t'],] 
            for e in self.es[1:-1]:
                l.append(self.gw.G[e[0]][e[1]]['length'])
            l.append(self.gw.proj_p2edge(dest_lonlat, self.es[-1])['l_s'])
        return l

    def precise_time(self, orig_lonlat, dest_lonlat):
        if len(self.es) == 0 and self.gw != None:
            self.get_es_from_ways()

        if len(self.es) == 0:
            t = 0
        if len(self.es) == 1:
            e = self.es[0]
            l = self.gw.proj_p2edge(orig_lonlat, e)['l_t'] - self.gw.proj_p2edge(dest_lonlat, e)['l_t']
            t = l / self.gw.G[e[0]][e[1]]['speed']
        else:
            e = self.es[0]
            t1 = self.gw.proj_p2edge(orig_lonlat, e)['l_t'] / self.gw.G[e[0]][e[1]]['speed']
            e = self.es[-1]
            t2 = self.gw.proj_p2edge(dest_lonlat, e)['l_s'] / self.gw.G[e[0]][e[1]]['speed']
            t = t1 + t2
            for e in self.es[1:-1]:
                t += self.gw.G[e[0]][e[1]]['length'] / self.gw.G[e[0]][e[1]]['speed']
        return t
 
    def travel_time(self):
        t = 0.0
        for e in self.es:
            t = t + self.gw.G[e[0]][e[1]]['length'] / self.gw.G[e[0]][e[1]]['speed']
        return t

    def as_geom(self):
        return cg.lonlats2geom(self.get_lonlats())

    def get_lonlats(self):
        if self.lonlats is None or len(self.lonlats) == 0:
            self.get_lonlats_from_es()
        return self.lonlats

    def get_lonlats_from_es(self):
        if not self.is_valid():
            return None
        lonlats = []
        for e in self.es:
            lonlats = lonlats + list(self.gw.G[e[0]][e[1]]['lonlats'])
        self.lonlats = tuple(lonlats)
        return self.lonlats

    def as_ways(self):
        s = str(self.get_ways())
        return s[1:-1]

    def get_ways(self):
        if self.ways is None or len(self.ways) == 0:
            self.get_ways_from_es()
        return self.ways

    def get_ways_from_es(self):
        way_ids = [self.gw.G[e[0]][e[1]]['way_id'] for e in self.es]
        self.ways = tuple(way_ids)
        return self.ways
    
    '''This method has not been tested. 
    But it is rarely used, unless you retrive paths from database.'''
    def get_es_from_ways(self):
        es = [self.gw.st[self.ways[0]],]
        for wid in self.ways[1:]:
            wst = self.gw.st[wid]
            if es[-1][1] != wst[0]:
                wst = wst[::-1]
                if es[-1][1] != wst[0]:
                    es = []
                    break
                try:
                    self.gw.G[wst[0]][wst[1]]
                except KeyError,e:
                    es = []
                    break
            es.append(self.gw.st[wid])

        if len(es) > 0:
            self.es = tuple(es)
            return self.es

        es = [self.gw.st[self.ways[0]][::-1],]
        for wid in self.ways[1:]:
            wst = self.gw.st[wid]
            if es[-1][1] != wst[0]:
                wst = wst[::-1]
                if es[-1][1] != wst[0]:
                    es = []
                    break
                try:
                    self.gw.G[wst[0]][wst[1]]
                except KeyError,e:
                    es = []
                    break
            es.append(self.gw.st[wid])

        if len(es) > 0:
            self.es = tuple(es)
            return self.es 

    def get_es(self):
        if self.es is None or len(self.es) == 0:
            self.get_es_from_ways()
        return self.es

    def summary(self):
        print "%11.5f km %11.5f min" % (self.length(), self.travel_time()*60.0),

    def confidence(self, track):
        ways_ds = self.get_ways_ds_proj(track)
        avg_d = sum(d for (w,d) in ways_ds) / len(ways_ds)
        avg_d_rds = (track.length() / (len(track.rds) - 1))
        c = (0.05 - avg_d) / avg_d_rds
        return c

    def get_ways_ds_proj(self, track):
        ways_ds = []
        es = self.get_es()
        for rd in track.rds:
            lonlat = rd['gps_lonlat']
            d_min = INF
            for e in es:
                d = self.gw.d_p2edge(lonlat, e)
                if d < d_min:
                    d_min = d
                    way_min = self.gw.G[e[0]][e[1]]['way_id']
            if d_min < INF:
                ways_ds.append((way_min, d_min))
        return ways_ds

    def get_proj_lonlats(self, track):
        proj_lonlats = []
        es = self.get_es()
        for rd in track.rds:
            lonlat = rd['gps_lonlat']
            d_min = INF
            for e in es:
                proj = self.gw.proj_p2edge(lonlat, e)
                d = proj['d_proj']
                if d < d_min:
                    d_min = d
                    proj_lonlat = proj['proj_lonlat']
            if d_min < INF:
                proj_lonlats.append(proj_lonlat)
        return proj_lonlats

    def compare(self, gt_path):
        st = self.gw.st
        gw = self.gw
        gt_es = set()
        es = set()
        for wid in gt_path.get_ways():
            e = st[wid]
            i = 1
            while (e[0], e[1], i) in gt_es:
                i += 1
            gt_es.add((e[0], e[1], i))
        for wid in self.get_ways():
            e = st[wid]
            i = 1
            while (e[0], e[1], i) in es:
                i += 1
            es.add((e[0], e[1], i))

        result = {}
        result['matched_length'] = sum([gw.G[s][t]['length'] for s,t,i in (gt_es & es)])
        result['missed_length']  = sum([gw.G[s][t]['length'] for s,t,i in (gt_es - es)])
        result['false_length']   = sum([gw.G[s][t]['length'] for s,t,i in (es - gt_es)])
        return result


