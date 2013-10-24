drop table ways;

create table ways(
	wid int not null,
	source int not null,
	target int not null,
	km double precision not null,
	x1 double precision not null,
	y1 double precision not null,
	x2 double precision not null,
	y2 double precision not null,
	reverse_cost double precision not null,
	primary key(wid));
