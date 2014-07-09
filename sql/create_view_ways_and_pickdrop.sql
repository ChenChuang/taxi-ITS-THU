drop view ways_and_pickdrop;

create view ways_and_pickdrop
as
select ways.*, wattr.*, wpd.pickup, wpd.dropoff, (wpd.pickup + wpd.dropoff)/(ways.km+0.7) as heat from ways, ways_ut_attr_2 as wattr, ways_pickdrop as wpd where ways.id = wpd.wid and ways.id = wattr.wid;
