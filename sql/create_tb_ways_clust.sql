create table ways_clust_som(
	wid int not null references ways(id) on delete cascade,
	clust int not null default 0,
	primary key(wid));

insert into ways_clust_som(wid) select id from ways;
