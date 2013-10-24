import psycopg2
import sys
import time

from common.data_parser import *
import common.lib as lib
import common.config

from_cuid = 1
to_cuid = 200

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
                self.descs.append({"t":time_tx,"h":head_tx,"s":speed_tx,"o":occupied_tx})
                self.coordnum = self.coordnum + 1

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
                self.tracknum = self.tracknum + 1

            self.coords = list()
            self.descs = list()

        self.pre_occupied = attrs['occupied']

    def insert_track(self):
        cursor = self.conn.cursor()

        coords_sql = "LINESTRING("
        coord = self.coords[0]
        coords_sql = coords_sql + str(coord[0]) + " " + str(coord[1])
        length = 0
        for i in range(1, len(self.coords)):
            coord = self.coords[i]
            coords_sql = coords_sql + "," + str(coord[0]) + " " + str(coord[1])
            length += lib.lonlats2km(self.coords[i-1], self.coords[i])
        coords_sql = coords_sql + ")"

        descs_sql = ""
        for desc in self.descs:
            descs_sql = descs_sql + desc["t"] + " " + desc["h"] + " " + desc["s"] + " " + desc["o"] + ","
        descs_sql = descs_sql + ""

        sql = "insert into taxi_tracks(cuid, track_geom, track_desc) values(%s,%s,%s) returning id;"
        cursor.execute(sql, (self.cuid, coords_sql, descs_sql))
        tid = cursor.fetchone()[0]
        self.conn.commit()
        

        rds_num = len(self.coords)
        sql = "insert into taxi_tracks_attr(tid, rds_num, length) values(%s,%s,%s);"
        cursor.execute(sql, (str(tid), str(rds_num), str(length)))
        self.conn.commit()

tracks2postgres = Tracks2Postgres()

read_by_cuid(from_cuid,to_cuid,tracks2postgres)

print "num of coords =",tracks2postgres.coordnum
print "num of tracks =",tracks2postgres.tracknum
print "num of one-coord tracks =",tracks2postgres.onecoord_tracknum
