drop table taxi_paths_dp;

create table taxi_paths_dp(
	tid int not null,
	way_ids text not null,
	primary key(tid));
