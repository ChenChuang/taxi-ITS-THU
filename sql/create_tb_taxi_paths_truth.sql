drop table taxi_paths_truth;

create table taxi_paths_truth(
	tid int not null references taxi_tracks(id),
	way_ids text not null,
	path_geom geometry not null,
	primary key(tid));

insert into taxi_paths_truth (tid, way_ids, path_geom)
select tid, way_ids, path_geom from taxi_paths_uti where tid in 
(18, 28, 69, 73, 96, 456, 464, 476, 477, 483, 548, 550, 662, 691, 735, 784);

insert into taxi_paths_truth (tid, way_ids, path_geom)
select tid, way_ids, path_geom from taxi_paths_iv where tid in 
(84, 97, 451, 481, 501, 727, 768);

insert into taxi_paths_truth (tid, way_ids, path_geom)
select tid, way_ids, path_geom from taxi_paths_ut where tid in 
(479, 505, 658, 724);

insert into taxi_paths_truth (tid, way_ids, path_geom)
select tid, way_ids, path_geom from taxi_paths_bn where tid in 
(891);

insert into taxi_paths_truth (tid, way_ids, path_geom)
select tid, way_ids, path_geom from taxi_paths_st where tid in 
(940);
