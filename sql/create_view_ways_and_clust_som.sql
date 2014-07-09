drop view ways_and_clust_som;

create view ways_and_clust_som
as
select ways.*, wattr.*, wclust.clust from ways, ways_ut_attr_2 as wattr, ways_clust_som as wclust where ways.id = wclust.wid and ways.id = wattr.wid;
