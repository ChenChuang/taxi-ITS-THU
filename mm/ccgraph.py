import sys
import math
import re
import psycopg2 as pg
import psycopg2.extras as pgextras
import networkx as nx
from rtree import index as rtx
from ccdef import *

gw = None

def new_gw(**kwargs):
    global gw
    if gw is not None:
        return gw

    print 'loading...',
    gw = GraphWrapper(**kwargs)
    print 'end'

    print 'creating graph...',
    result = gw.create_graph()
    print 'end'
    # gw.summary()

    print 'creating rtree...',
    result = gw.create_rtree()
    print 'end'

    return gw


class GraphWrapper(object):
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.G = None
        self.__ways_num = None
        self.__oneway_ways_num = None
        self.conn = None
        self.cursor = None
        self.rtree = None
        self.st = None

    def nodes_num(self):
        return len(self.G.nodes())

    def edges_num(self):
        return len(self.G.edges())

    def oneway_edges_num(self):
        n = 0
        for s,t in self.G.edges_iter():
            if not self.G.has_edge(t,s):
                n = n + 1
        return n

    def ways_num(self):
        return self.__ways_num

    def oneway_ways_num(self):
        return self.__oneway_ways_num

    def create_graph(self):
        self.G = nx.DiGraph()
        self.st = {}

        self.__ways_num = 0
        self.__oneway_ways_num = 0

        if not self.open_db():
            return False
        sql = '''select id, 
                 osm_id, osm_source_id, osm_target_id, 
                 clazz, flags, 
                 source, target, 
                 km, kmh, 
                 reverse_cost, 
                 x1, y1, x2, y2, 
                 st_astext(geom_way) as geom from ways'''
        self.cursor.execute(sql)

        while True:
            row = self.cursor.fetchone()
            if row == None:
                break

            way_id = int(row['id'])
            #osm_id = long(row['osm_id'])
            #osm_s_id = long(row['osm_source_id'])
            #osm_t_id = long(row['osm_target_id'])
            #clazz = row['clazz']
            #flags = row['flags']
            s = int(row['source'])
            t = int(row['target'])
            length = float(row['km'])
            speed = float(row['kmh'])
            is_oneway = int(row['reverse_cost']) > 100000
            s_lonlat = (float(row['x1']), float(row['y1']))
            t_lonlat = (float(row['x2']), float(row['y2']))
            lonlats = geom2lonlats(row['geom'])
            
            # length = lonlatlist2km(lonlats)

            self.__ways_num = self.__ways_num + 1

            self.G.add_edge(
                    s, 
                    t, 
                    way_id = way_id, 
                    wid = way_id,
                    weight = 1,
                    time = length / speed,
                    length = length, 
                    speed = speed, 
                    s_lonlat = s_lonlat, 
                    t_lonlat = t_lonlat, 
                    lonlats = lonlats)
            
            if not is_oneway:
                self.G.add_edge(
                        t, 
                        s, 
                        way_id = way_id,
                        wid = way_id,
                        weight = 1,
                        time = length / speed, 
                        length = length, 
                        speed = speed, 
                        s_lonlat = t_lonlat, 
                        t_lonlat = s_lonlat, 
                        lonlats = lonlats[::-1])
            else:
                self.__oneway_ways_num = self.__oneway_ways_num + 1

            self.G.add_node(s, pos = s_lonlat)
            self.G.add_node(t, pos = t_lonlat)

            self.st[way_id] = (s,t)

        self.close_db()
        
        self.nodes_pos = nx.get_node_attributes(self.G, 'pos')

        return True

    def create_rtree(self):
        self.rtree = rtx.Index()
        if self.G == None:
            return False

        uid = 1
        for s,t,d in self.G.edges_iter(data = True):
            lonlats = d['lonlats']
            
            minlon = INF
            minlat = INF
            maxlon = -1
            maxlat = -1

            for lonlat in lonlats:
                if lonlat[0] < minlon:
                    minlon = lonlat[0]
                if lonlat[0] > maxlon:
                    maxlon = lonlat[0]
                if lonlat[1] < minlat:
                    minlat = lonlat[1]
                if lonlat[1] > maxlat:
                    maxlat = lonlat[1]
            
            self.rtree.insert(uid, (minlon, minlat, maxlon, maxlat), obj = (s,t))
            uid = uid + 1
        
        return True

    def find_edges_intersect(self, minlon, minlat, maxlon, maxlat):
        return tuple( [n.object for n in self.rtree.intersection((minlon, minlat, maxlon, maxlat), objects = True)] )

    def find_projs_within(self, lonlat, radius):
        latgap = km2latgap(radius)
        longap = km2longap(radius, lonlat[1])
        
        es = self.find_edges_intersect(
                minlon = lonlat[0] - longap,
                minlat = lonlat[1] - latgap,
                maxlon = lonlat[0] + longap,
                maxlat = lonlat[1] + latgap)
        
        projs = []
        for e in es:
            proj = self.proj_p2edge(lonlat, e)
            if proj['d_proj'] < radius:
                projs.append(proj)

        return tuple(projs)
    
    def find_wsds_within(self, lonlat, radius):
        latgap = km2latgap(radius)
        longap = km2longap(radius, lonlat[1])
        
        es = self.find_edges_intersect(
                minlon = lonlat[0] - longap,
                minlat = lonlat[1] - latgap,
                maxlon = lonlat[0] + longap,
                maxlat = lonlat[1] + latgap)
        
        wsds = []
        for e in es:
            proj = self.proj_p2edge(lonlat, e)
            if proj['d_proj'] < radius:
                wsds.append((self.G[e[0]][e[1]]['wid'], proj['d_proj']))

        return wsds

    def find_wsds_within_rough(self, lonlat, radius):
        latgap = km2latgap(radius)
        longap = km2longap(radius, lonlat[1])
        
        es = self.find_edges_intersect(
                minlon = lonlat[0] - longap,
                minlat = lonlat[1] - latgap,
                maxlon = lonlat[0] + longap,
                maxlat = lonlat[1] + latgap)
        
        wsds = []
        for e in es:
            d = min(lonlats2km(lonlat, self.nodes_pos[e[0]]), 
                    lonlats2km(lonlat, self.nodes_pos[e[1]]))
            if d < radius:
                wsds.append((self.G[e[0]][e[1]]['wid'], d))

        return wsds

    def find_wsds_within_rough(self, lonlat, radius):
        latgap = km2latgap(radius)
        longap = km2longap(radius, lonlat[1])
        
        es = self.find_edges_intersect(
                minlon = lonlat[0] - longap,
                minlat = lonlat[1] - latgap,
                maxlon = lonlat[0] + longap,
                maxlat = lonlat[1] + latgap)
        
        wsds = []
        for e in es:
            d = min(lonlats2km(lonlat, self.nodes_pos[e[0]]), 
                    lonlats2km(lonlat, self.nodes_pos[e[1]]))
            if d < radius:
                wsds.append((self.G[e[0]][e[1]]['wid'], d))

        return wsds

    def find_projs_nearest(self, lonlat, maxr):
        r = min(maxr, 0.05)

        while r <= maxr:
            projs = self.find_projs_within(lonlat, r)
            if len(projs) > 0:
                d_min = INF
                nproj = None
                for proj in projs:
                    if proj['d_proj'] < d_min:
                        nproj = proj
                return nproj
            r = min(maxr, r * 2)

    def d_p2edge(self, lonlat, edge):
        s = edge[0]
        t = edge[1]
        lonlats = self.G[s][t]['lonlats']
        d_min = INF
        for i in range(0, len(lonlats)-1):
            s_lonlat = lonlats[i]
            t_lonlat = lonlats[i+1]
            d = d_p2seg(lonlat, s_lonlat, t_lonlat)
            if d < d_min:
                d_min = d
        return d_min
       
    def proj_p2edge(self, p_lonlat, edge):
        s = edge[0]
        t = edge[1]
        lonlats = self.G[s][t]['lonlats']
        d_min = INF
        for i in range(0, len(lonlats)-1):
            s_lonlat = lonlats[i]
            t_lonlat = lonlats[i+1]
            d = d_p2seg(p_lonlat, s_lonlat, t_lonlat)
            if d < d_min:
                d_min = d
                i_d_min = i
        
        s_lonlat = lonlats[i_d_min]
        t_lonlat = lonlats[i_d_min+1]
        
        tt = proj_p2seg(p_lonlat, s_lonlat, t_lonlat)

        if tt <= 0:
            l_s = 0
        elif tt >= 1:
            l_s = lonlats2km(s_lonlat, t_lonlat)
        else:
            l_s = lonlats2km(s_lonlat, t_lonlat) * tt
        
        for i in range(0, i_d_min):
            l_s = l_s + lonlats2km(lonlats[i], lonlats[i+1])
        
        l_t = self.G[s][t]['length'] - l_s

        proj_lonlat = ( (1-tt) * s_lonlat[0] + tt * t_lonlat[0], (1-tt) * s_lonlat[1] + tt * t_lonlat[1] )  

        return {'d_proj':d_min, 'l_s':l_s, 'l_t':l_t, 'proj_lonlat':proj_lonlat, 's':s, 't':t}

    def close_db(self):
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def open_db(self):
        self.conn = None
        self.cursor = None
        try:
            database = self.kwargs['database']
        except KeyError, e:
            database = 'beijing_mm_po_car'
        try:
            user = self.kwargs['user']
        except KeyError, e:
            user = 'postgres'
        try:
            password = self.kwargs['password']
        except KeyError, e:
            password = '123456'
        try:
            host = self.kwargs['host']
        except KeyError, e:
            host = 'localhost'
        try:
            port = self.kwargs['port']
        except KeyError, e:
            port = '5432' 

        try:
            self.conn = pg.connect(
                    database = database,
                    user = user,
                    password = password,
                    host = host,
                    port = port)
            self.cursor = self.conn.cursor(cursor_factory = pgextras.DictCursor)
            return True
        except pg.DatabaseError, e:
            print e
            return False

    def shortest_path_from_to(self, origin, destination, weight, **kwargs):
        try:
            vs = nx.shortest_path(self.G, origin, destination, weight=weight)
        except Exception, e:
            #print e
            return ()

        es = []
        for i in range(0,len(vs)-1):
            es.append( (vs[i], vs[i+1]) )
        return tuple(es)

    '''This is a very slow method, it seems correct, but DO NOT use it'''
    def paths_from_to_shorter_than(self, origin, destination, max_length, method='astar'):
        
        def isbackward(ne, ti, tj):
            while tj is not None:
                e = tree[ti][tj][0]
                tj = tree[ti][tj][1]
                if e[0] == ne[1] or e[1] == ne[1]:
                    return True
                ti -= 1
            return False
        
        print "m:",max_length,"origin:",origin,"dest:",destination
        tree = []
        tree.append([[e, None, self.G[e[0]][e[1]]['length'], self.d_between_nodes(e[1], destination)] for e in self.G.out_edges(nbunch=origin)])
        iscontinue = True
        while iscontinue:
            tier = []
            
            for j,[e,pre,w,dmin] in enumerate(tree[-1]):
                if e[1] == destination:
                    #print 'aaa'
                    continue
                
                for ne in self.G.out_edges(nbunch=e[1]):
                    if isbackward(ne, len(tree)-1, j):
                        continue
                    nw = w + self.G[ne[0]][ne[1]]['length']
                    d2dest = self.d_between_nodes(ne[1], destination)
                    if d2dest < dmin*1.1 and (nw + d2dest*1.2) < max_length:
                        tier.append([ne, j, nw, min(d2dest, dmin)])
            #print i,tier_i
            if len(tier) > 0:
                tree.append(tier)
            else:
                iscontinue = False

        paths = []
        for i,tier in enumerate(tree):
            # print i,len(tier)
            for e,pre,w,dmin in tier:
                if e[1] == destination:
                   p = [e,]
                   tmp_pre = pre
                   tmp_i = i
                   while tmp_pre is not None:
                       assert destination not in tree[tmp_i-1][tmp_pre][0]
                       p.append(tree[tmp_i-1][tmp_pre][0])
                       tmp_pre = tree[tmp_i-1][tmp_pre][1]
                       tmp_i -= 1
                   p.reverse()
                   paths.append(p)

        print "paths:",
        if len(paths) > 0:
            print len(paths), sum([len(p) for p in paths])/len(paths)
        else:
            print ""
        return paths

    def is_turn_between_es(self, ea, eb):
        if ea[1] != eb[0]:
            raise Exception('error in is_turn_between_es')
        cv = ea[1]
        in_es = self.G.in_edges(nbunch = cv)
        out_es = self.G.out_edges(nbunch = cv)
        n_in = len(in_es)
        n_out = len(out_es)
        angle_ea_eb = self.angle_between_es(ea, eb)
        angles_in_eb  = [self.angle_between_es(in_e,  eb) for in_e  in in_es ]
        angles_ea_out = [self.angle_between_es(ea, out_e) for out_e in out_es]

        if n_in == 1 and n_out == 1:
            return False
        if angle_ea_eb == min(angles_in_eb) and angle_ea_eb == min(angles_ea_out):
            return False
        return True

    def angle_between_es(self, ea, eb):
        a_lonlats = self.G[ea[0]][ea[1]]['lonlats']
        a1 = a_lonlats[-2]
        a2 = a_lonlats[-1]
        
        b_lonlats = self.G[eb[0]][eb[1]]['lonlats']
        b1 = b_lonlats[0]
        b2 = b_lonlats[1]

        return angle_between_lonlats(a1,a2,b1,b2)

    def d_between_nodes(self, na, nb):
        a_lonlat = self.nodes_pos[na]
        b_lonlat = self.nodes_pos[nb]
        return lonlats2km(a_lonlat, b_lonlat)

    def time_of_edges(self, es):
        w = 0
        for e in es:
            w = w + self.G[e[0]][e[1]]['time']
        return w

    def length_of_edges(self, es):
        l = 0
        for e in es:
            l = l + self.G[e[0]][e[1]]['length']
        return l

    def wids_of_edges(self, es):
        return self.get_edges_attr(es, 'way_id')

    def get_edges_attr(self, es, attr):
        attrs = []
        for e in es:
            attrs.append(self.G[e[0]][e[1]][attr])
        return tuple(attrs)

    def summary(self):
        print 'G:','node_num:',self.nodes_num(),'edge_num:',self.edges_num(),'oneway_ways_oum:',self.oneway_ways_num()

    def save_fig(self, filepath):
        import matplotlib.pyplot as plt
        pos = nx.get_node_attributes(self.G, 'pos')
        print 'drawing ...',
        nx.draw_networkx_edges(self.G, pos = pos, width = 0.02, arrows = False)
        print 'writing ...',
        plt.savefig(filepath)
        print 'end'

    def save_gexf(self, filepath):
        nx.write_gexf(self.G, filepath)

def lonlats2km(s_lonlat, t_lonlat):
    dlat = 111.0 * abs(s_lonlat[1] - t_lonlat[1])
    dlon = 111.0 * abs(math.cos(math.radians((s_lonlat[1] + t_lonlat[1]) / 2))) * abs(s_lonlat[0] - t_lonlat[0])
    return math.sqrt(dlat**2 + dlon**2)

def lonlatlist2km(lonlats):
    return sum([lonlats2km(x,y) for x,y in zip(lonlats[:-1], lonlats[1:])])

def km2latgap(d):
    return d / 111.0

def km2longap(d, lat):
    return d / 111.0 / abs(math.cos(math.radians(lat)))

def lonlat2xykm(lonlat):
    return (111.0 * abs(math.cos(math.radians(lonlat[1]))) * lonlat[0], 111.0 * lonlat[1])

def angle_between_lonlats(a1,a2,b1,b2):
    a1_xy = lonlat2xykm(a1)
    a2_xy = lonlat2xykm(a2)
    b1_xy = lonlat2xykm(b1)
    b2_xy = lonlat2xykm(b2)
    
    a = [a2_xy[0] - a1_xy[0], a2_xy[1] - a1_xy[1]]
    b = [b2_xy[0] - b1_xy[0], b2_xy[1] - b1_xy[1]]

    v = (a[0]*b[0] + a[1]*b[1]) / math.sqrt(a[0]**2 + a[1]**2) / math.sqrt(b[0]**2 + b[1]**2)
    v = min(v, 1)
    v = max(v, -1)
    return math.acos(v)

def d_p2p(s_xy, t_xy):
    return math.sqrt((s_xy[0] - t_xy[0])**2 + (s_xy[1] - t_xy[1])**2)

def d_p2seg(p_lonlat, s_lonlat, t_lonlat):
    p_xy = lonlat2xykm(p_lonlat)
    s_xy = lonlat2xykm(s_lonlat)
    t_xy = lonlat2xykm(t_lonlat)
    ps = d_p2p(p_xy, s_xy)
    pt = d_p2p(p_xy, t_xy)
    st = d_p2p(s_xy, t_xy)
    if ps < 0.000001 or pt < 0.000001:
        return 0.0
    if st < 0.000001:
        return (ps + pt) / 2
    if ps**2 >= pt**2 + st**2:
        return pt
    if pt**2 >= ps**2 + st**2:
        return ps
    l = (ps + pt + st) / 2
    try:
        a = math.sqrt(l * (l-ps) * (l-pt) * (l-st))
    except:
        return 0
    return 2 * a / st

def proj_p2seg(p_lonlat, s_lonlat, t_lonlat):
    p_xy = lonlat2xykm(p_lonlat)
    s_xy = lonlat2xykm(s_lonlat)
    t_xy = lonlat2xykm(t_lonlat)
    st_xy = (t_xy[0] - s_xy[0], t_xy[1] - s_xy[1])
    if st_xy[0] == 0 and st_xy[1] == 0:
        return 0
    t = ( (p_xy[0] - s_xy[0])*st_xy[0] + (p_xy[1] - s_xy[1])*st_xy[1] ) / (st_xy[0]**2 + st_xy[1]**2)
    return t

def geom2lonlats(geom):
    try:
        str_lonlats = re.search('^LINESTRING\((.*)\)$', geom).group(1).split(',')
        lonlats = []
        for s in str_lonlats:
            if s == '':
                continue
            lon = float(s.split(' ')[0])
            lat = float(s.split(' ')[1])
            lonlats.append( (lon, lat) )
        return tuple(lonlats)

    except Exception,e:
        print e
        return None

def lonlats2geom(lonlats):
    sg = "LINESTRING("
    for lonlat in lonlats:
        sg = sg + str(lonlat[0]) + " " + str(lonlat[1]) + ","
    sg = sg[:-1]
    sg = sg + ")"
    return sg

def lonlats2hough(s_lonlat, t_lonlat, o_lonlat=[0,0]):
    s = list(lonlat2xykm(s_lonlat))
    t = list(lonlat2xykm(t_lonlat))
    o = list(lonlat2xykm(o_lonlat))
    return xys2hough(s,t,o)

def xys2hough(s, t, o=[0,0]):
    s[0] -= o[0]
    s[1] -= o[1]
    t[0] -= o[0]
    t[1] -= o[1]
    A = s[1] - t[1]
    B = t[0] - s[0]
    C = (t[1] - s[1])*s[0] + (s[0] - t[0])*s[1]
    if A == 0 and B == 0:
        return None
    d = abs(C) / math.sqrt(A**2 + B**2)
    if abs(B) > 0.0001:
        angle = math.atan(-A/B)
    else:
        angle = math.pi / 2
    if B < 0:
        angle = angle + math.pi
    if angle < 0:
        angle = angle + math.pi*2
    return [d, angle]




