drop view taxi_paths_ok;

create view taxi_paths_ok
as
select * from taxi_paths where tid in (select tid from taxi_paths_attr where valid > 0);
