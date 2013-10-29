select 
avg(bn) as avg_bn,
avg(st) as avg_st,
avg(iv) as avg_iv,
avg(ut) as avg_ut,
avg(uti) as avg_uti 
from taxi_paths_compare, taxi_tracks_attr 
where taxi_paths_compare.tid = taxi_tracks_attr.tid 
and bn*st*iv*ut*uti > 0 
and length/rds_num > 2 
and length/rds_num < 2000000
and taxi_tracks_attr.tid < 1000;
