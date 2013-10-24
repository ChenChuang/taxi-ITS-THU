import ccdb as cdb

from_cuid = 1;
to_cuid = 1000;

def insert_tracks_attr():
    trd = cdb.new_track_reader()
    if trd is None:
        return

    tawd = cdb.new_track_attr_writer()
    track = trd.fetch_one()
    while track is not None:
        if track.cuid >= from_cuid and track.cuid <= to_cuid:
            print trd.fetched_num, track.tid
            tawd.insert(track)
        track = trd.fetch_one()
    
    del trd
    del tawd

insert_tracks_attr()
