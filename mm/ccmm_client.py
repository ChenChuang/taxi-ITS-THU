import sys
import time

import urllib2
import urllib

import ccgraph as cg
import cctrack as ct
import ccpath as cp
import ccdb as cdb

import alg_st as alg

if __name__ == "__main__":
    if len(sys.argv) != 2:
        exit(-1)
    ICORE = int(sys.argv[1])

server = "http://219.223.168.143:9090"
read_url = server + "/read?name=core" + str(ICORE)
write_url = server + "/write?name=core" + str(ICORE)
map_url = server + "/map"


def read_map():
    fields = ['id', 'source', 'target', 'km', 'kmh', 'reverse_cost', 'x1', 'y1', 'x2', 'y2', 'geom']
    data = urllib2.urlopen(map_url).read()
    for line in data.strip().split('\n'):
        m = {}
        for i, x in enumerate(line.strip().split(', ')):
            m[fields[i]] = x
        yield m

gw = cg.new_gw(source = read_map())
trd = cdb.new_track_reader_for_purpose(purpose="mm")

task = ""

def urlpost(url, data):
    d = urllib.urlencode(data)
    req = urllib2.Request(url, d)
    req.add_header('Content-Type', "application/x-www-form-urlencoded")
    resp = urllib2.urlopen(req).read()
    return resp

def new_track_from_http(str_tid, str_cuid, geom, desc):
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
            tt = time.strptime(s, "%Y-%m-%d %H:%M:%S")
            hh = 0
            ss = 0
            if i == 0 or lonlats[i] != lonlats[i-1]:
                rds.append( {'time':tt, 'head':hh, 'speed':ss, 'gps_lonlat':lonlats[i]} )
            i = i + 1
        rds = tuple(rds)
        return ct.Track(tid, cuid, rds, desc)
    except Exception,e:
        print e
        return None
    return None

def next_track():
    global task
    if task == "":
        while True:
            try:
                task = urllib2.urlopen(read_url, timeout=2).read()
                break
            except Exception, e:
                pass
            time.sleep(5)
    if task == "done":
        return None, True
    task_id, tid, cuid, geom, desc, oorc = task.strip().split('\n')
    track = new_track_from_http(tid, cuid, geom, desc)
    task = ""
    return task_id, tid, track, False

def upload_path(task_id, tid, path):
    global task
    try:
        wids = path.as_ways()
        geom = path.as_geom()
    except Exception, e:
        path = None
    if path is None:
        data = {'id': task_id, 'res': "\n".join([str(tid), "error"])}
    else:
        data = {'id': task_id, 'res': "\n".join([str(path.tid), wids, geom])}
    while True:
        try:
            task = urlpost(write_url, data)
            break
        except Exception, e:
            pass
        time.sleep(5)

def match(track):
    print "Matching..",
    path = alg.match(gw, track)

    if path is not None:
        print "end   ",    
        path.summary()
    print ""
    return path

def mm():
    alg.prepare(gw)
    while True:
        task_id, tid, track, done = next_track()
        if done:
            break
        if track is None:
            upload_path(task_id, tid, None)
            continue 
        print 'core ' + str(ICORE) + ':' + "track",str(task_id).ljust(10)," ",
        try:
            path = match(track)
            upload_path(task_id, tid, path)
        except (KeyboardInterrupt, SystemExit):
            break
        except Exception, e:
            print e

if __name__ == "__main__":
    mm()

