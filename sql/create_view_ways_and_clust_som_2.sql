drop view ways_and_clust_som_2;

create view ways_and_clust_som_2
as
select ways.*, wattr.*, wclust.clust, wclust.cat from ways, ways_ut_attr_2 as wattr, ways_clust_som_2 as wclust where ways.id = wclust.wid and ways.id = wattr.wid;
