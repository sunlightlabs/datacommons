\set agg_top_n 10


DROP TABLE IF EXISTS agg_regulations_text;
CREATE TABLE agg_regulations_text as
WITH ranked_aggregates as (
    SELECT
        entity_id, agency, docket_id, extract(year from date_posted) as year, count(*),
        rank() over (PARTITION BY entity_id ORDER BY count(*) desc) as rank
    FROM regulations_comments_full
    INNER JOIN regulations_text_matches USING (document_id)
    GROUP BY entity_id, agency, docket_id, extract(year from date_posted)
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
    INNER JOIN regulations_text_matches USING (document_id)
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
        entity_id, agency, docket_id, extract(year from date_posted) as year, count(*),
        rank() over (PARTITION BY entity_id ORDER BY count(*) desc) as rank
    FROM regulations_comments_full
    INNER JOIN regulations_submitter_matches USING (document_id)
    GROUP BY entity_id, agency, docket_id, extract(year from date_posted)
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
