drop view ways_and_attrs;

create view ways_and_attrs
as
select ways.*, wattr.* from ways, ways_ut_attr as wattr where ways.id = wattr.wid;
