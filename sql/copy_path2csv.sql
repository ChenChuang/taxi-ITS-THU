\i create_function.sql
copy (select id as tid, cuid, orig_time(track_desc), dest_time(track_desc), travel_time(track_desc), way_ids as wids from taxi_tracks,taxi_paths_bn where id=tid limit 100) to '/var/lib/postgresql/9.1/main/dm.csv';

su
cp /var/lib/postgresql/9.1/main/dm.csv /home/chenchuang/Workspace/ITSproject/sql/
chmod 666 dm.csv


mysql --local-infile -u root -p
source test_mysql.sql
load data local infile 'dm.csv' into table tracks fields terminated by '\t' lines terminated by '\n';

