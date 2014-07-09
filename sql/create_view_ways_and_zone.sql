drop view ways_and_zone;

create view ways_and_zone
as
select ways.*, wattr.*, wclust.clust, wclust.cat, wzone.label from ways, ways_ut_attr_2 as wattr,  ways_clust_som_3 as wclust, ways_zone as wzone where ways.id = wzone.wid and ways.id = wattr.wid and ways.id = wclust.wid;
