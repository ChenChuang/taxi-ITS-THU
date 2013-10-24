import psycopg2
import sys
import time
import datetime

from common.data_parser import *
import common.lib as lib
import common.config as config

from_cuid = 241
to_cuid = 4000

class Tracks2Postgres:
    
    def __init__(self):
        self.conn = psycopg2.connect(database='beijing_taxi',user='postgres',password='123456')

    def parser_start_callback(self):
        self.coordnum = 0
        self.tracknum = 0
        self.onecoord_tracknum = 0

    def parser_end_callback(self):
        pass

    def cuid_start_callback(self, cuid):
        self.cuid = cuid
        self.coords = list()
        self.descs = list()

        self.pre_occupied = -1

        self.tracknum_cuid = 0

    def cuid_end_callback(self, cuid):        
        pass

    def file_start_callback(self, infn):
        pass

    def file_end_callback(self, infn):
        pass    

    def line_callback(self, line):
        attrs = lib.parse_line(line)
        
        time_tx = time.strftime("%Y-%m-%dT%H:%M:%SZ", attrs['time'])
        head_tx = str(attrs['head'])
        speed_tx = str(attrs['speed'])
        occupied_tx = str(attrs['occupied'])

        if attrs['occupied'] == 1:
            coord = [attrs['lon'], attrs['lat']]
            if len(self.coords) == 0 or coord != self.coords[-1]:
                self.coords.append(coord)
                self.descs.append([time_tx, head_tx, speed_tx, occupied_tx])
                self.coordnum += 1

        if self.pre_occupied == -1:
            pass

        elif self.pre_occupied == 0 and attrs['occupied'] == 1:
            pass

        elif self.pre_occupied == 1 and attrs['occupied'] == 0:
            track_needed = False

            if len(self.coords) > 1:
                track_needed = True
            elif len(self.coords) == 1:
                self.onecoord_tracknum = self.onecoord_tracknum + 1

            if track_needed:
                self.insert_track()
                self.tracknum += 1
                self.tracknum_cuid += 1
                if self.tracknum_cuid % 100 == 0:
                    print self.tracknum_cuid,

            self.coords = list()
            self.descs = list()

        self.pre_occupied = attrs['occupied']

    def insert_track(self):
        cursor = self.conn.cursor()

        coords_sql_ls = [" ".join([str(coord[0]),str(coord[1])]) for coord in self.coords]
        coords_sql = "LINESTRING(" + ",".join(coords_sql_ls) + ")"
        
        length = 0
        for i in xrange(1, len(self.coords)):
            length += lib.lonlats2km(self.coords[i-1], self.coords[i])

        descs_sql_ls = [" ".join(desc) for desc in self.descs] 
        descs_sql = ",".join(descs_sql_ls)

        sql = "insert into taxi_tracks(cuid, track_geom, track_desc) values(%s,%s,%s) returning id;"
        cursor.execute(sql, (self.cuid, coords_sql, descs_sql))
        tid = cursor.fetchone()[0]
        self.conn.commit()
        

        rds_num = len(self.coords)
        sql = "insert into taxi_tracks_attr(tid, rds_num, length) values(%s,%s,%s);"
        cursor.execute(sql, (str(tid), str(rds_num), str(length)))
        self.conn.commit()

def work():
    print "".center(70, '-')
    print "CUID:",from_cuid,"~",to_cuid
    
    tracks2postgres = Tracks2Postgres()

    start_at = datetime.datetime.now()
    print (' start at ' + str(start_at) + ' ').center(70, '-')

    read_by_cuid(from_cuid,to_cuid,tracks2postgres)

    end_at = datetime.datetime.now()
    print (' end at ' + str(end_at) + ' ').center(70, '-'),'elapsed time',str(end_at - start_at)

    print "".center(70, '-')
    print "CUID:",from_cuid,"~",to_cuid
    print "num of coords =",tracks2postgres.coordnum
    print "num of tracks =",tracks2postgres.tracknum
    print "num of one-coord tracks =",tracks2postgres.onecoord_tracknum
    print "".center(70, '-')

if __name__ == "__main__":
    work()



