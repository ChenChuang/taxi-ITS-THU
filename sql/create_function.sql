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

