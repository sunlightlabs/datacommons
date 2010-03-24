CREATE OR REPLACE FUNCTION random_lastname()
   returns varchar
as $_$
DECLARE
   ran real := random();
   rtn varchar; 
BEGIN
   select into rtn name from lastname where ran <= norm_cum_freq order by norm_cum_freq asc limit 1;
   return rtn;
END;
$_$ language plpgsql;

CREATE OR REPLACE FUNCTION random_firstname()
   returns varchar
as $_$
DECLARE
   ran real := random();
   rtn varchar := null; 
BEGIN
   select into rtn name from firstname where ran <= norm_cum_freq order by norm_cum_freq asc limit 1;  
   return rtn;
END;
$_$ language plpgsql;

CREATE OR REPLACE FUNCTION random_name()
   returns varchar
as $_$
   select random_firstname() || ' ' || random_lastname();
$_$ language sql;


