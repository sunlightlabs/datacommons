\set agg_top_n 10


-- indexes

create index regulations_submitter_matches_entity_id on regulations_submitter_matches (entity_id);
create index regulations_text_matches_entity_id on regulations_text_matches (entity_id);


drop view if exists agg_regulations_collapsed_matches;
create view agg_regulations_collapsed_matches as
select document_id, entity_id
from regulations_text_matches
group by document_id, entity_id;


DROP TABLE IF EXISTS agg_regulations_text;
CREATE TABLE agg_regulations_text as
WITH ranked_aggregates as (
    SELECT
        entity_id, d.docket_id, d.title, d.agency, extract(year from d.date)::integer as year, count(*),
        rank() over (PARTITION BY entity_id ORDER BY count(*) desc) as rank
    FROM regulations_comments_full
    INNER JOIN agg_regulations_collapsed_matches USING (document_id)
    INNER JOIN regulations_dockets d USING (docket_id)
    GROUP BY entity_id, d.docket_id, d.title, d.agency, extract(year from d.date)
)
SELECT entity_id, -1 as cycle, agency, docket_id as docket, year, count
FROM ranked_aggregates
where rank <= :agg_top_n

union all

SELECT entity_id, cycle, agency, docket_id as docket, year, count
FROM (
    select entity_id, (case when year % 2 = 0 then year else year + 1 end) as cycle, agency, docket_id, year, count,
        rank() over (partition by entity_id, (case when year % 2 = 0 then year else year + 1 end) order by count desc) as rank
    from ranked_aggregates) x
where rank <= :agg_top_n
;


DROP TABLE IF EXISTS agg_regulations_text_totals;
CREATE TABLE agg_regulations_text_totals as
WITH totals as (
    SELECT
        entity_id, extract(year from d.date)::integer as year, docket_id as docket, count(*)
    FROM regulations_comments_full
    INNER JOIN agg_regulations_collapsed_matches USING (document_id)
    INNER JOIN regulations_dockets d USING (docket_id)
    GROUP BY entity_id, extract(year from d.date)::integer, docket_id
)
SELECT
    entity_id, -1 as cycle,
    count(distinct docket) as docket_count,
    sum(count) as document_count
FROM totals
GROUP BY entity_id

union all

SELECT
    entity_id, (case when year % 2 = 0 then year else year + 1 end) as cycle,
    count(distinct docket) as docket_count,
    sum(count) as document_count
FROM totals
GROUP BY entity_id, (case when year % 2 = 0 then year else year + 1 end)
;


DROP TABLE IF EXISTS agg_regulations_submitter;
CREATE TABLE agg_regulations_submitter as
WITH ranked_aggregates as (
    SELECT
        entity_id, d.agency, d.docket_id, extract(year from d.date)::integer as year, count(*),
        rank() over (PARTITION BY entity_id ORDER BY count(*) desc) as rank
    FROM regulations_comments_full
    INNER JOIN regulations_submitter_matches USING (document_id)
    INNER JOIN regulations_dockets d USING (docket_id)
    GROUP BY entity_id, d.agency, d.docket_id, extract(year from d.date)
)
SELECT entity_id, -1 as cycle, agency, docket_id as docket, year, count
FROM ranked_aggregates
where rank <= :agg_top_n

union all

SELECT entity_id, cycle, agency, docket_id as docket, year, count
FROM (
    select entity_id, (case when year % 2 = 0 then year else year + 1 end) as cycle, agency, docket_id, year, count,
        rank() over (partition by entity_id, (case when year % 2 = 0 then year else year + 1 end) order by count desc) as rank
    from ranked_aggregates) x
where rank <= :agg_top_n
;


DROP TABLE IF EXISTS agg_regulations_submitter_totals;
CREATE TABLE agg_regulations_submitter_totals as
WITH totals as (
    SELECT
        entity_id, extract(year from d.date)::integer as year, docket_id as docket, count(*)
    FROM regulations_comments_full
    INNER JOIN regulations_submitter_matches USING (document_id)
    INNER JOIN regulations_dockets d USING (docket_id)
    GROUP BY entity_id, extract(year from d.date)::integer, docket_id
)
SELECT
    entity_id, -1 as cycle,
    count(distinct docket) as docket_count,
    sum(count) as document_count
FROM totals
GROUP BY entity_id

union all

SELECT
    entity_id, (case when year % 2 = 0 then year else year + 1 end) as cycle,
    count(distinct docket) as docket_count,
    sum(count) as document_count
FROM totals
GROUP BY entity_id, (case when year % 2 = 0 then year else year + 1 end)
;
