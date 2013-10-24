drop table taxi_tid_dp_1;

create table taxi_tid_dp_1(
	tid int not null references taxi_tracks(id) on delete cascade,
	primary key(tid));

comment on table taxi_tid_dp_1 is 'tid of All tracks going through the intersection of ChengFu Road and ZhongGuancun East Road.'

	
