import datetime
import time
import os
import math

def dates_to_tbnames(fromdate, todate):
    tbnames = []
    d = datetime.date(*fromdate)
    to_d = datetime.date(*todate)
    while True:
        tbnames.append("tb_" + str(d).replace('-',''))
        d += datetime.date.resolution
        if d > to_d:
            break
    return tbnames

def times_to_utcs(fromdate, todate, fromtime, totime):
    utcs = []
    t = datetime.datetime(*(fromdate + fromtime))
    to_t = datetime.datetime(*(todate + totime))
    d = datetime.date(*fromdate)
    to_d = datetime.date(*todate)
    while True:
        utcs.append((
            time.mktime(t.utctimetuple()), 
            time.mktime(to_t.utctimetuple())))   #mktime always convert local time to utc seconds
        d += datetime.date.resolution
        if d > to_d:
            break
    return utcs

def new_output_dir():
    output_dir = raw_input('Query results will be loaded in this new directory: ')
    if os.path.isdir(output_dir):
        print output_dir,"has exist"
        return ""
    os.mkdir(output_dir)    
    os.chdir(output_dir)
    os.mkdir('data')
    os.chdir('data')
    return os.getcwd()

def new_output_dir_as(output_dir):
    if os.path.isdir(output_dir):
        print output_dir,"has exist"
        return ""
    os.mkdir(output_dir)
    os.mkdir(output_dir + 'data/')
    return output_dir + 'data/'
    
def sort_filenames_by_ints(strs):
    return sorted(strs, key = lambda s: int(os.path.splitext(s)[0]))

def is_record_in_area(line, min_lon, max_lon, min_lat, max_lat):
    s = line.split(', ')
    return is_coord_in_area([int(s[2]), int(s[3])], min_lon, max_lon, min_lat, max_lat)

def is_coord_in_area(coord, min_lon, max_lon, min_lat, max_lat):
    return min_lon <= coord[0] <= max_lon and min_lat <= coord[1] <= max_lat

def parse_line(line):
    s = line.split(', ')
    attrs = {}
    attrs['cuid'] = s[0]
    attrs['time'] = time.localtime(long(s[1]))
    attrs['lat'] = float(s[2]) / 100000
    attrs['lon'] = float(s[3]) / 100000
    attrs['head'] = int(s[4])
    attrs['speed'] = int(s[5])
    attrs['occupied'] = int(s[6])
    return attrs
    
def lonlats2km(s_lonlat, t_lonlat):
    dlat = 111.0 * abs(s_lonlat[1] - t_lonlat[1])
    dlon = 111.0 * abs(math.cos(math.radians((s_lonlat[1] + t_lonlat[1]) / 2))) * abs(s_lonlat[0] - t_lonlat[0])
    return math.sqrt(dlat**2 + dlon**2)

