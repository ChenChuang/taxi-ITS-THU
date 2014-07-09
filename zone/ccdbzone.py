import psycopg2 as pg
import psycopg2.extras as pgextras

import sys, os
mmpath = os.path.join(os.getcwd(), '..', 'mm')
sys.path.insert(0, mmpath)
import ccdb as cdb
del sys.path[0]

class WayPickDropDB(cdb.DB):
    def __init__(self, tbname="ways_pickdrop"):
        super(WayPickDropDB, self).__init__(database='beijing_mm_po_car')
        self.tbname = tbname

    def read_picks_drops(self):
        sql = "select pickup, dropoff from " + self.tbname + " order by wid"
        try:
            self.cursor.execute(sql)
            rows = self.cursor.fetchall()
        except Exception, e:
            print e
            return [None, None]
        picks = [row[0] for row in rows]
        drops = [row[1] for row in rows]
        return [picks, drops]

    def update_picks_drops(self, picks, drops):
        for i, [pick, drop] in enumerate(zip(picks, drops)):
            wid = i+1
            print 'update wid =',wid
            sql = "update " + self.tbname + " set (pickup, dropoff) = (%s, %s) where wid = %s"
            self.cursor.execute(sql, (pick, drop, wid))
        self.conn.commit()

class WayZoneDB(cdb.DB):
    def __init__(self, tbname="ways_zone"):
        super(WayZoneDB, self).__init__(database='beijing_mm_po_car')
        self.tbname = tbname

    def update_zone(self, lbs):
        for i, lb in enumerate(lbs):
            wid = i+1
            # print 'update wid =',wid
            sql = "update " + self.tbname + " set label = (%s) where wid = %s"
            self.cursor.execute(sql, (lb, wid))
        self.conn.commit()

class WayClustDB(cdb.DB):
    def __init__(self, tbname="ways_clust_som"):
        super(WayClustDB, self).__init__(database='beijing_mm_po_car')
        self.tbname = tbname

    def read_clust(self):
        sql = "select clust from " + self.tbname + " order by wid"
        try:
            self.cursor.execute(sql)
            rows = self.cursor.fetchall()
        except Exception, e:
            print e
            return None
        clusts = [row[0] for row in rows]
        return clusts

class WayCatoDB(cdb.DB):
    def __init__(self, tbname="ways_clust_som_3"):
        super(WayCatoDB, self).__init__(database='beijing_mm_po_car')
        self.tbname = tbname

    def read_cato(self):
        sql = "select cat from " + self.tbname + " order by wid"
        try:
            self.cursor.execute(sql)
            rows = self.cursor.fetchall()
        except Exception, e:
            print e
            return None
        clusts = [row[0] for row in rows]
        return clusts


