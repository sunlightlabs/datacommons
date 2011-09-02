\set agg_top_n 10


create view agg_regulations_collapsed_matches as
select document_id, entity_id
from regulations_text_matches
group by document_id, entity_id;


DROP TABLE IF EXISTS agg_regulations_text;
CREATE TABLE agg_regulations_text as
WITH ranked_aggregates as (
    SELECT
        entity_id, d.docket_id, d.title, d.agency, extract(year from d.date) as year, count(*),
        rank() over (PARTITION BY entity_id ORDER BY count(*) desc) as rank
    FROM regulations_comments_full
    INNER JOIN agg_regulations_collapsed_matches USING (document_id)
    INNER JOIN regulations_dockets d USING (docket_id)
    GROUP BY entity_id, d.docket_id, d.title, d.agency, extract(year from d.date)
)
SELECT entity_id, -1 as cycle, agency, docket_id as docket, year, count
FROM ranked_aggregates
where rank <= :agg_top_n;


DROP TABLE IF EXISTS agg_regulations_text_totals;
CREATE TABLE agg_regulations_text_totals as
WITH totals as (
    SELECT
        entity_id, docket_id as docket, count(*)
    FROM regulations_comments_full
    INNER JOIN agg_regulations_collapsed_matches USING (document_id)
    GROUP BY entity_id, docket_id
)
SELECT
    entity_id, -1 as cycle,
    count(distinct docket) as docket_count,
    sum(count) as document_count
FROM totals
GROUP BY entity_id;


DROP TABLE IF EXISTS agg_regulations_submitter;
CREATE TABLE agg_regulations_submitter as
WITH ranked_aggregates as (
    SELECT
        entity_id, d.agency, d.docket_id, extract(year from d.date) as year, count(*),
        rank() over (PARTITION BY entity_id ORDER BY count(*) desc) as rank
    FROM regulations_comments_full
    INNER JOIN regulations_submitter_matches USING (document_id)
    INNER JOIN regulations_dockets d USING (docket_id)
    GROUP BY entity_id, d.agency, d.docket_id, extract(year from d.date)
)
SELECT entity_id, -1 as cycle, agency, docket_id as docket, year, count
FROM ranked_aggregates
where rank <= :agg_top_n;


DROP TABLE IF EXISTS agg_regulations_submitter_totals;
CREATE TABLE agg_regulations_submitter_totals as
WITH totals as (
    SELECT
        entity_id, docket_id as docket, count(*)
    FROM regulations_comments_full
    INNER JOIN regulations_submitter_matches USING (document_id)
    GROUP BY entity_id, docket_id
)
SELECT
    entity_id, -1 as cycle,
    count(distinct docket) as docket_count,
    sum(count) as document_count
FROM totals
GROUP BY entity_id;
