import ccdb as cdb
import ccgraph as cg

def insert_paths_attr():
    gw = cg.new_gw()

    prd = cdb.new_path_reader_for_method(method='bn', gw=gw, limit=10000, offset=0)
    if prd is None:
        return
    trd = cdb.new_track_reader()
    
    pawd = cdb.new_path_attr_writer('taxi_paths_bn_attr')

    path = prd.fetch_one()    
    while path is not None:
        print prd.fetched_num, path.tid
        track = trd.fetch_by_id(path.tid)
        pawd.insert(path, track)
        path = prd.fetch_one()

    del prd
    del pawd

insert_paths_attr()
