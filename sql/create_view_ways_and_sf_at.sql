drop view ways_and_sf_at;
        
create view ways_and_sf_at
as
select ways.*, 
intat(wattr.used_interval, 1) as at_1, 
intat(wattr.used_interval, 2) as at_2, 
intat(wattr.used_interval, 3) as at_3, 
intat(wattr.used_interval, 4) as at_4, 
intat(wattr.used_interval, 5) as at_5, 
intat(wattr.used_interval, 6) as at_6, 
intat(wattr.used_interval, 7) as at_7, 
intat(wattr.used_interval, 8) as at_8, 
intat(wattr.used_interval, 9) as at_9, 
intat(wattr.used_interval, 10) as at_10 
from ways, ways_ut_attr_2 as wattr where ways.id = wattr.wid;

