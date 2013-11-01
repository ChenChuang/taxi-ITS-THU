select
count(*) as track_num,
avg(bn) as avg_bn,
avg(st) as avg_st,
avg(iv) as avg_iv,
avg(ut) as avg_ut,
avg(uti) as avg_uti 
from taxi_paths_compare, taxi_tracks_attr 
where taxi_paths_compare.tid = taxi_tracks_attr.tid 
and bn*st*iv*ut*uti > 0 
and length/rds_num >= 2.0
and length/rds_num < 200000000.0
and taxi_tracks_attr.tid <= 1000;

select 
count(taxi_tracks_attr.tid) as track_num 
from taxi_tracks_mm,taxi_tracks_attr 
where taxi_tracks_mm.id = taxi_tracks_attr.tid 
and length/rds_num >= 0.2 and length/rds_num < 0.4 and taxi_tracks_attr.tid < 1000;

