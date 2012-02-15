from django.db import connection
from dcapi.aggregates.handlers import EntitySingletonHandler, PieHandler, TopListHandler, execute_top, EntityTopListHandler


class CandidateSummaryHandler(EntitySingletonHandler):
        
    args = ['cycle', 'entity_id']    
    fields = "total_raised total_receipts_rank total_disbursements_rank cash_on_hand_rank max_rank contributions_indiv contributions_pac contributions_party contributions_candidate transfers_in disbursements cash_on_hand date".split()
    
    stmt = """
        select
            total_receipts - (candidate_loan_repayments + other_loan_repayments + refunds_to_individuals + refunds_to_committees) as total_raised,
            r.total_receipts_rank,
            r.cash_on_hand_rank,
            r.total_disbursements_rank,
            (select count(*) from fec_candidates r where r.candidate_status = 'C' and substring(r.race for 1) = substring(c.race for 1)) as max_rank,
            total_individual_contributions - refunds_to_individuals as indiv,
            contributions_from_other_committees,
            contributions_from_party_committees,
            contributions_from_candidate + loans_from_candidate - candidate_loan_repayments as contributions_from_candidate,
            authorized_transfers_from,
            total_disbursements,
            ending_cash,
            ending_date
        from fec_candidates c
        inner join fec_candidate_summaries s using (candidate_id)
        inner join matchbox_entityattribute a on c.candidate_id = a.value and a.namespace = 'urn:fec_current_candidate:' || %s
        inner join agg_fec_candidate_rankings r using (candidate_id)
        where
            a.entity_id = %s
    """


class CandidateStateHandler(PieHandler):
    
    args = ['cycle', 'entity_id']
    
    stmt = """
        select
            case when c.state = i.state then 'in-state' else 'out-of-state' end as local,
            sum(amount),
            count(*)
        from fec_candidates c
        inner join fec_indiv i on c.committee_id = i.filer_id
        inner join matchbox_entityattribute a on c.candidate_id = a.value and a.namespace = 'urn:fec_current_candidate:' || %s
        where
            a.entity_id = %s
        group by local
    """

class CandidateTimelineHandler(TopListHandler):

    candidates_fields = "entity_id candidate_id candidate_name race party incumbent".split()
    candidates_stmt = """
        select entity_id, candidate_id, e.name, race, party_designation1, incumbent_challenger_open
        from fec_candidates c
        inner join matchbox_entityattribute a on c.candidate_id = a.value and a.namespace = 'urn:fec_current_candidate:2012'
        inner join matchbox_entity e on a.entity_id = e.id
        where
            election_year = '12'
            and candidate_status = 'C'
            and race in 
                (select race
                from fec_candidates c
                inner join matchbox_entityattribute a on c.candidate_id = a.value and a.namespace = 'urn:fec_current_candidate:' || %s
                where
                    candidate_status = 'C'
                    and a.entity_id = %s)
    """
    
    timeline_stmt = """
        with non_zero_data as
            (select week, cumulative_raised
            from agg_fec_candidate_cumulative_timeline
            where
                candidate_id = %s)
        select week, max(coalesce(cumulative_raised, 0)::integer) over (order by week)
        from (select * from generate_series(0, (select max(week) from non_zero_data)) as g(week)) all_weeks
        left join non_zero_data d using (week)
    """

    def read(self, request, **kwargs):
        c = connection.cursor()
        
        raw_candidates_result = execute_top(self.candidates_stmt, request.GET['cycle'], kwargs['entity_id'])
        candidates = [dict(zip(self.candidates_fields, row)) for row in raw_candidates_result]
        
        # this makes a separate query for each candidate
        # if this proves to be slow it could be done in one query with slightly more complex code
        for candidate in candidates:
            raw_timeline = execute_top(self.timeline_stmt, candidate['candidate_id'])
            candidate['timeline'] = [amount for (week, amount) in raw_timeline]
        
        return candidates


class CandidateItemizedDownloadHandler(EntityTopListHandler):
    
    args = ['cycle', 'entity_id']
    
    fields = "contributor_name date amount contributor_type transaction_type organization occupation city state zipcode candidate_name party race status".split()
    
    stmt = """
        select contributor_name, date, amount, contributor_type, transaction_type, 
            organization, occupation, city, state, zipcode, 
            candidate_name, party, race, status
        from fec_candidate_itemized i
        inner join matchbox_entityattribute a on i.candidate_id = a.value and a.namespace = 'urn:fec_current_candidate:' || %s
        where
            a.entity_id = %s
        order by amount desc
    """
    
