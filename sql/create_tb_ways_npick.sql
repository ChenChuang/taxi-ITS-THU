create table ways_npick_c3(
	wid int not null,
	h00 double precision not null default 0,
	h01 double precision not null default 0,
	h02 double precision not null default 0,
	h03 double precision not null default 0,
	h04 double precision not null default 0,
	h05 double precision not null default 0,
	h06 double precision not null default 0,
	h07 double precision not null default 0,
	h08 double precision not null default 0,
	h09 double precision not null default 0,
	h10 double precision not null default 0,
	h11 double precision not null default 0,
	h12 double precision not null default 0,
	h13 double precision not null default 0,
	h14 double precision not null default 0,
	h15 double precision not null default 0,
	h16 double precision not null default 0,
	h17 double precision not null default 0,
	h18 double precision not null default 0,
	h19 double precision not null default 0,
	h20 double precision not null default 0,
	h21 double precision not null default 0,
	h22 double precision not null default 0,
	h23 double precision not null default 0,
	primary key(wid));
insert into ways_npick_c3(wid) select id from ways;
