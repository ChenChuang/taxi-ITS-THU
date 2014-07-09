drop view ways_and_clust_som_3;

create view ways_and_clust_som_3
as
select ways.*, wattr.*, wclust.clust, wclust.cat from ways, ways_ut_attr_2 as wattr, ways_clust_som_3 as wclust where ways.id = wclust.wid and ways.id = wattr.wid;
