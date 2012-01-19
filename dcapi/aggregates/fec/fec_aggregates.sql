
drop view if exists agg_fec_candidate_rankings;
create view agg_fec_candidate_rankings as
select candidate_id, substring(race for 1) as race,
    rank() over (partition by substring(race for 1) order by total_receipts desc) as total_receipts_rank,
    rank() over (partition by substring(race for 1) order by ending_cash desc) as cash_on_hand_rank
from fec_candidates c
inner join fec_candidate_summaries s using (candidate_id)
where
    candidate_status = 'C'
    and election_year = '12';



drop table if exists agg_fec_candidate_timeline;
create table agg_fec_candidate_timeline as
select candidate_id, race, (date - '2011-01-01') / 7 as week, count(*), sum(amount) as amount
from fec_candidates c
inner join (select filer_id, date, amount from fec_indiv union all select other_id, date, amount from fec_pac2cand) t on c.committee_id = t.filer_id
group by candidate_id, race, week;

drop table if exists agg_fec_candidate_cumulative_timeline;
create table agg_fec_candidate_cumulative_timeline as
select candidate_id, race, week, sum(amount) OVER (partition by candidate_id, race order by week) as cumulative_raised
from agg_fec_candidate_timeline;