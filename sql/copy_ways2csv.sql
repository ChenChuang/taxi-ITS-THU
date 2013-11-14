copy (select tid,way_ids from taxi_paths_bn limit 10) to 'dp.csv';
copy (select * from ways) to '/var/lib/postgresql/9.1/main/ways.csv';
