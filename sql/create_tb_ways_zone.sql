create table ways_zone(
    wid int not null,
    label int not null default -1,
    primary key(wid));
insert into ways_zone(wid) select id from ways;
