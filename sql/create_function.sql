CREATE OR REPLACE FUNCTION orig_time(text) RETURNS text as $$
DECLARE
    arr text[];
    arrb text[];
    x text;
BEGIN
    select string_to_array($1, ',') into arr;
    select string_to_array(arr[1], ' ') into arrb;
    select arrb[1] into x;
    return x;
END;
$$ LANGUAGE plpgsql VOLATILE;

CREATE OR REPLACE FUNCTION orig_hour(text) RETURNS integer as $$
DECLARE
    arr text[];
    arrb text[];
    x integer;
BEGIN
    select string_to_array($1, ',') into arr;
    select string_to_array(arr[1], ' ') into arrb;
    select cast(substring(arrb[1] from 12 for 2) as integer) into x;
    return x;
END;
$$ LANGUAGE plpgsql VOLATILE;

CREATE OR REPLACE FUNCTION dest_time(text) RETURNS text as $$
DECLARE
    arr text[];
    arrb text[];
    x text;
BEGIN
    select string_to_array($1, ',') into arr;
    select string_to_array(arr[array_upper(arr,1)-1], ' ') into arrb;
    select arrb[1] into x;
    return x;
END;
$$ LANGUAGE plpgsql VOLATILE;

CREATE OR REPLACE FUNCTION time_between(text, text) RETURNS text as $$
DECLARE
    a timestamp;
    b timestamp;
    x text;
BEGIN
    select to_timestamp($1, 'YYYY-MM-DDTHH:MI:SSZ') into a;
    select to_timestamp($2, 'YYYY-MM-DDTHH:MI:SSZ') into b;
    select to_char(b-a, 'HH24:MI:SS') into x;
    return x;
END;
$$ LANGUAGE plpgsql VOLATILE;

CREATE OR REPLACE FUNCTION travel_time(text) RETURNS text as $$
DECLARE
    x text;
BEGIN
    select time_between(orig_time($1), dest_time($1)) into x;
    return x;
END;
$$ LANGUAGE plpgsql VOLATILE;

CREATE OR REPLACE FUNCTION minval(text) RETURNS integer as $$
DECLARE
    arr integer[];
    minv integer default -1;
BEGIN
    --select sort_asc(string_to_array($1, ',')::integer[]) into arr;
    select array_agg(x) from (select unnest(string_to_array($1, ',')::integer[]) AS x order by x) as y into arr;
    select arr[1] into minv;
    return minv;
END;
$$ LANGUAGE plpgsql VOLATILE;

CREATE OR REPLACE FUNCTION maxval(text) RETURNS integer as $$
DECLARE
    arr integer[];
    maxv integer default -1;
BEGIN
    --select sort_desc(string_to_array($1, ',')::integer[]) into arr;
    select array_agg(x) from (select unnest(string_to_array($1, ',')::integer[]) AS x order by x desc) as y into arr;
    select arr[1] into maxv;
    return maxv;
END;

$$ LANGUAGE plpgsql VOLATILE;
CREATE OR REPLACE FUNCTION minloc(text) RETURNS integer as $$
DECLARE
    arr integer[];
    minv integer default -1;
    minl integer default -1;
BEGIN
    select string_to_array($1, ',')::integer[] into arr;
    select minval($1) into minv;
    select idx(arr, minv) into minl;
    return minl;
END;
$$ LANGUAGE plpgsql VOLATILE;

CREATE OR REPLACE FUNCTION maxloc(text) RETURNS integer as $$
DECLARE
    arr integer[];
    maxv integer default -1;
    maxl integer default -1;
BEGIN
    select string_to_array($1, ',')::integer[] into arr;
    select maxval($1) into maxv;
    select idx(arr, maxv) into maxl;
    return maxl;
END;
$$ LANGUAGE plpgsql VOLATILE;

CREATE OR REPLACE FUNCTION idx(anyarray, anyelement)
  RETURNS int AS 
$$
  SELECT i FROM (
         SELECT generate_series(array_lower($1,1),array_upper($1,1))
          ) g(i)
          WHERE $1[i] = $2
          LIMIT 1;
$$ LANGUAGE sql IMMUTABLE;

CREATE OR REPLACE FUNCTION intat(text, integer) RETURNS integer as $$
DECLARE
    arr integer[];
BEGIN
    select string_to_array($1, ',')::integer[] into arr;
    return arr[$2];
END;
$$ LANGUAGE plpgsql VOLATILE;
