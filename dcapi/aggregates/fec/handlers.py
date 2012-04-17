from django.db import connection
from dcapi.aggregates.handlers import EntitySingletonHandler, PieHandler, TopListHandler, execute_top, EntityTopListHandler


class CandidateSummaryHandler(EntitySingletonHandler):
        
    args = ['entity_id']    
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
        inner join matchbox_entityattribute a on c.candidate_id = a.value and a.namespace = 'urn:fec:candidate'
        inner join agg_fec_candidate_rankings r using (candidate_id)
        where
            a.entity_id = %s
    """


class CommitteeSummaryHandler(EntitySingletonHandler):

    args = ['entity_id']    
    fields = "total_raised contributions_from_indiv contributions_from_pacs transfers_from_affiliates nonfederal_transfers_received loans_received disbursements cash_on_hand debts contributions_to_committees independent_expenditures_made party_coordinated_expenditures_made nonfederal_expenditure_share first_filing_date last_filing_date num_committee_filings".split()

    stmt = """
        select
            sum(total_receipts - (loan_repayments + refunds_to_individuals + refunds_to_committees)),
            sum(individual_contributions - refunds_to_individuals),
            sum(contributions_from_other_committees),
            sum(transfers_from_affiliates),
            sum(nonfederal_transfers_received),
            sum(total_loans_received),
            sum(total_disbursements),
            sum(cash_close_of_period),
            sum(debts_owed),
            sum(contributions_to_committees),
            sum(independent_expenditures_made), 
            sum(party_coordinated_expenditures_made), 
            sum(nonfederal_expenditure_share),
            min(through_date),
            max(through_date),
            count(*)
        from fec_committee_summaries c
        inner join matchbox_entityattribute a on c.committee_id = a.value and a.namespace = 'urn:fec:committee'
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
        inner join matchbox_entityattribute a on c.candidate_id = a.value and a.namespace = 'urn:fec:candidate'
        where
            a.entity_id = %s
        group by local
    """

class CandidateTimelineHandler(TopListHandler):

    candidates_fields = "entity_id candidate_id candidate_name race party incumbent".split()
    candidates_stmt = """
        select entity_id, candidate_id, e.name, race, party_designation1, incumbent_challenger_open
        from fec_candidates c
        inner join matchbox_entityattribute a on c.candidate_id = a.value and a.namespace = 'urn:fec:candidate'
        inner join matchbox_entity e on a.entity_id = e.id
        where
            election_year = '12'
            and candidate_status = 'C'
            and race in 
                (select race
                from fec_candidates c
                inner join matchbox_entityattribute a on c.candidate_id = a.value and a.namespace = 'urn:fec:candidate'
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
        
        raw_candidates_result = execute_top(self.candidates_stmt, kwargs['entity_id'])
        candidates = [dict(zip(self.candidates_fields, row)) for row in raw_candidates_result]
        
        # this makes a separate query for each candidate
        # if this proves to be slow it could be done in one query with slightly more complex code
        for candidate in candidates:
            raw_timeline = execute_top(self.timeline_stmt, candidate['candidate_id'])
            candidate['timeline'] = [amount for (week, amount) in raw_timeline]
        
        return candidates


class CandidateItemizedDownloadHandler(EntityTopListHandler):
    
    args = ['entity_id']
    
    fields = "contributor_name date amount contributor_type transaction_type organization occupation city state zipcode candidate_name party race status".split()
    
    stmt = """
        select contributor_name, date, amount, contributor_type, transaction_type, 
            employer, occupation, city, state, zipcode,
            candidate_name, party, race, status
        from fec_candidate_itemized i
        inner join matchbox_entityattribute a on i.candidate_id = a.value and a.namespace = 'urn:fec:candidate'
        where
            a.entity_id = %s
        order by amount desc
    """

class CommitteeItemizedDownloadHandler(EntityTopListHandler):

    args = ['entity_id']
    fields = "contributor_name date amount contributor_type contributor_committee_id transaction_type \
                organization occupation city state zipcode \
                committee_name committee_id committee_designation committee_type committee_party interest_group connected_org".split()

    stmt = """
        select contributor_name, date, amount, contributor_type, contributor_committee_id, transaction_type,
                    employer, occupation, city, state, zipcode,
                    committee_name, committee_id, committee_designation, committee_type, committee_party, interest_group, connected_org
        from fec_committee_itemized i
        inner join matchbox_entityattribute a on i.committee_id = a.value and a.namespace = 'urn:fec:committee'
        where
            a.entity_id = %s
        order by amount desc
    """

class CommitteeTopContribsHandler(EntityTopListHandler):

    args = ['entity_id', 'limit']
    fields = "contributor_name transaction_type count amount".split()

    stmt = """
        select contributor_name, transaction_type, count(*), sum(amount)
        from fec_committee_itemized i
        inner join matchbox_entityattribute a on i.committee_id = a.value and a.namespace = 'urn:fec:committee'
        where
            a.entity_id = %s
            and transaction_type in ('10', '11', '15', '15e', '15j', '22y')
        group by contributor_name, transaction_type
        order by sum(amount) desc
        limit %s
    """

