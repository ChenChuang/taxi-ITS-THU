truncate table ways_sf_c1;
insert into ways_sf_c1(wid) select id from ways;

truncate table ways_sf_c2;
insert into ways_sf_c2(wid) select id from ways;

truncate table ways_sf_c3;
insert into ways_sf_c3(wid) select id from ways;



truncate table ways_freq_c1;
insert into ways_freq_c1(wid) select id from ways;

truncate table ways_freq_c2;
insert into ways_freq_c2(wid) select id from ways;

truncate table ways_freq_c3;
insert into ways_freq_c3(wid) select id from ways;



truncate table ways_npick_c1;
insert into ways_npick_c1(wid) select id from ways;

truncate table ways_npick_c2;
insert into ways_npick_c2(wid) select id from ways;

truncate table ways_npick_c3;
insert into ways_npick_c3(wid) select id from ways;



truncate table ways_ndrop_c1;
insert into ways_ndrop_c1(wid) select id from ways;

truncate table ways_ndrop_c2;
insert into ways_ndrop_c2(wid) select id from ways;

truncate table ways_ndrop_c3;
insert into ways_ndrop_c3(wid) select id from ways;
