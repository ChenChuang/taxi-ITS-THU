drop table ways_clust;

create table ways_clust(
	wid int not null references ways(id) on delete cascade,
	clust int not null default 0,
	primary key(wid));

insert into ways_clust(wid) select id from ways;
