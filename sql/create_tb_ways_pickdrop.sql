drop table ways_pickdrop;

create table ways_pickdrop(
	wid int not null references ways(id) on delete cascade,
	pickup int not null default 0,
    dropoff int not null default 0,
	primary key(wid));

insert into ways_pickdrop(wid) select id from ways;
