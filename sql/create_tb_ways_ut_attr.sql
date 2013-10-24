drop table ways_UT_attr;

create table ways_UT_attr(
	wid int not null references ways(id) on delete cascade,
	used_times double precision not null default 0,
	weight double precision not null default 0,
	used_interval text not null default '',
	primary key(wid));
