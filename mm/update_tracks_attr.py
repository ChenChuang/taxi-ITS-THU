import ccdb as cdb

from_tid = 1000200;
to_tid = 2638410;
# max(tid) == 2638410


def insert_tracks_attr():
    trd = cdb.new_track_reader()
    if trd is None:
        return

    tawd = cdb.new_track_attr_writer()
    
    for tid in xrange(from_tid, to_tid+1):
        track = trd.fetch_by_id(tid)
        if track.tid % 100 == 0:
            print track.tid
        tawd.insert_update(track)
    
    del trd
    del tawd

if __name__ == "__main__":
    insert_tracks_attr()
