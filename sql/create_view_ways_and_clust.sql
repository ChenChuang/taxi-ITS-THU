drop view ways_and_clust;

create view ways_and_clust
as
select ways.*, wattr.*, wclust.clust from ways, ways_ut_attr_2 as wattr, ways_clust as wclust where ways.id = wclust.wid and ways.id = wattr.wid;
