drop view taxi_tracks_mm;

create view taxi_tracks_mm
as
select * from taxi_tracks where id in (select tid from taxi_tracks_attr where rds_num > 3 and rds_num < 100 and length < 80)

comment on view taxi_tracks_mm is 'Only valid tracks with reasonable length and number of records will be map-matched later.'
