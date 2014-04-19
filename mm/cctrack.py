import sys
import time
import re
import random
import math
import psycopg2 as pg
import psycopg2.extras as pgextras
import ccgraph as cg
from ccdef import *

def new_track_from_db(str_tid, str_cuid, geom, desc):
    try:
        tid = int(str_tid)
        cuid = int(str_cuid)

        lonlats = cg.geom2lonlats(geom)
        if not len(lonlats) > 0:
            return None

        rds = []
        i = 0
        for s in desc.split(','):
            if s == '':
                continue
            thso = s.split(' ')
            tt = time.strptime(thso[0], "%Y-%m-%dT%H:%M:%SZ")
            hh = int(thso[1])
            ss = int(thso[2])/1000.0*60.0
            if i == 0 or lonlats[i] != lonlats[i-1]:
                rds.append( {'time':tt, 'head':hh, 'speed':ss, 'gps_lonlat':lonlats[i]} )
            i = i + 1
        rds = tuple(rds)
        return Track(tid, cuid, rds, desc)

    except Exception,e:
        print e
        return None

    return None


class Track(object):
    def __init__(self, tid, cuid, rds, desc=None):
        self.tid = tid
        self.cuid = cuid
        self.rds = rds
        self.desc = desc
    
    def length(self):
        l = 0
        pre_lonlat = self.rds[0]['gps_lonlat']
        for i in range(1,len(self.rds)):
            cur_lonlat = self.rds[i]['gps_lonlat']
            d = cg.lonlats2km(pre_lonlat, cur_lonlat)
            l = l + d
            pre_lonlat = cur_lonlat
        return l

    def max_d(self):
        max_d = 0
        pre_lonlat = self.rds[0]['gps_lonlat']
        for i in range(1,len(self.rds)):
            cur_lonlat = self.rds[i]['gps_lonlat']
            d = cg.lonlats2km(pre_lonlat, cur_lonlat)
            print d
            if d > max_d:
                max_d = d
            pre_lonlat = cur_lonlat
        return max_d

    def summary(self):
        print "tid:",self.tid,"cuid:",self.cuid,"records number:",len(self.rds)

    def aggre_records(self):
        ards = []
        
        tmp_rds = [self.rds[0]]
        cent = self.rds[0]['gps_lonlat']

        def ards_add():
            tt = tmp_rds[len(tmp_rds) / 2]['time']
            hh = tmp_rds[len(tmp_rds) / 2]['head']
            ss = tmp_rds[len(tmp_rds) / 2]['speed']

            avg_rd = {'time':tt, 'head':hh, 'speed':ss, 'gps_lonlat':cent}
            ards.append(avg_rd)

        for i,rd in enumerate(self.rds[1:]):
            d = cg.lonlats2km(rd['gps_lonlat'], cent)
            if d < 0.01:
                tmp_rds.append(rd)
                cent = ((cent[0] + rd['gps_lonlat'][0]) / 2, (cent[1] + rd['gps_lonlat'][1]) / 2)
            else:
                ards_add()               
                tmp_rds = [rd]
                cent = rd['gps_lonlat']
       
        ards_add()

        return ards

    def rect(self):
        min_lon = INF
        min_lat = INF
        max_lon = -INF
        max_lat = -INF
        for rd in self.rds:
            (lon, lat) = rd['gps_lonlat']
            min_lon = min(min_lon, lon)
            max_lon = max(max_lon, lon)
            min_lat = min(min_lat, lat)
            max_lat = max(max_lat, lat)
        return (min_lon, min_lat, max_lon, max_lat)

    def add_noise(self, sigma=0.02):
        for i,rd in enumerate(self.rds):
            lonlat = rd['gps_lonlat']
            angle = random.uniform(0,2 * math.pi)
            r = abs(random.gauss(0,sigma))
            dlat = cg.km2latgap(r * math.sin(angle))
            dlon = cg.km2longap(r * math.cos(angle), lonlat[1])
            self.rds[i]['gps_lonlat'] = (lonlat[0] + dlon, lonlat[1] + dlat)

    def get_geom(self):
        lonlats = [rd['gps_lonlat'] for rd in self.rds]
        return cg.lonlats2geom(lonlats)
    
    def get_desc(self):
        return self.desc

    def sample(self, interval, s=0):
        if s < 0:
            raise Exception('s < 0')
        
        tmp_desc = self.desc.split(',')
        desc = tmp_desc[s::interval]
        rds = list(self.rds[s::interval])
        if s > 0:
            desc = [tmp_desc[0]] + desc
            rds = [self.rds[0]] + rds
        
        if len(self.rds) - 1 % interval != 0:
            rds.append(self.rds[-1])
            desc.append(tmp_desc[-1])

        self.rds = rds
        self.desc = ",".join(desc)

    def sample_head_tail(self):
        rds = [self.rds[0], self.rds[-1]]
        
        tmp_desc = self.desc.split(',')
        desc = [tmp_desc[0], tmp_desc[-1]]
        
        self.rds = rds
        self.desc = ",".join(desc)


