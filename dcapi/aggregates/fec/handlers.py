from django.db import connection
from dcapi.aggregates.handlers import EntitySingletonHandler, PieHandler, TopListHandler, execute_top


class CandidateSummaryHandler(EntitySingletonHandler):
        
    args = ['entity_id']    
    fields = "total_raised rank max_rank contributions_indiv contributions_pac contributions_party contributions_candidate transfers_in disbursements cash_on_hand".split()
    
    stmt = """
        select
            total_receipts - (candidate_loan_repayments + other_loan_repayments + refunds_to_individuals + refunds_to_committees) as tota_raised,
            (select rank from fec_candidate_rankings r where s.candidate_id = r.candidate_id) as rank,
            (select count(*) from fec_candidate_rankings r where r.race = substring(c.race for 1)) as max_rank,
            total_individual_contributions - refunds_to_individuals as indiv,
            contributions_from_other_committees,
            contributions_from_party_committees,
            contributions_from_candidate + loans_from_candidate - candidate_loan_repayments as contributions_from_candidate,
            authorized_transfers_from,
            total_disbursements,
            ending_cash
        from fec_candidates c
        inner join fec_candidate_summaries s using (candidate_id)
        inner join tmp_fec_crp_ids i on s.candidate_id = i.fec_candidate_id
        inner join matchbox_entityattribute a on i.crp_candidate_id = a.value and a.namespace = 'urn:crp:recipient'
        where
            a.entity_id = %s
    """


class CandidateStateHandler(PieHandler):
    
    args = ['entity_id']
    
    stmt = """
        select
            case when c.state = i.state then 'in-state' else 'out-of-state' end as local,
            sum(amount),
            count(*)
        from fec_candidates c
        inner join fec_indiv i on c.committee_id = i.filer_id
        inner join tmp_fec_crp_ids ids on c.candidate_id = ids.fec_candidate_id
        inner join matchbox_entityattribute a on ids.crp_candidate_id = a.value and a.namespace = 'urn:crp:recipient'
        where
            a.entity_id = %s
        group by local
    """

class CandidateTimelineHandler(TopListHandler):

    candidates_fields = "candidate_id canidate_name race party incumbent".split()
    candidates_stmt = """
        select candidate_id, candidate_name, race, party_designation1, incumbent_challenger_open
        from fec_candidates
        where
            election_year = '12'
            and candidate_status = 'C'
            and race in 
                (select race
                from fec_candidates c
                inner join tmp_fec_crp_ids ids on c.candidate_id = ids.fec_candidate_id
                inner join matchbox_entityattribute a on ids.crp_candidate_id = a.value and a.namespace = 'urn:crp:recipient'
                where
                    a.entity_id = %s)
    """
    
    timeline_stmt = """
        with non_zero_data as
            (select week, amount
            from agg_fec_candidate_timeline
            where
                candidate_id = %s)
        select week, coalesce(amount, 0)
        from (select * from generate_series(0, (select max(week) from non_zero_data)) as g(week)) all_weeks
        left join non_zero_data d using (week)
    """

    def read(self, request, **kwargs):
        c = connection.cursor()
        
        raw_candidates_result = execute_top(self.candidates_stmt, kwargs['entity_id'])
        candidates = [dict(zip(self.candidates_fields, row)) for row in raw_candidates_result]
        
        # this makes a separate query for each candidate
        # if this proves to be slow it could be done in one query with slightly more complex code
        for candidate in candidates:
            raw_timeline = execute_top(self.timeline_stmt, candidate['candidate_id'])
            candidate['timeline'] = [amount for (week, amount) in raw_timeline]
        
        return candidates
