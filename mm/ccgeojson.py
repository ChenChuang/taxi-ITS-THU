import json as js
import re
import psycopg2 as pg
import psycopg2.extras as pgextras
import sys
import time
import cctrack as ct
import ccgraph as cg
import ccdb as cdb

def check_method(method):
    if method in ['bn','st','iv','ut','uti']:
        return True
    return False


def export_all_for_method(method):
    if not check_method(method):
        print 'no method named',method
        return

    pt2j = PT2Geojson(method)
    pt2j.init_path_track_reader()
    print 'exporting paths by',method,'to geojson ...',
    pt2j.export_paths_tracks()
    print 'end'

def new_pt2geojson(method):
    if not check_method(method):
        print 'no method named',method
        return None
    return PT2Geojson(method)

class PT2Geojson:
    
    def __init__(self, method):
        self.output_dir_p = "/home/chenchuang/beijing_taxi_proc_output/geojson_paths/"
        self.output_prefix_p = "geojson_p_"
        self.output_dir_t = "/home/chenchuang/beijing_taxi_proc_output/geojson_tracks/"
        self.output_prefix_t = "geojson_t_"
        self.method = method
           
    def init_path_track_reader():
        self.prd = cdb.new_path_reader_for_method(method = self.method, offset = 0)
        self.trd = cdb.new_track_reader(offset = 0)

    def export_paths_tracks(self):
        while True:
            path = self.prd.fetch_one()
            if path is None:
                break
            self.write_p_geojson(path)
            self.export_track_by_id(path.tid)
        return True

    def write_p_geojson(self, path):
        jdict = {}
        jdict["type"] = "FeatureCollection"
        geo = {}
        geo["type"] = "LineString"
        lonlats = path.get_lonlats()
        if lonlats is None or len(lonlats) == 0:
            return False
        
        geo["coordinates"] = lonlats
        features = [{"geometry":geo, "properties":{"tid":path.tid}}]
        
        jdict["features"] = features
        
        filename = self.output_dir_p + self.output_prefix_p + self.method + "_" + str(path.tid) + ".json"
        with open(filename, "w") as f:
            f.write(js.dumps(jdict))

        return True

    def export_track_by_id(self, tid):
        track = self.trd.fetch_by_id(tid)
        if track == None:
            return False
        if self.write_t_geojson(track):
            return True
        else:
            return False

    def write_t_geojson(self, track):
        jdict = {}
        jdict["type"] = "FeatureCollection"
        geo = {}
        geo["type"] = "LineString"
        lonlats = []
        descs = []
        for rd in track.rds:
            lonlats.append(rd['gps_lonlat'])
            time_tx = time.strftime("%Y-%m-%dT%H:%M:%SZ", rd['time'])
            head_tx = str(rd['head'])
            speed_tx = str(rd['speed'])
            occupied_tx = '1'
            descs.append({'t':time_tx, 'h':head_tx, 's':speed_tx, 'o':occupied_tx})
        geo["coordinates"] = lonlats
        features = [{"geometry":geo, "properties":{"desc":descs}}]

        jdict["features"] = features

        filename = self.output_dir_t + self.output_prefix_t + str(track.tid) + ".json"
        with open(filename, "w") as f:
            f.write(js.dumps(jdict))

        return True


