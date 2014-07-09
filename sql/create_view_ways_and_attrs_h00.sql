drop view ways_and_attrs_h00;
create view ways_and_attrs_h00
as
select ways.*, ways_freq.h00, ways_sf.h00, ways_npick.h00, ways_ndrop.h00 
from ways, ways_freq, ways_sf, ways_npick, ways_ndrop 
where ways.id = ways_freq.wid and ways.id = ways_sf.wid and ways.id = ways_npick.wid ways.id = ways_ndrop.wid;
