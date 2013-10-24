drop view ways_and_attrs_2;

create view ways_and_attrs_2
as
select ways.*, wattr.* from ways, ways_ut_attr_2 as wattr where ways.id = wattr.wid;
