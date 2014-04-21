create view ways_and_score
as
select ways.*, road_score.* from ways, road_score where ways.id = road_score.wid;
