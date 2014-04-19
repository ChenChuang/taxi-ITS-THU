import numpy as npy
import scipy.sparse as spysp
import scipy.io
import psycopg2 as pg
import psycopg2.extras as pgextras

import datetime
import random

import ccgraph as cg

nr = 100
maxiter = 10
tol = 1e-5

def A():
    info = {'nzero':0, 'nall':nr*nr}
    amat = spysp.lil_matrix((nr, nr))
    for i in npy.ndindex((nr,nr)):
        c = random.random()
        if c < 2:
            amat[i] = c*100
            info['nzero'] = info['nzero'] + 1
    print "A done"
    print info
    return [amat, info]

def b():
    print "b done"
    return npy.ones((nr, 1))

def create_Ab_test():
    [amat, info] = A()
    return [amat, b(), info]

def read_Ab_from_file(amatf, bmatf):
    amat = read_mat(amatf)
    bmat = read_mat(bmatf)
    info = {'nzero':0, 'nall':nr*nr}
    return [amat, bmat, info]

def compute():
    x0 = None
    # [amat, bmat, info] = create_Ab_test()
    [amat, bmat, x0, info] = create_Ab_from_db()
    # [amat, bmat, x0, info] = read_Ab_from_file('A.mtx','b.mtx','x0.mtx')

    x = compute_x(amat, bmat, x0)

    wwt = WayWriter()
    wwt.write_profits(x)


def compute_x(amat, bmat, x0):
    callback = Callback()
    
    
    start_at = datetime.datetime.now()
    
    x = spysp.linalg.gmres(amat, bmat, x0=x0, restart=None, xtype=None, M=None, restrt=None, 
            tol = tol, 
            maxiter = maxiter, 
            callback = callback) 
    
    end_at = datetime.datetime.now()
    print info
    print "start:",start_at
    print "end:",end_at
    print "elapsed:",end_at-start_at
    return x 

class Callback:
    def __init__(self):
        self.iters = 0
    def __call__(self, rk):
        print self.iters, rk
        self.iters = self.iters + 1

def cond(amat):
    x = spysp.linalg.lsmr(amat, npy.ones((nr, 1)), damp=0.0, maxiter=None, show=True)
    return x

def write_mat(amat, filename):
    if not filename.endswith('.mtx'):
        filename = filename + '.mtx'
    scipy.io.mmwrite(filename, amat, comment='', field='real', precision=None)

def read_mat(filename):
    if not filename.endswith('.mtx'):
        filename = filename + '.mtx'
    return scipy.io.mmread(filename)

def fare(length):
    return 10

def weight(d):
    return 1

def create_Ab_from_db():
    def push_fs(wid, fs):
        i = wid - 1
        bmat[(i, 0)] = fs[0]
        x0mat[(i, 0)] = fs[0]
        for j, f in enumerate(fs):
            if j == i:
                f = 1 - f
            if j > 0 and f > 0:
                amat[(i, j-1)] = -f

    info = {'nzero':0, 'nall':nr*nr}
    amat = spysp.lil_matrix((nr, nr))
    bmat = npy.zeros((nr, 1))
    x0mat = npy.zeros((nr, 1))
    prd = PathReader()
    gw = cg.new_gw()

    alpha = 0.5
    beta = 0.5

    for wid in xrange(1, nr+1):
        fs = npy.zeros(nr+1)
        for (swid, ewid, length, elonlats) in prd.paths_startwith_wid():
            wsds = gw.find_wsds_within(elonlats, radius=10)
            for (near_wid, d) in wsds:
                fs[near_wid] = fs[near_wid] + weight(d)
            fs[0] = fs[0] + fare(length)
        fs[0] = fs[0] * alpha
        fs[1:] = fs[1:] * beta
        fs[1:] = fs[1:] / sum(fs[1:])
        push_fs(wid, fs)
        
    return [amat, bmat, x0mat, info]

def create_exA_from_db():
    def push_fs(wid, fs):
        x0[wid, 0] = fs[0]
        exa[wid, :] = fs

    info = {'nzero':0, 'nall':nr*nr}
    
    exa = spysp.lil_matrix((nr, nr))
    exa[0,1:] = npy.zeros((1, nr))
    exa[0,0] = 1

    x0 = npy.zeros((nr, 1))
    x0[0,0] = 1
    
    prd = PathReader()
    gw = cg.new_gw()

    alpha = 0.5
    beta = 0.5

    for wid in xrange(1, nr+1):
        fs = npy.zeros(nr+1)
        for (swid, ewid, length, elonlats) in prd.paths_startwith_wid():
            wsds = gw.find_wsds_within(elonlats, radius=10)
            for (near_wid, d) in wsds:
                fs[near_wid] = fs[near_wid] + weight(d)
            fs[0] = fs[0] + fare(length)
        fs[0] = fs[0] * alpha
        fs[1:] = fs[1:] * beta
        fs[1:] = fs[1:] / sum(fs[1:])
        push_fs(wid, fs)
        
    return [exa, x0, info]



class RemoteDB(object):
    def __init__(self, database = "beijing_taxi"):
        self.database = database
        self.user = "chenchuang"
        self.password = "123456"
        self.host = "219.223.168.39"
        self.port = "5432"
        self.open_db()
    
    def __del__(self):
        self.close_db()

    def open_db(self):
        self.conn = None
        self.cursor = None
        try:
            self.conn = pg.connect(
                    database = self.database,
                    user = self.user,
                    password = self.password,
                    host = self.host,
                    port = self.port)
                    self.cursor = self.conn.cursor(cursor_factory = pgextras.DictCursor)
            return True
        except pg.DatabaseError, e:
            print e
            return False

    def close_db(self):
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None


class PathReader(RemoteDB):
    def __init__(self, tbname = ""):
        super(PathReader, self).__init__()
        self.tbname = tbname

    def paths_startwith_wid(wid):
        sql = "select id as pid, tid, tid_s_wid as swid, tid_e_wid as ewid, st_astext(tid_s) as s, st_astext(tid_e) as e, length as l, day from " + self.tbname + " where tid_s_wid = %s"
        self.cursor.execute(sql, (str(wid),))
        while True:            
            row = self.cursor.fetchone()
            if row is None:
                break
            estrs = row['e'][6:-1].split(',')
            elonlats = (float(estrs[0]), float(estrs[1]))
            yield [row['swid'], row['ewid'], row['l'], elonlats]


class WayWriter(RemoteDB):
    def __init__(self, tbname = ""):
        super(WayWriter, self).__init__()
        self.tbname = tbname

    def write_profits(profits):
        for (wid, p) in enumerate(profits):
            sql = "update " + self.tbname + " set (profit) = (%s) where wid = %s"
            self.cursor.execute(sql, (p, wid))
        self.conn.commit()
        
