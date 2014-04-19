import numpy as npy
import scipy.sparse as spysp
import scipy.sparse.linalg as spyalg
import scipy.io
import psycopg2 as pg
import psycopg2.extras as pgextras

import datetime
import random

import sys, os
mmpath = os.path.join(os.getcwd(), '..', 'mm')
sys.path.insert(0, mmpath)
import ccgraph as cg
del sys.path[0]

nr = 49122
nv = nr
var = None
varloc = None

maxiter = 10
tol = 1e-5

def compute():
    x0 = None
    # [amat, bmat, info] = create_Ab_test()
    [amat, bmat, x0, info] = create_Ab_from_db()
    # [amat, bmat, x0, info] = read_Ab_from_file('A.mtx','b.mtx','x0.mtx')

    x = compute_x(amat, bmat, x0)

    wwt = WayWriter()
    wwt.write_profits(x)

def compute_x(amat, bmat, x0, info=None):
    callback = Callback()
    
    start_at = datetime.datetime.now()
    
    x = spyalg.gmres(amat, bmat, x0=x0, restart=None, xtype=None, M=None, restrt=None, 
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
    x = spysp.linalg.lsmr(amat, npy.ones((nv, 1)), damp=0.0, maxiter=None, show=True)
    return x

def create_var_from_db():
    global var
    # var = range(1, nr+1)
    var = range(1, 20)
    global nv
    nv = len(var)
    global varloc
    varloc = range(-1, nr)

def fare(length):
    return length

def weight(d):
    return 1

def isvar(wid):
    return 1 <= wid <= nv
    # return wid in var

def create_Ab_from_db():
    def push_fs(wid, fs):
        i = wid - 1
        bmat[(i, 0)] = fs[0]
        x0mat[(i, 0)] = fs[0]
        for j, f in enumerate(fs[1:]):
            if j == i:
                f = f - 1
            if f != 0:
                amat[(i, j)] = -f

    start_at = datetime.datetime.now() 

    create_var_from_db()

    info = {'nnz':0, 'nall':nv*nv}
    amat = spysp.lil_matrix((nv, nv))
    bmat = npy.zeros((nv, 1))
    x0mat = npy.zeros((nv, 1))
    prd = PathReader()
    gw = cg.new_gw(
            database='beijing_mm_po', 
            user='chenchuang', 
            password='123456',
            host='219.223.168.39',
            port='5432')

    alpha = 0.5
    beta = 0.5

    for i, wid in enumerate(var):
        print i, wid, 
        fs = npy.zeros(nv+1)
        pcount = 0
        for (swid, ewid, length, elonlats) in prd.paths_startwith_wid(wid):
            pcount = pcount + 1
            wsds = gw.find_wsds_within(elonlats, radius=2)
            for (near_wid, d) in wsds:
                if isvar(near_wid):
                    near_i = varloc[near_wid]
                    fs[near_i] = fs[near_i] + weight(d)
            fs[0] = fs[0] + fare(length)
        print "pcount:", pcount, 
        fs[0] = fs[0] * alpha
        fsum = sum(fs[1:])
        if fsum > 0:
            fs[1:] = fs[1:] / fsum
            fs[1:] = fs[1:] * beta
        push_fs(wid, fs)
        print "done"
    

    end_at = datetime.datetime.now()
    print "start:",start_at
    print "end:",end_at
    print "elapsed:",end_at - start_at
 
    info['nnz'] = amat.nnz
    return [amat, bmat, x0mat, info]

# Ax = b
# b + (I-A)x = x
# 1   0     1   1
# b (I-A) * x = x
def create_exA_from_Ab(amat, bmat):
    tnv = bmat.shape[0] + 1
    info = {'nnz':0, 'nall':tnv*tnv}
    exa = spysp.lil_matrix((tnv, tnv))
    
    x0mat = npy.ones((tnv, 1))
    x0mat[1:, 0] = bmat[:,0]
    
    exa[0,0] = 1
    exa[0,1:] = 0
    exa[1:,0] = bmat
    exa[1:,1:] = spysp.eye(tnv-1) - amat
 
    info['nnz'] = amat.nnz
    return [exa, x0mat, info] 

class RemoteDB(object):
    def __init__(self, database = "beijing_taxi_201211"):
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
    def __init__(self, tbname = "track_information_201211"):
        super(PathReader, self).__init__()
        self.tbname = tbname

    def paths_startwith_wid(self, wid):
        sql = "select id as pid, tid, \
            tid_s_lon as slon, \
            tid_s_lat as slat, \
            tid_s_wid as swid, \
            tid_e_lon as elon, \
            tid_e_lat as elat, \
            tid_e_wid as ewid, tid_length as l, day from " + self.tbname + " where tid_s_wid = %s"
        self.cursor.execute(sql, (str(wid),))
        while True:            
            row = self.cursor.fetchone()
            if row is None:
                break
            elonlats = (row['elon'], row['elat'])
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


def write_mat(amat, filename):
    if not filename.endswith('.mtx'):
        filename = filename + '.mtx'
    scipy.io.mmwrite(filename, amat, comment='', field='real', precision=None)

def read_mat(filename):
    if not filename.endswith('.mtx'):
        filename = filename + '.mtx'
    return scipy.io.mmread(filename).tolil()

def read_Ab_from_file(amatf, bmatf):
    amat = read_mat(amatf)
    bmat = read_mat(bmatf)
    info = {'nnz':amat.nnz, 'nall':nv*nv}
    return [amat, bmat, info]


def A():
    info = {'nnz':0, 'nall':nv*nv}
    amat = spysp.lil_matrix((nv, nv))
    for i in npy.ndindex((nv,nv)):
        c = random.random()
        if c < 2:
            amat[i] = c*100
    print "A done"
    info['nnz'] = amat.nnz
    return [amat, info]

def b():
    print "b done"
    return npy.ones((nv, 1))

def create_Ab_test():
    [amat, info] = A()
    return [amat, b(), info]

def print_mat(m, ur, dr, lc, rc):
    for i in xrange(ur, dr):
        for j in xrange(lc, rc):
            if m[i,j] != 0:
                print "{:5.2f}".format(m[i,j]), 
            else:
                print " "*5,
        print ""


