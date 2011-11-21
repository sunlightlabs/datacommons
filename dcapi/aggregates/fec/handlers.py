from dcapi.aggregates.handlers import EntitySingletonHandler, PieHandler, TopListHandler


class CandidateSummaryHandler(EntitySingletonHandler):
        
    args = ['entity_id']    
    fields = "total_raised contributions_indiv contributions_pac contributions_party contributions_candidate transfers_in disbursements cash_on_hand".split()
    
    stmt = """
        select
            total_receipts - (candidate_loan_repayments + other_loan_repayments + refunds_to_individuals + refunds_to_committees) as tota_raised,
            total_individual_contributions - refunds_to_individuals as indiv,
            contributions_from_other_committees,
            contributions_from_party_committees,
            contributions_from_candidate + loans_from_candidate - candidate_loan_repayments,
            authorized_transfers_from,
            total_disbursements,
            ending_cash
        from fec_candidate_summaries s
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
    
    args = ['cycle', 'entity_id']
    fields = "week count amount".split()

    stmt = """
        with non_zero_data as 
            (select (date - ((%s - 1) || '-01-01')::date) / 7 as week, count(*), sum(amount) as amount
            from fec_candidates c
            inner join fec_indiv i on c.committee_id = i.filer_id
            inner join tmp_fec_crp_ids ids on c.candidate_id = ids.fec_candidate_id
            inner join matchbox_entityattribute a on ids.crp_candidate_id = a.value and a.namespace = 'urn:crp:recipient'
            where
                a.entity_id = %s
            group by week)

        select week, coalesce(count, 0), coalesce(amount, 0)
        from (select * from generate_series(0, (select max(week) from non_zero_data)) as g(week)) all_weeks
        left join non_zero_data d using (week)
        order by week
    """

