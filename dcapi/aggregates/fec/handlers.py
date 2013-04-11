from piston.handler import BaseHandler

from dcapi.aggregates.handlers import EntitySingletonHandler, PieHandler, execute_top, execute_one, EntityTopListHandler


class CandidateSummaryHandler(EntitySingletonHandler):

    args = ['entity_id', 'cycle']
    fields = "total_raised office total_receipts_rank total_disbursements_rank cash_on_hand_rank max_rank contributions_indiv contributions_pac contributions_party contributions_candidate transfers_in disbursements cash_on_hand date".split()

    stmt = """
        select
            total_receipts - (candidate_loan_repayments + other_loan_repayments + refunds_to_individuals + refunds_to_committees) as total_raised,
            r.office,
            r.total_receipts_rank,
            r.total_disbursements_rank,
            r.cash_on_hand_rank,
            num_candidates_in_field,
            total_individual_contributions - refunds_to_individuals as indiv,
            contributions_from_other_committees,
            contributions_from_party_committees,
            contributions_from_candidate + loans_from_candidate - candidate_loan_repayments as contributions_from_candidate,
            authorized_transfers_from,
            total_disbursements,
            ending_cash,
            ending_date
        from fec_candidates c
        inner join fec_candidate_summaries s using (candidate_id, cycle)
        inner join matchbox_entityattribute a on c.candidate_id = a.value and a.namespace = 'urn:fec:candidate'
        left join agg_fec_candidate_rankings r on c.candidate_id = r.candidate_id and to_cycle(r.election_year) = c.cycle
        where
            a.entity_id = %s
            and c.cycle = %s
    """


class CommitteeSummaryHandler(EntitySingletonHandler):

    args = ['entity_id', 'cycle']
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
            and c.cycle = %s
    """


class CandidateStateHandler(PieHandler):

    args = ['entity_id', 'cycle']

    stmt = """
        select
            case when c.office_state = i.state then 'in-state' else 'out-of-state' end as local,
            sum(amount),
            count(*)
        from fec_candidates c
        inner join fec_indiv i on c.committee_id = i.filer_id and c.cycle = i.cycle
        inner join matchbox_entityattribute a on c.candidate_id = a.value and a.namespace = 'urn:fec:candidate'
        where
            a.entity_id = %s
            and c.cycle = %s
        group by local
    """

class CandidateTimelineHandler(EntityTopListHandler):

    candidates_fields = "entity_id candidate_id candidate_name race party incumbent".split()
    candidates_stmt = """
        select distinct entity_id, candidate_id, e.name, race, party, incumbent_challenger_open
        from fec_candidates c
        inner join matchbox_entityattribute a on c.candidate_id = a.value and a.namespace = 'urn:fec:candidate'
        inner join matchbox_entity e on a.entity_id = e.id
        where
            cycle = %s
            and candidate_status = 'C'
            and race in
                (select race
                from fec_candidates c
                inner join matchbox_entityattribute a on c.candidate_id = a.value and a.namespace = 'urn:fec:candidate'
                where
                    candidate_status = 'C'
                    and a.entity_id = %s
                    and c.cycle = %s)
    """

    timeline_stmt = """
        with non_zero_data as
            (select week, cumulative_raised
            from agg_fec_candidate_cumulative_timeline
            where
                candidate_id = %s
                and cycle = %s)
        select week, max(coalesce(cumulative_raised, 0)::integer) over (order by week)
        from (select * from generate_series(0, (select max(week) from non_zero_data)) as g(week)) all_weeks
        left join non_zero_data d using (week)
    """

    def read(self, request, **kwargs):
        cycle = request.GET.get('cycle')

        raw_candidates_result = execute_top(self.candidates_stmt, cycle, kwargs['entity_id'], cycle)
        candidates = [dict(zip(self.candidates_fields, row)) for row in raw_candidates_result]

        # this makes a separate query for each candidate
        # if this proves to be slow it could be done in one query with slightly more complex code
        for candidate in candidates:
            raw_timeline = execute_top(self.timeline_stmt, candidate['candidate_id'], cycle)
            candidate['timeline'] = [amount for (week, amount) in raw_timeline]

        return candidates


class CandidateItemizedDownloadHandler(EntityTopListHandler):

    args = ['cycle', 'entity_id']

    fields = "contributor_name date amount contributor_type transaction_type organization occupation city state zipcode candidate_name party race status".split()

    stmt = """
        select contributor_name, date, amount, contributor_type, transaction_type,
            employer, occupation, city, state, zipcode,
            candidate_name, party, race, status
        from (select * from fec_candidate_itemized where cycle = %s) i
        inner join matchbox_entityattribute a on i.candidate_id = a.value and a.namespace = 'urn:fec:candidate'
        where
            a.entity_id = %s
        order by amount desc
    """

class CommitteeItemizedDownloadHandler(EntityTopListHandler):

    args = ['cycle', 'entity_id']
    fields = "contributor_name date amount contributor_type contributor_committee_id transaction_type \
                organization occupation city state zipcode \
                committee_name committee_id committee_designation committee_type committee_party interest_group connected_org".split()

    stmt = """
        select contributor_name, date, amount, contributor_type, contributor_committee_id, transaction_type,
                    employer, occupation, city, state, zipcode,
                    committee_name, committee_id, committee_designation, committee_type, committee_party, interest_group, connected_org
        from (select * from fec_committee_itemized where cycle = %s) i
        inner join matchbox_entityattribute a on i.committee_id = a.value and a.namespace = 'urn:fec:committee'
        where
            a.entity_id = %s
        order by amount desc
    """

class CommitteeTopContribsHandler(EntityTopListHandler):

    args = ['cycle', 'entity_id', 'limit']
    fields = "contributor_name transaction_type count amount".split()

    stmt = """
        select contributor_name, transaction_type, count(*), sum(amount)
        from (
            select committee_id, contributor_name, transaction_type, amount from fec_committee_itemized
            where
                transaction_type in ('10', '11', '15', '15e', '15j', '22y')
                and cycle = %s
        ) i
        inner join matchbox_entityattribute a on i.committee_id = a.value and a.namespace = 'urn:fec:committee'
        where
            a.entity_id = %s
        group by contributor_name, transaction_type
        order by sum(amount) desc
        limit %s
    """


class ElectionSummaryHandler(BaseHandler):
    """Used on SunlightFoundation site, not in brisket."""

    fields = "house_receipts house_expenditures senate_receipts senate_expenditures romney_receipts romney_disbursements obama_receipts obama_disbursements house_indexp senate_indexp presidential_indexp".split()

    stmt = """
        with office_totals as (
            select substring(candidate_id for 1) as office, sum(total_receipts) as receipts, sum(total_disbursements) as expenditures
            from fec_candidate_summaries
            group by substring(candidate_id for 1)
        ), office_indexp as (
            select candidate_office as office, sum(amount) as total_spending
            from fec_indexp
            group by candidate_office
        )
        select
            (select receipts from office_totals where office = 'H') as house_receipts,
            (select expenditures from office_totals where office = 'H') as house_expenditures,
            (select receipts from office_totals where office = 'S') as senate_receipts,
            (select expenditures from office_totals where office = 'S') as senate_expenditures,
            (select total_receipts from fec_candidate_summaries where candidate_id = 'P80003353') as romney_receipts,
            (select total_disbursements from fec_candidate_summaries where candidate_id = 'P80003353') as romney_disbursements,
            (select total_receipts from fec_candidate_summaries where candidate_id = 'P80003338') as obama_receipts,
            (select total_disbursements from fec_candidate_summaries where candidate_id = 'P80003338') as obama_disbursements,
            (select total_spending from office_indexp where office = 'H') as house_indexp,
            (select total_spending from office_indexp where office = 'S') as senate_indexp,
            (select total_spending from office_indexp where office = 'P') as presidential_indexp
    """

    def read(self, request):
        result = execute_one(self.stmt)
        return dict(zip(self.fields, result))
