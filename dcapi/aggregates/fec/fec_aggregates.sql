

create view fec_candidate_rankings as
select candidate_id, substring(race for 1) as race, c.candidate_name, state, c.incumbent_challenger_open, total_receipts, 
    rank() over (partition by substring(race for 1) order by total_receipts desc)
from fec_candidates c
inner join fec_candidate_summaries s using (candidate_id)
where
    candidate_status = 'C'
    and election_year = '12'
order by substring(race for 1), rank;


create table agg_fec_candidate_timeline as
select candidate_id, race, (date - '2011-01-01') / 7 as week, count(*), sum(amount) as amount
from fec_candidates c
inner join (select filer_id, date, amount from fec_indiv union all select other_id, date, amount from fec_pac2cand) t on c.committee_id = t.filer_id
group by candidate_id, race, week;
