
from dcapi.aggregates.handlers import EntityTopListHandler, TopListHandler, PieHandler, ALL_CYCLES, execute_one, execute_top, check_empty
from piston.handler import BaseHandler


class OrgPartyBreakdownHandler(PieHandler):

    category_map = {'R': 'Republicans', 'D': 'Democrats'}
    default_key = 'Other'

    stmt = """
        select recipient_party, count, amount
        from agg_party_from_org
        where
            organization_entity = %s
            and cycle = %s
    """

class OrgLevelBreakdownHandler(PieHandler):

    category_map = {'urn:fec:transaction': 'Federal', 'urn:nimsp:transaction': 'State'}

    stmt = """
        select transaction_namespace, count, amount
        from agg_namespace_from_org
        where
            organization_entity = %s
            and cycle = %s
    """

class PolLocalBreakdownHandler(PieHandler):

    stmt = """
        select local, count, amount
        from agg_local_to_politician
        where
            recipient_entity = %s
            and cycle = %s
    """

class PolContributorTypeBreakdownHandler(PieHandler):

    category_map = {'I': 'Individuals', 'C': 'PACs'}
    default_key = 'Unknown'

    stmt = """
        select contributor_type, count, amount
        from agg_contributor_type_to_politician
        where
            recipient_entity = %s
            and cycle = %s
    """

class IndivPartyBreakdownHandler(PieHandler):

    category_map = {'R': 'Republicans', 'D': 'Democrats'}
    default_key = 'Other'

    stmt = """
        select recipient_party, count, amount
        from agg_party_from_indiv
        where
            contributor_entity = %s
            and cycle = %s
    """


class PolContributorsHandler(EntityTopListHandler):
    fields = ['name', 'id', 'total_count', 'direct_count', 'employee_count', 'total_amount', 'direct_amount', 'employee_amount']

    stmt = """
        select organization_name, organization_entity, total_count, pacs_count, indivs_count, total_amount, pacs_amount, indivs_amount
        from agg_orgs_to_cand
        where
            recipient_entity = %s
            and cycle = %s
        order by total_amount desc
        limit %s
    """

class PolOrgContributorHandler(EntityTopListHandler):
    fields = ['total_count', 'direct_count', 'employee_count', 'total_amount', 'direct_amount', 'employee_amount']

    stmt = """
        select total_count, pacs_count, indivs_count, total_amount, pacs_amount, indivs_amount
        from agg_orgs_to_cand
        where
            recipient_entity = %s
            and cycle = %s
        order by total_amount desc
        limit %s
    """

class IndivOrgRecipientsHandler(EntityTopListHandler):

    fields = ['recipient_name', 'recipient_entity', 'count', 'amount']

    stmt = """
        select recipient_name, recipient_entity, count, amount
        from agg_orgs_from_indiv
        where
            contributor_entity = %s
            and cycle = %s
        order by amount desc
        limit %s
    """


class IndivPolRecipientsHandler(EntityTopListHandler):

    fields = ['recipient_name', 'recipient_entity', 'count', 'amount']

    stmt = """
        select recipient_name, recipient_entity, count, amount
        from agg_cands_from_indiv
        where
            contributor_entity = %s
            and cycle = %s
        order by amount desc
        limit %s
    """


class OrgRecipientsHandler(EntityTopListHandler):

    fields = ['name', 'id', 'total_count', 'direct_count', 'employee_count', 'total_amount', 'direct_amount', 'employee_amount']

    stmt = """
        select recipient_name, recipient_entity, total_count, pacs_count, indivs_count, total_amount, pacs_amount, indivs_amount
        from agg_cands_from_org
        where
            organization_entity = %s
            and cycle = %s
        order by total_amount desc
        limit %s
    """


class SectorsHandler(EntityTopListHandler):

    fields = ['sector', 'count', 'amount']

    stmt = """
        select sector, count, amount
        from agg_sectors_to_cand
        where
            recipient_entity = %s
            and cycle = %s
        order by amount desc
        limit %s
    """


class IndustriesBySectorHandler(EntityTopListHandler):

    args = ['entity_id', 'sector', 'cycle', 'limit']

    fields = ['industry', 'count', 'amount']

    stmt = """
        select contributor_category_order, count, amount
        from agg_cat_orders_to_cand
        where
            recipient_entity = %s
            and sector = %s
            and cycle = %s
        order by amount desc
        limit %s
    """


class TopPoliticiansByReceiptsHandler(TopListHandler):

    args = ['cycle', 'limit']

    fields = ['name', 'id', 'count', 'amount', 'state', 'party', 'seat']

    stmt = """
        select name, me.id, recipient_count, recipient_amount, state, party, seat
          from agg_entities ae
         inner join matchbox_entity me
            on ae.entity_id = id
         left join matchbox_politicianmetadata mpm
            on me.id = mpm.entity_id
         where cycle     = %s
           and type      = 'politician'
         order by recipient_amount desc, recipient_count desc
         limit %s
    """


class TopOrganizationsByContributionsHandler(TopListHandler):

    args = ['cycle', 'limit']

    fields = ['name', 'id', 'count', 'amount']

    stmt = """
        select name, id, contributor_count, contributor_amount
          from agg_entities
         inner join matchbox_entity
            on entity_id = id
         where cycle     = %s
           and type      = 'organization'
         order by contributor_amount desc, contributor_count desc
         limit %s
    """


class TopIndividualsByContributionsHandler(TopListHandler):

    args = ['cycle', 'limit']

    fields = ['name', 'id', 'count', 'amount']

    stmt = """
        select name, id, contributor_count, contributor_amount
          from agg_entities
         inner join matchbox_entity
            on entity_id = id
         where cycle     = %s
           and type      = 'individual'
         order by contributor_amount desc, contributor_count desc
         limit %s
    """


class SparklineHandler(EntityTopListHandler):

    args = ['entity_id', 'cycle']

    fields = ['step', 'amount']

    stmt = """
        select step, amount
        from agg_contribution_sparklines
        where
            entity_id = %s
            and cycle = %s
        order by step
    """

class SparklineByPartyHandler(BaseHandler):

    args   = ['entity_id', 'cycle']
    fields = ['step', 'amount']

    stmt = """
        select
            case
                when recipient_party = 'D' then 'Democrats'
                when recipient_party = 'R' then 'Republicans'
                else 'Other' end as recipient_party,
            step,
            sum(amount) as amount
        from agg_contribution_sparklines_by_party
        where
            entity_id = %s
            and cycle = %s
        group by recipient_party, step
        order by step
    """

    def read(self, request, **kwargs):
        kwargs.update({'cycle': request.GET.get('cycle', ALL_CYCLES)})

        raw_result = execute_top(self.stmt, *[kwargs[param] for param in self.args])

        labeled_result = {}

        for (party, step, amount) in raw_result:
            if not labeled_result.has_key(party): labeled_result[party] = []
            labeled_result[party].append(dict(zip(self.fields, (step, amount))))

        return check_empty(labeled_result, kwargs['entity_id'])


class ContributionAmountHandler(BaseHandler):

    args = ['contributor_entity', 'contributor_entity', 'recipient_entity']

    fields = 'recipient_entity recipient_name contributor_name contributor_entity amount'.split()

    stmt = """
        select
            recipient.entity_id as recipient_entity,
            re.name as recipient_name,
            ce.name as contributor_name,
            contributor.entity_id as contributor_entity,
            sum(amount)::integer as amount
        from
            contributions_all_relevant
            inner join recipient_associations recipient using (transaction_id)
            inner join matchbox_entity re on recipient.entity_id = re.id
            inner join (
                select * from contributor_associations
                where entity_id = %%s
                union
                select * from organization_associations oa
                where entity_id = %%s
            ) contributor using (transaction_id)
            inner join matchbox_entity ce on contributor.entity_id = ce.id
        where
            recipient.entity_id = %%s
            and %s
        group by recipient.entity_id, re.name, contributor.entity_id, ce.name
    """

    def read(self, request, **kwargs):
        cycle_where = '1=1'
        if request:
            cycle = int(request.GET.get('cycle', ALL_CYCLES))
            if cycle != -1:
                cycle_where = 'cycle = %d' % cycle

        raw_result = execute_one(self.stmt % cycle_where, *[kwargs[param] for param in self.args])
        labeled_result = dict(zip(self.fields, raw_result))

        return check_empty(labeled_result, kwargs['recipient_entity'], kwargs['contributor_entity'])

