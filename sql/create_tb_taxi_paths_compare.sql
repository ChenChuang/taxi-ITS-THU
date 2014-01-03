drop table taxi_paths_compare;

create table taxi_paths_compare(
	tid int not null references taxi_tracks(id),
	bn int not null default 0,
	st int not null default 0,
	iv int not null default 0,
	ut int not null default 0,
	uti int not null default 0,
    primary key(tid));

insert into taxi_paths_compare (tid) 
select bn.tid from 
taxi_paths_bn as bn, 
taxi_paths_st as st, 
taxi_paths_iv as iv, 
taxi_paths_ut as ut,
taxi_paths_uti as uti where 
bn.tid = st.tid and 
bn.tid = iv.tid and 
bn.tid = ut.tid and 
bn.tid = uti.tid and not (

( bn.way_ids like '%'||st.way_ids||'%' or st.way_ids like '%'||bn.way_ids||'%' ) and
( bn.way_ids like '%'||iv.way_ids||'%' or iv.way_ids like '%'||bn.way_ids||'%' ) and 
( bn.way_ids like '%'||ut.way_ids||'%' or ut.way_ids like '%'||bn.way_ids||'%' ) and 
( bn.way_ids like '%'||uti.way_ids||'%' or uti.way_ids like '%'||bn.way_ids||'%' ) and
 
( st.way_ids like '%'||iv.way_ids||'%' or iv.way_ids like '%'||st.way_ids||'%' ) and 
( st.way_ids like '%'||ut.way_ids||'%' or ut.way_ids like '%'||st.way_ids||'%' ) and 
( st.way_ids like '%'||uti.way_ids||'%' or uti.way_ids like '%'||st.way_ids||'%' ) and

( iv.way_ids like '%'||ut.way_ids||'%' or ut.way_ids like '%'||iv.way_ids||'%' ) and 
( iv.way_ids like '%'||uti.way_ids||'%' or uti.way_ids like '%'||iv.way_ids||'%' ) and

( ut.way_ids like '%'||uti.way_ids||'%' or uti.way_ids like '%'||ut.way_ids||'%' ) 

);
