-- need to periodically check by hand for new manual fixes that may be needed in the postload.
-- here are two queries to run


with bad_entries as (
    select candidate_id, candidate_name, candidate_state, count(*)
    from fec_indexp_import
    where
        candidate_id not in (select candidate_id from fec_candidates)
    group by candidate_id, candidate_name, candidate_state
    order by candidate_name)
select b.*, c.candidate_id, c.candidate_name
from bad_entries b
left join fec_candidates c on c.candidate_name ilike (b.candidate_name || '%');

