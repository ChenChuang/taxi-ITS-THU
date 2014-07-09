drop view ways_and_sf;

create view ways_and_sf
as
select ways.*, wattr.*, minloc(wattr.used_interval) as minl, maxloc(wattr.used_interval) as maxl, wpd.pickup, wpd.dropoff, wpd.pickup + wpd.dropoff as heat from ways, ways_ut_attr_2 as wattr, ways_pickdrop as wpd where ways.id = wpd.wid and ways.id = wattr.wid;
