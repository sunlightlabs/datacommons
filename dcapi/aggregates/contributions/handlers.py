
from dcapi.aggregates.handlers import EntityTopListHandler, TopListHandler, PieHandler, ALL_CYCLES, execute_one, execute_top, check_empty
from django.core.cache import cache
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

    fields = ['recipient_name', 'recipient_entity', 'party', 'state', 'count', 'amount']

    stmt = """
        select recipient_name, recipient_entity, party, state, count, amount
        from agg_cands_from_indiv
            left join matchbox_politicianmetadata on recipient_entity = entity_id
        where
            contributor_entity = %s
            and cycle = %s
        order by amount desc
        limit %s
    """


class OrgRecipientsHandler(EntityTopListHandler):

    fields = ['name', 'id', 'party', 'state', 'total_count', 'direct_count', 'employee_count', 'total_amount', 'direct_amount', 'employee_amount']

    stmt = """
        select recipient_name, recipient_entity, party, state, total_count, pacs_count, indivs_count, total_amount, pacs_amount, indivs_amount
        from agg_cands_from_org
            left join matchbox_politicianmetadata on recipient_entity = entity_id
        where
            organization_entity = %s
            and cycle = %s
        order by total_amount desc
        limit %s
    """


class IndustriesHandler(EntityTopListHandler):

    fields = ['industry', 'count', 'amount']

    stmt = """
        select industry as industry, count, amount
        from agg_industries_to_cand
        where
            recipient_entity = %s
            and cycle = %s
        order by amount desc
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


class TopIndustriesByContributionsHandler(TopListHandler):

    args = ['cycle', 'limit']

    fields = ['name', 'id', 'count', 'amount']

    stmt = """
        select name, id, contributor_count, contributor_amount
          from agg_entities
         inner join matchbox_entity
            on entity_id = id
         where cycle     = %s
           and type      = 'industry'
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


class TopOrganizationsByIndustryHandler(TopListHandler):

    args = ['entity_id', 'cycle', 'limit']

    fields = ['industry_entity', 'organization_entity', 'organization_name', 'count', 'amount']

    stmt = """
        select industry_entity, organization_entity, name as organization_name, count, amount
          from agg_top_orgs_by_industry
         inner join matchbox_entity
            on id = organization_entity
         where industry_entity = %s
            and cycle = %s
         order by count desc, amount desc
         limit %s
    """


class SparklineHandler(EntityTopListHandler):

    args   = ['entity_id', 'cycle', 'entity_id', 'cycle']
    fields = ['step', 'amount']

    stmt = """
        select step, coalesce(amount, 0)::integer
        from generate_series(1,(select greatest(max(step), 24) from agg_contribution_sparklines where entity_id = %s and cycle = %s)) as all_steps(step)
        left join (select step, amount
            from agg_contribution_sparklines
            where
                entity_id = %s
                and cycle = %s) sparkline
            using (step)
        order by step;
    """

class SparklineByPartyHandler(BaseHandler):

    args   = ['entity_id', 'cycle', 'entity_id', 'cycle']
    fields = ['step', 'amount']

    stmt = """
        select
            recipient_party,
            step,
            sum(amount)
        from (
            select
                recipient_party,
                step,
                coalesce(amount, 0)::integer as amount
            from (
                select *
                from generate_series(1,(select greatest(max(step), 24) from agg_contribution_sparklines_by_party where entity_id = %s and cycle = %s)) as all_steps(step)
                cross join (
                    select recipient_party from (values ('D'), ('R'), ('O')) as parties(recipient_party)
                ) x
            ) steps_and_parties
            left join (
                select
                    case
                        when recipient_party in('D', 'R') then recipient_party
                        else 'O'
                    end as recipient_party,
                    step,
                    amount
                from
                    agg_contribution_sparklines_by_party
                where
                    entity_id = %s
                    and cycle = %s
            ) contribution_data using (step, recipient_party)
        ) grouped
        group by recipient_party, step
        order by step, recipient_party
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

    args = ['contributor_entity', 'recipient_entity']

    fields = 'recipient_entity recipient_name contributor_entity contributor_name amount'.split()

    stmt = """
    select r.id, r.name, c.id, c.name,
        (select coalesce(sum(amount), 0)::integer
        from recipient_associations ra
        inner join (select * from contributor_associations union select * from organization_associations) ca
            on ca.entity_id = c.id
                and ra.entity_id = r.id
               and ca.transaction_id = ra.transaction_id
        inner join contributions_all_relevant contrib
            on contrib.transaction_id = ra.transaction_id
        %s) as amount
    from matchbox_entity r
    cross join matchbox_entity c
    where
        c.id = %%s
        and r.id = %%s
    """

    def read(self, request, **kwargs):
        cycle = request.GET.get('cycle', ALL_CYCLES)

        cache_key = self.get_cache_key('pairwise', kwargs['recipient_entity'], kwargs['contributor_entity'], cycle)
        cached = cache.get(cache_key, 'has expired')

        if cached == 'has expired':
            if cycle == ALL_CYCLES:
                cycle_where = ''
            else:
                cycle_where = 'where cycle = %d' % int(cycle)

            result = execute_one(self.stmt % cycle_where, *[kwargs[param] for param in self.args])

            if result:
                result = dict(zip(self.fields, result)) # add labels

            result = check_empty(result, kwargs['recipient_entity'], kwargs['contributor_entity'])
            cache.set(cache_key, result)

            return result
        else:
            return cached

    def get_cache_key(self, query_name, recipient_entity, contributor_entity, cycle):
        return "_".join([query_name, recipient_entity, contributor_entity, str(cycle)])

