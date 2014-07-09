import numpy as npy
import scipy.sparse as spysp
import scipy.sparse.linalg as spyalg
import scipy.io
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
from ccdb import DB
del sys.path[0]

nr = 49122
nv = nr
var = None
varloc = None

maxiter = 30000
tol = 1e-5

def compute(dirname='', todir='', cores=3, alpha=0.5, beta=0.5, amat=None, bmat=None, x0mat=None):
    print "start to load A,b,x0"
    start_at = datetime.datetime.now()

    # x0mat = None

    read_var_from_dir(dirname)
    
    # [amat, bmat, info] = create_Ab_test()
    # [amat, bmat, x0mat, info] = create_Ab_from_db()
    # [amat, bmat, x0mat, info] = read_Ab_from_file('testamat.mtx','testbmat.mtx','testbmat.mtx')
    if amat is None or bmat is None or x0mat is None:
        [amat, bmat, x0mat, info] = read_Ab_from_dir(dirname, cores)
    
    print "start to refine A,b,x0"
    [amat, bmat, x0mat] = refine_Ab(amat, bmat, alpha, beta)

    end_at = datetime.datetime.now()
    print "start:",start_at
    print "end:",end_at
    print "elapsed:",end_at-start_at
    # print info
    print ""
    
    callback = Callback(dirname + 'res.log')

    xmat = compute_x(amat, bmat, x0mat, callback)

    write_mat(xmat, todir + 'xmat.mtx')
    
    # wwt = WayWriter()
    # wwt.update_score(xmat[:,0])
    return xmat

def compute_x(amat, bmat, x0, callback):
    print "start to compute x"
    start_at = datetime.datetime.now()
    
    print ""
    x, info = spyalg.gmres(amat, bmat, x0=x0, restart=None, xtype=None, M=None, restrt=None, 
            tol = tol, 
            maxiter = maxiter, 
            callback = callback) 
    print ""
    
    callback.finish()

    end_at = datetime.datetime.now()
    print "start:",start_at
    print "end:",end_at
    print "elapsed:",end_at-start_at

    xmat = npy.zeros((len(x), 1))
    xmat[:,0] = x
 
    return xmat 

class Callback:
    def __init__(self, logf):
        self.iters = 0
        self.logf = logf
        self.f = open(logf, 'w')
    
    def __del__(self):
        self.f.close()

    def finish(self):
        self.f.close()
        self.f = open(self.logf, 'w')

    def __call__(self, rk):
        print self.iters, rk
        self.f.write(','.join([str(self.iters), str(rk)]))
        self.f.write('\n')
        self.iters = self.iters + 1

def cond(amat):
    x = spysp.linalg.lsmr(amat, npy.ones((nv, 1)), damp=0.0, maxiter=None, show=True)
    return x

def create_var_from_db(dirname=''):
    lnpick = 20

    global var
    wwt = WayWriter()
    var = wwt.wids_npick_gt(lnpick-1)
    # var = range(1, nr+1)
    # var = range(1, 20)
    global nv
    nv = len(var)
    global varloc
    # varloc = range(-1, nr)
    varloc = -npy.ones(nr+1)
    for i, wid in enumerate(var):
        varloc[wid] = i
    
    varmat = npy.zeros((nv, 1))
    varmat[:,0] = var
    write_mat(varmat, dirname + 'var.mtx')
    
    with open(dirname + 'args.txt', 'a') as argsf:
        argsf.write('npick >= '  + str(lnpick)  + '\n')

def read_var_from_dir(dirname=''):
    varmat = read_mat(dirname + 'var.mtx')
    global var
    var = list(varmat[:,0])
    global nv
    nv = len(var)
    global varloc
    varloc = -npy.ones(nr+1)
    for i, wid in enumerate(var):
        varloc[wid] = i

def fare_length(length):
    return length

def fare_rmb(length):
    if length < 3.0:
        return 10.0 + 3.0
    if length < 15.0:
        return 10.0 + (length - 10.0) * 2.0 + 3.0
    else:
        return 20.0 + (length - 15.0) * 3.0 + 3.0

def make_unif(scale):
    return lambda x: scale

def make_norm(mean, stderr):
    return lambda x: 1 / ( stderr * (math.pi*2)**0.5 ) * math.exp( (x - mean)**2 / (-2.0 * stderr**2) )

def refine_Ab(amat, bmat, alpha, beta):
    eye = spysp.eye(nv)
    iamat = eye - amat
    ramat = eye - iamat * alpha
    rbmat = bmat * beta
    rx0mat = rbmat
    return [ramat, rbmat, rx0mat]
    

def create_Ab_from_db(fri=None, toi=None, core=0, write=True, dirname='', **kwargs):
    try:
        alpha = kwargs['alpha']
        beta = kwargs['beta']
        radius = kwargs['radius']
    
        if kwargs['weight'] == 'unif':
            weight = make_unif(1.0)
        elif kwargs['weight'] == 'norm':
            weight = make_norm(0, kwargs['stderr'])

        if kwargs['fare'] == 'length':
            fare = fare_length
        elif kwargs['fare'] == 'rmb':
            fare = fare_rmb
    except Exception, e:
        print 'args error:', e
        return

    
    with open(dirname + 'args.txt', 'a') as argsf:
        argsf.write('alpha = '  + str(alpha)  + '\n')
        argsf.write('beta = '   + str(beta)   + '\n')
        argsf.write('radius = ' + str(radius) + '\n')
        argsf.write('fare = ' + kwargs['fare'] + '\n')
        argsf.write('weight = ' + kwargs['weight'] + '\n')
        argsf.write('stderr = ' + kwargs['stderr'] + '\n')
    
    def isvar(wid):
        # return 1 <= wid <= nv
        # return wid in var
        return varloc[wid] >= 0

    def push_fs(wid, fs):
        i = varloc[wid]
        bmat[(i, 0)] = fs[0]
        x0mat[(i, 0)] = fs[0]
        for j, f in enumerate(fs[1:]):
            if j == i:
                f = f - 1
            if f != 0:
                amat[(i, j)] = -f
   
    if fri is None:
        fri = 0
    if toi is None:
        toi = len(var)
    toi = min(len(var), toi)
    print "core:", core, "from index:", fri, "to index:", toi

    start_at = datetime.datetime.now() 

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

    for i, wid in enumerate(var[fri:toi]):
        i = i + fri
        print core, i, wid 
        fs = npy.zeros(nv+1)
        pcount = 0
        for (swid, ewid, elon, elat, length) in prd.paths_startwith_wid(wid):
            pcount = pcount + 1
            wsds = gw.find_wsds_within_rough((elon, elat), radius=radius)
            for (near_wid, d) in wsds:
                if isvar(near_wid):
                    near_i = varloc[near_wid]
                    fs[near_i] = fs[near_i] + weight(d)
            fs[0] = fs[0] + fare(length)
        # print "pcount:", pcount, 
        fs[0] = fs[0] * alpha
        fsum = sum(fs[1:])
        if fsum > 0:
            fs[1:] = fs[1:] / fsum
            fs[1:] = fs[1:] * beta
        push_fs(wid, fs)
        # print "done"
    

    end_at = datetime.datetime.now()
    print "start:",start_at
    print "end:",end_at
    print "elapsed:",end_at - start_at
    if write:
        write_mat(amat, dirname + 'amat_'+str(core))
        write_mat(bmat, dirname + 'bmat_'+str(core))
        write_mat(x0mat, dirname + 'x0mat_'+str(core))
 
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
            self.cursor = self.conn.cursor()
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
        sql = "select \
            tid_s_wid, \
            tid_e_wid, \
            tid_e_lon, \
            tid_e_lat, \
            tid_length from " + self.tbname + " where tid_s_wid = %s"
        self.cursor.execute(sql, (str(wid),))
        rows = self.cursor.fetchall()
        return rows

    def npick(self, wid):
        sql = "select count(*) from " + self.tbname + " where tid_s_wid = %s"
        self.cursor.execute(sql, (str(wid),))
        return int(self.cursor.fetchone()[0])
    
    def ndrop(self, wid):
        sql = "select count(*) from " + self.tbname + " where tid_e_wid = %s"
        self.cursor.execute(sql, (str(wid),))
        return int(self.cursor.fetchone()[0])

class PathTransfer(DB):
    def __init__(self, swid):
        super(PathTransfer, self).__init__(database='tempdb')
        self.tbname = "paths_startwith_" + str(swid)
        self.swid = swid

    def create_tb(self):
        sql = "create table " + self.tbname + "( \
                swid int not null, \
                ewid int not null, \
                s_geom geometry not null, \
                e_geom geometry not null, \
                path_geom geometry not null);"
        try:
            self.cursor.execute(sql)
            self.conn.commit()
            print "table", self.tbname,"created"
        except Exception, e:
            print e
            self.conn.rollback()

    def transfer(self):
        rdb = RemoteDB()
        for i in xrange(1, 21):
            print i,
            day = str(i)
            if i < 10:
                day = "0" + day
            day = "201211" + day
            sql = "select tid_s_wid, tid_s_lon, tid_s_lat, tid_e_wid, tid_e_lon, tid_e_lat, st_astext(path_geom) as geom from taxi_paths_occupied_crusing_st_" + day + \
                " as paths, track_information_201211 as info where paths.tid = info.tid and info.day = '" + day + "'" + \
                " and info.tid_s_wid = " + str(self.swid) + ";"
            try:
                rdb.cursor.execute(sql)
                rows = rdb.cursor.fetchall()
            except:
                continue
            try:
                for row in rows:
                    sql = "insert into " + self.tbname + "(swid, ewid, s_geom, e_geom, path_geom) values (%s,%s,%s,%s,%s)"
                    args = (row[0], row[3], ('POINT(%f %f)' % (row[1], row[2])), ('POINT(%f %f)' % (row[4], row[5])), row[6])
                    self.cursor.execute(sql, args)
                self.conn.commit()
            except Exception, e:
                print e
                self.conn.rollback()
                continue
        print "transfer done"

def transfer_startwith(wid):
    pt = com.PathTransfer(wid)
    pt.create_tb()
    pt.transfer()

def update_score_from_dir(dirname=''):
    read_var_from_dir(dirname)
    xmat = read_mat(dirname + 'xmat.mtx')
    wwt = WayWriter()
    wwt.update_score(xmat[:,0])


class WayWriter(RemoteDB):
    def __init__(self, tbname = "road_score"):
        super(WayWriter, self).__init__(database="beijing_mm_po")
        self.tbname = tbname

    def update_score(self, scores):
        sql = "update " + self.tbname + " set (score) = (0.0)"
        self.cursor.execute(sql)
        self.conn.commit()
        for (i, s) in enumerate(scores):
            wid = var[i]
            print i, wid
            sql = "update " + self.tbname + " set (score) = (%s) where wid = %s"
            self.cursor.execute(sql, (s, wid))
        self.conn.commit()

    def update_npick(self):
        prd = PathReader()
        for wid in xrange(1, nr+1):
            print wid
            n = prd.npick(wid)
            sql = "update " + self.tbname + " set (pickup_num) = (%s) where wid = %s"
            self.cursor.execute(sql, (n, wid))
        self.conn.commit()
    
    def update_ndrop(self):
        prd = PathReader()
        for wid in xrange(1, nr+1):
            print wid
            n = prd.ndrop(wid)
            sql = "update " + self.tbname + " set (dropoff_num) = (%s) where wid = %s"
            self.cursor.execute(sql, (n, wid))
        self.conn.commit()

    def wids_npick_gt(self, n):
        sql = "select wid from " + self.tbname + " where pickup_num > %s order by wid"
        self.cursor.execute(sql, (n,))
        ws = self.cursor.fetchall()
        return [w[0] for w in ws]
    
    def init_road_score(self):
        for wid in xrange(1, nr+1):
            sql = "insert into " + self.tbname + " values (%s, 0, 0, 0)"
            self.cursor.execute(sql, (wid,))
        self.conn.commit()

def write_mat(amat, filename):
    if not filename.endswith('.mtx'):
        filename = filename + '.mtx'
    scipy.io.mmwrite(filename, amat, comment='', field='real', precision=None)

def read_mat(filename):
    if not filename.endswith('.mtx'):
        filename = filename + '.mtx'
    mat = scipy.io.mmread(filename)
    if spysp.isspmatrix(mat):
        mat = mat.tolil()
    return mat

def read_Ab_from_file(amatf, bmatf, x0matf):
    amat = read_mat(amatf)
    bmat = read_mat(bmatf)
    x0mat = read_mat(x0matf)
    info = {'nnz':amat.nnz, 'nall':nv*nv}
    return [amat, bmat, x0mat, info]

def read_Ab_from_dir(dirname, n):
    print "reading A ...",
    try:
        amat = read_mat(dirname + 'amat_0.mtx')
    except:
        amat = spysp.lil_matrix((nv, nv))
        for i in range(1, n+1):
            print i,
            amat = amat + read_mat(dirname + 'amat_' + str(i) + '.mtx')
        write_mat(amat, dirname + 'amat_0.mtx')
    print "done"
    print "reading b ...",
    try:
        bmat = read_mat(dirname + 'bmat_0.mtx')
    except:
        bmat = npy.zeros((nv, 1))
        for i in range(1, n+1):
            print i,
            bmat = bmat + read_mat(dirname + 'bmat_' + str(i) + '.mtx')
        write_mat(bmat, dirname + 'bmat_0.mtx')
    print "done"
    print "reading x0 ...",
    try: 
        x0mat = read_mat(dirname + 'x0mat_0.mtx')
    except:
        x0mat = npy.zeros((nv, 1))
        for i in range(1, n+1):
            print i,
            x0mat = x0mat + read_mat(dirname + 'x0mat_' + str(i) + '.mtx')
        write_mat(x0mat, dirname + 'x0mat_0.mtx')
    print "done"
    info = {'nnz':amat.nnz, 'nall':nv*nv}
    return [amat, bmat, x0mat, info]


def A_slow():
    info = {'nnz':0, 'nall':nv*nv}
    amat = spysp.lil_matrix((nv, nv))
    for i in xrange(0,nv):
        s = 0
        for j in xrange(0,nv):
            c = random.random()
            if c < 0.01:
                amat[i,j] = c*100
                s = s + amat[i,j]
        for j in xrange(0,nv):
            if amat[i,j] > 0:
                amat[i,j] = amat[i,j] / s / 2
        print i
    print "A done"
    info['nnz'] = amat.nnz
    return [amat, info]

def A():
    info = {'nnz':0, 'nall':nv*nv}
    amat = spysp.lil_matrix((nv, nv))
    rnv = 4000
    js = npy.zeros(rnv)
    pi = 0
    for i in xrange(0, rnv):
        c = random.random()
        i = int(c*nv)
        if i >= nv:
            i = nv-1
        s = 0
        for k in xrange(0, rnv):
            c = random.random()
            j = int(c*nv)
            if j >= nv:
                j = nv-1
            js[k] = j
            c = random.random()
            amat[i,j] = c*100
            s = s + amat[i,j]
        for j in js:
            amat[i,j] = amat[i,j] / s / 2
        pi = pi + 1
        print pi
    print "A done"
    info['nnz'] = amat.nnz
    return [amat, info]


def b():
    print "b done"
    return npy.ones((nv, 1))

def create_Ab_test():
    global nv
    nv = 40000
    [amat, info] = A()
    bmat = b()
    write_mat(amat, 'testamat.mtx')
    write_mat(bmat, 'testbmat.mtx')
    return [amat, bmat, info]

def print_mat(m, ur, dr, lc, rc):
    for i in xrange(ur, dr):
        for j in xrange(lc, rc):
            if m[i,j] != 0:
                print "{:5.2f}".format(m[i,j]), 
            else:
                print " "*5,
        print ""

def hist_x_b():
    bmat = read_mat('mat_init/bmat_0.mtx')
    xmat = read_mat('mat_05_05/xmat.mtx')
    cmat = (xmat - bmat*0.5)*2.0

    import matplotlib.pyplot as plt
    import numpy as np
    
    start = min(min(bmat), min(xmat), min(cmat))
    stop = max(max(bmat), max(xmat), max(cmat))
    
    h = plt.hist(bmat, bins=np.logspace(math.log10(start), math.log10(stop), 50), alpha=0.5)
    h = plt.hist(xmat, bins=np.logspace(math.log10(start), math.log10(stop), 50), alpha=0.5)
    h = plt.hist(cmat, bins=np.logspace(math.log10(start), math.log10(stop), 50), alpha=0.5)
    
    plt.xscale('log')
    
    plt.show()
