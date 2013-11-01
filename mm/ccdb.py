import psycopg2 as pg
import psycopg2.extras as pgextras
import ccpath as cp
import cctrack as ct
import ccgraph as cg

def tbname_of_method(method):
    if method in ['bn','st','iv','ut','uti']:
        return 'taxi_paths_' + method
    else:
        return None

def tbname_of_purpose(purpose):
    if purpose in ['dp','mm']:
        return 'taxi_tracks_' + purpose
    else:
        return None

def tbname_by_sample(interval):
    return 'taxi_tracks_sample_' + str(interval)

def new_path_reader(gw=None, tbname="taxi_paths", limit=10000, offset=0):
    return PathReader(tbname=tbname, gw=gw, limit=limit, offset=offset)

def new_path_writer(tbname="taxi_paths"):
    return PathWriter(tbname=tbname)

def new_path_reader_for_method(method, gw=None, limit=10, offset=0):
    tbname = tbname_of_method(method)
    if tbname is not None:
        return PathReader(tbname=tbname, gw=gw, limit=limit, offset=offset)
    else:
        return None

def new_path_writer_for_method(method):
    tbname = tbname_of_method(method)
    if tbname is not None:
        return PathWriter(tbname=tbname)
    else:
        return None

def new_path_attr_writer(tbname="taxi_paths_attr"):
        return PathAttrWriter(tbname=tbname)

def new_path_attr_writer_for_method(method):
    tbname = tbname_of_method(method)
    if tbname is not None:
        tbname = tbname + "_attr"
        return new_path_attr_writer(tbname)

def new_track_reader(limit=10000, offset=0):
    return TrackReader(tbname="taxi_tracks", limit=limit, offset=offset)

def new_track_reader_for_purpose(purpose, limit=10000, offset=0):
    tbname = tbname_of_purpose(purpose)
    if tbname is not None:
        return TrackReader(tbname=tbname, limit=limit, offset=offset)
    else:
        return None

def new_track_writer(tbname):
    return TrackWriter(tbname=tbname)

def new_track_attr_writer(tbname="taxi_tracks_attr"):
    return TrackAttrWriter(tbname=tbname)


def new_track_reader_by_sample(interval):
    tbname = tbname_by_sample(interval)
    return TrackReader(tbname=tbname, limit=10000, offset=0)

def new_track_writer_by_sample(interval):
    tbname = tbname_by_sample(interval)
    return TrackWriter(tbname=tbname)


def new_way_attr_db(tbname="ways_ut_attr"):
    return WayAttrDB(tbname=tbname)

def new_way_db(tbname="ways"):
    return WayDB(tbname=tbname)

def new_tid_dp_db(tbname):
    return TidDpDB(tbname=tbname)

def copy_valid_path(gw, tid, method):
    pwd = new_path_writer()
    pawd = new_path_attr_writer()
    prd = new_path_reader_for_method(method=method, gw=gw)
    path = prd.fetch_path_by_tid(tid)
    if path is not None:
        pwd.insert(path)
        pawd.insert(path)


class DB(object):
    def __init__(self, database='beijing_taxi'):
        self.database = database
        self.user = 'postgres'
        self.password = '123456'
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
                    password = self.password)
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


class WayDB(DB):
    def __init__(self, tbname='ways'):
        super(WayDB, self).__init__(database='beijing_mm_po_car')
        self.tbname = tbname

    def reverse_way_by_id(self, wid):
        sql = "select id, source, target, x1, y1, x2, y2, st_astext(geom_way) as geom from " + self.tbname + " where id = %s"
        self.cursor.execute(sql, (wid,))
        row = self.cursor.fetchone()
        t = int(row['source'])
        s = int(row['target'])
        x2 = float(row['x1'])
        y2 = float(row['y1'])
        x1 = float(row['x2'])
        y1 = float(row['y2'])
        geom = row['geom']
        lonlats = list(cg.geom2lonlats(geom))
        lonlats.reverse()
        geom = cg.lonlats2geom(lonlats)
       
        print geom
        sql = "update " + self.tbname + " set (source, target, x1, y1, x2, y2, geom_way) = (%s,%s,%s,%s,%s,%s,st_geomfromtext(%s,%s)) where id = %s"
        self.cursor.execute(sql, (s,t,x1,y1,x2,y2,geom,4326,wid))
        self.conn.commit()

    def read_attr(self, attrname):
        sql = "select " + attrname + " from " + self.tbname + " order by id"
        try:
            self.cursor.execute(sql)
            rows = self.cursor.fetchall()
        except Exception, e:
            print e
            return None
        attrs = [row[0] for row in rows]
        return attrs



class WayAttrDB(DB):
    def __init__(self, tbname):
        super(WayAttrDB, self).__init__(database='beijing_mm_po_car')
        self.tbname = tbname

    def init_tb(self, min_wid=1, max_wid=49122, attrs_values={}):
        if len(attrs_values) == 0:
            return False
        attrs = attrs_values.keys()
        values = [attrs_values[attr] for attr in attrs]
        for wid in xrange(min_wid, max_wid+1):
            sql = "".join(["insert into ", self.tbname, " (", "%s, "*len(attrs), "wid) ", "values("])
            sql = sql % tuple(attrs)
            sql = sql + "%s, "*len(values) + "%s)"
            try:
                self.cursor.execute(sql, tuple(values + [wid]))
            except Exception, e:
                print e
                print "clear %s before initialization" % self.tbname
                return False
        self.conn.commit()
        return True

    def update_attr(self, attrname, attrs):
        for wid, attr in enumerate(attrs):
            wid += 1
            sql = "update " + self.tbname + " set (%s) = ($v) where wid = $v"
            sql = sql % (attrname,)
            sql = sql.replace("$v","%s")
            try:
                self.cursor.execute(sql, (attr,wid))
            except Exception, e:
                print e
                return False
        self.conn.commit()
        return True

    def read_attr(self, attrname):
        sql = "select " + attrname + " from " + self.tbname + " order by wid"
        try:
            self.cursor.execute(sql)
            rows = self.cursor.fetchall()
        except Exception, e:
            print e
            return None
        attrs = [row[0] for row in rows]
        return attrs



class PathWriter(DB):
    def __init__(self, tbname):
        super(PathWriter, self).__init__()
        self.tbname = tbname

    def insert_update(self, path):
        sql = "select count(*) as num from " + self.tbname + " where tid = %s"
        self.cursor.execute(sql, (str(path.tid),))
        row = self.cursor.fetchone()
        try:
            if int(row['num']) > 0:
                sql = "update " + self.tbname + " set (tid, way_ids, path_geom) = (%s,%s,%s) where tid = %s"
                self.cursor.execute(sql, (str(path.tid), path.as_ways(), path.as_geom(), str(path.tid)))
            else:
                sql = "insert into " + self.tbname + "(tid, way_ids, path_geom) values (%s,%s,%s)"
                self.cursor.execute(sql, (str(path.tid), path.as_ways(), path.as_geom()))
            self.conn.commit()
        except:
            pass

    def insert(self, path):
        sql = "insert into " + self.tbname + "(tid, way_ids, path_geom) values (%s,%s,%s)"
        try:
            self.cursor.execute(sql, (str(path.tid), path.as_ways(), path.as_geom()))
            self.conn.commit()
        except:
            pass

class PathAttrWriter(DB):
    def __init__(self, tbname):
        super(PathAttrWriter, self).__init__()
        self.tbname = tbname
    
    '''depreacted'''
    def insert_update(self, path, track):
        sql = "select count(*) as num from " + self.tbname + " where tid = %s"
        self.cursor.execute(sql, (str(path.tid),))
        row = self.cursor.fetchone()
        try:
            if int(row['num']) > 0:
                sql = "update " + self.tbname + " set (length, conf) = (%s,%s) where tid = %s"
                self.cursor.execute(sql, (path.length(), path.confidence(track), path.tid))
            else:
                sql = "insert into " + self.tbname + "(tid, length, conf) values (%s,%s,%s)"
                self.cursor.execute(sql, (path.tid, path.length(), path.confidence(track)))
            self.conn.commit()
        except:
            pass

    def insert(self, path, track):
        sql = "insert into " + self.tbname + "(tid, length, conf) values (%s,%s,%s)"
        try:
            self.cursor.execute(sql, (path.tid, path.length(), path.confidence(track)))
            while self.conn.isexecuting():
                pass
            self.conn.commit()
        except:
            pass



class PathReader(DB):
    def __init__(self, tbname, gw = None, limit = 10, offset = 0):
        super(PathReader, self).__init__()

        self.limit = limit
        self.offset = offset
        self.queried_num = 0
        self.fetched_num = 0

        self.tbname = tbname
        self.gw = gw

        self.query_more()

    def query_more(self):
        sql = "select tid, way_ids, st_astext(path_geom) as geom from " + self.tbname + " limit %s offset %s"
        self.cursor.execute(sql, (str(self.limit), str(self.offset)))
        self.offset = self.offset + self.limit
        self.queried_num = self.queried_num + self.limit

    def fetch_one(self):
        row = self.cursor.fetchone()
        if row == None:
            self.query_more()
            row = self.cursor.fetchone()
        if row == None:
            return None

        self.fetched_num = self.fetched_num + 1
        return cp.new_path_from_db(self.gw, row['tid'], row['way_ids'], row['geom'])

    def fetch_path_by_tid(self, tid):
        tconn = None
        tmp_cursor = None
        try:
            tconn = pg.connect(
                    database = self.database,
                    user = self.user,
                    password = self.password)
            tmp_cursor = tconn.cursor(cursor_factory = pgextras.DictCursor)
            sql = "select tid, way_ids, st_astext(path_geom) as geom from " + self.tbname + " where tid = %s"
            tmp_cursor.execute(sql, (tid,))
            row = tmp_cursor.fetchone()
            if row == None:
                return None
            else:
                return cp.new_path_from_db(self.gw, row['tid'], row['way_ids'], row['geom'])
        except Exception, e:
            print e
            return None



class TrackReader(DB):
    def __init__(self, tbname="taxi_tracks", limit = 10000, offset = 0):
        super(TrackReader, self).__init__()
        self.tbname = tbname

        self.limit = limit
        self.offset = offset
        self.queried_num = 0
        self.fetched_num = 0

        self.query_more()

    def query_more(self):
        sql = "select id, cuid, st_astext(track_geom) as geom, track_desc from " + self.tbname + " limit %s offset %s"
        self.cursor.execute(sql, (str(self.limit), str(self.offset)))
        self.offset = self.offset + self.limit
        self.queried_num = self.queried_num + self.limit

    def fetch_one(self):
        row = self.cursor.fetchone()
        if row == None:
            self.query_more()
            row = self.cursor.fetchone()
        if row == None:
            return None

        self.fetched_num = self.fetched_num + 1
        return ct.new_track_from_db(row['id'], row['cuid'], row['geom'], row['track_desc'])

    def fetch_by_id(self, tid):
        tconn = None
        tmp_cursor = None
        try:
            tconn = pg.connect(
                    database = self.database,
                    user = self.user,
                    password = self.password)
            tmp_cursor = tconn.cursor(cursor_factory = pgextras.DictCursor)
            sql = "select id, cuid, st_astext(track_geom) as geom, track_desc from " + self.tbname + " where id = %s"
            tmp_cursor.execute(sql, (str(tid),))
            row = tmp_cursor.fetchone()
            if row == None:
                return None
            else:
                return ct.new_track_from_db(row['id'], row['cuid'], row['geom'], row['track_desc'])
        except:
            return None

class TrackWriter(DB):
    def __init__(self, tbname):
        super(TrackWriter, self).__init__()
        self.tbname = tbname

    def insert_geom(self, track):
        sql = "insert into " + self.tbname + "(tid, track_geom) values (%s, %s)"
        try:
            self.cursor.execute(sql, (track.tid, track.get_geom()))
            self.conn.commit()
        except:
            pass
    
    def insert(self, track):
        sql = "insert into " + self.tbname + "(tid, cuid, track_geom, track_desc) values (%s, %s, %s, %s)"
        try:
            self.cursor.execute(sql, (track.tid, track.cuid, track.get_geom(), track.get_desc()))
            self.conn.commit()
        except:
            pass
    



class TrackAttrWriter(DB):
    def __init__(self, tbname):
        super(TrackAttrWriter, self).__init__()
        self.tbname = tbname

    def insert_update(self, track):
        sql = "select count(*) as num from " + self.tbname + " where tid = %s"
        self.cursor.execute(sql, (str(track.tid),))
        row = self.cursor.fetchone()
        try:
            if int(row['num']) > 0:
                sql = "update " + self.tbname + " set (length, rds_num) = (%s,%s) where tid = %s"
                self.cursor.execute(sql, (str(track.length()), str(len(track.rds)), str(track.tid)))
            else:
                sql = "insert into " + self.tbname + "(tid, length, rds_num) values (%s,%s,%s)"
                self.cursor.execute(sql, (str(track.tid), str(track.length()), str(len(track.rds))))
            self.conn.commit()
        except:
            pass

    def insert(self, track):
        sql = "insert into " + self.tbname + "(tid, length, rds_num) values (%s,%s,%s)"
        try:
            self.cursor.execute(sql, (str(track.tid), str(track.length()), str(len(track.rds))))
            self.conn.commit()
        except:
            pass

class TidDpDB(DB):
    def __init__(self, tbname):
        super(TidDpDB, self).__init__()
        self.tbname = tbname

    def insert(self, tid):
        sql = "insert into " + self.tbname + "(tid) values (%s)"
        try:
            self.cursor.execute(sql, (tid,))
            self.conn.commit()
        except:
            pass






    

