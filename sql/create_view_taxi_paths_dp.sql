drop view taxi_paths_dp;

create view taxi_paths_dp
as
select tid,way_ids from taxi_paths_bn where tid in (select tid from taxi_tid_dp_1);
