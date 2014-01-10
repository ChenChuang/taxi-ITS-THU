drop view taxi_tracks_gt_1;

create view taxi_tracks_gt_1
as
select * from taxi_tracks where id in (select tid from taxi_tracks_attr where rds_num > 20 and rds_num < 10000 and length > 0 and length < 80 and max_d > 0 and max_d < 0.3);

comment on view taxi_tracks_gt_1 is 'Tracks with high sampling-rate (max_d < 0.3) will be used as ground truth.'
