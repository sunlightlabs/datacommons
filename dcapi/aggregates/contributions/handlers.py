from dcapi.aggregates.handlers import EntityTopListHandler, \
    EntitySingletonHandler, TopListHandler, PieHandler, ALL_CYCLES, execute_one, \
    execute_top, check_empty
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
        from agg_cands_from_indiv aci
            left join politician_metadata_latest_cycle_view on recipient_entity = entity_id
        where
            contributor_entity = %s
            and aci.cycle = %s
        order by amount desc
        limit %s
    """


class OrgRecipientsHandler(EntityTopListHandler):

    fields = ['name', 'id', 'party', 'state', 'total_count', 'direct_count', 'employee_count', 'total_amount', 'direct_amount', 'employee_amount']

    stmt = """
        select recipient_name, recipient_entity, party, state, total_count, pacs_count, indivs_count, total_amount, pacs_amount, indivs_amount
        from agg_cands_from_org aco
            left join politician_metadata_latest_cycle_view on recipient_entity = entity_id
        where
            organization_entity = %s
            and aco.cycle = %s
        order by total_amount desc
        limit %s
    """

class OrgPACRecipientsHandler(EntityTopListHandler):

    fields = ['name', 'id', 'total_count', 'direct_count', 'employee_count', 'total_amount', 'direct_amount', 'employee_amount']

    stmt = """
        select recipient_name, recipient_entity, total_count, pacs_count, indivs_count, total_amount, pacs_amount, indivs_amount
        from
            agg_pacs_from_org
        where
            organization_entity = %s
            and cycle = %s
        order by total_amount desc
        limit %s
    """

class IndustriesHandler(EntityTopListHandler):

    fields = ['name', 'id', 'count', 'amount', 'should_show_entity']

    stmt = """
        select industry as name, industry_entity as id, count, amount, coalesce(should_show_entity, 't') as should_show_entity
        from agg_industries_to_cand
        left join matchbox_industrymetadata on industry_entity = entity_id
        where
            recipient_entity = %s
            and cycle = %s
        order by amount desc
        limit %s
    """

class UnknownIndustriesHandler(EntitySingletonHandler):

    fields = 'count amount'.split()

    stmt = """
        select count, amount
        from agg_unknown_industries_to_cand
        where
            recipient_entity = %s
            and cycle = %s
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
         left join politician_metadata_latest_cycle_view pm
            on me.id = pm.entity_id
         where ae.cycle  = %s
           and type      = 'politician'
         order by recipient_amount desc, recipient_count desc
         limit %s
    """


class TopPoliticiansByReceiptsByOfficeHandler(TopListHandler):
    args = 'office office office limit office limit'.split()
    fields = 'name entity_id office amount'.split()

    stmt = """
        select
            candidate_name,
            entity_id,
            office,
            total_receipts
        from(
            select
                entity_id,
                candidate_name,
                substring(race from 1 for 1) as office,
                total_receipts,
                rank() over (partition by substring(race from 1 for 1) order by total_receipts desc)
            from
                fec_candidate_summaries s
                inner join fec_candidates c using (candidate_id)
                inner join matchbox_entityattribute a on s.candidate_id = a.value and a.namespace = 'urn:fec:candidate'
                inner join politician_metadata_latest_cycle_view pm using (entity_id)
        ) x
        where
            case when %s = 'house' then office = 'H' when %s = 'senate' then office = 'S' when %s = 'president' then office = 'P' else 'f' end
            and rank <= %s

        union all

        select
            name as candidate_name,
            entity_id,
            seat as office,
            recipient_amount as total_receipts
        from
            agg_entities ae
            inner join matchbox_entity me on ae.entity_id = me.id
            inner join politician_metadata_latest_cycle_view pm using (entity_id)
        where
            (%s = 'governor' and seat = 'state:governor')
            and ae.cycle = 2012
        order by total_receipts desc
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

    fields = ['name', 'id', 'count', 'amount', 'should_show_entity']

    stmt = """
        select name, me.id, contributor_count, contributor_amount, coalesce(should_show_entity, 't') as should_show_entity
          from agg_entities ae
         inner join matchbox_entity me
            on ae.entity_id = me.id
         left join matchbox_industrymetadata mim
            using (entity_id)
         where cycle = %s
           and type  = 'industry'
           and coalesce(should_show_entity, 't')
           and parent_industry_id is null -- don't include subindustries
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

class IndustryOrgHandler(EntityTopListHandler):
    fields = ['name', 'id', 'total_count', 'direct_count', 'employee_count', 'total_amount', 'direct_amount', 'employee_amount']

    stmt = """
        select organization_name, organization_entity, total_count, pacs_count, indivs_count, total_amount, pacs_amount, indivs_amount
        from agg_top_orgs_by_industry
        where
            industry_entity = %s
            and cycle = %s
        order by total_amount desc
        limit %s
    """


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


class TopIndividualContributorsToPartyHandler(TopListHandler):
    args = ['party', 'limit', 'cycle']
    fields = ['entity_id', 'name', 'party', 'cycle', 'count', 'amount', 'rank']

    stmt = """
        select * from (
            select
                contributor_entity,
                name,
                recipient_party,
                cycle,
                count,
                amount,
                rank() over (partition by cycle, recipient_party order by amount desc, count desc) as rank
            from agg_party_from_indiv
            inner join matchbox_entity me on me.id = contributor_entity
            where type = 'individual'
        ) x
        where
            upper(recipient_party) = %s
            and rank <= %s
            and cycle = %s
        ;
    """

# TODO: broken, doesn't work
# part of the reason this is broken is because the associations table for lobbyists is broken, and the agg_lobbying_lobbyists_for_registrant table is thus broken
class TopLobbyistsHandler(TopListHandler):
    args = ['cycle', 'limit']
    fields = ['entity_id', 'name', 'cycle', 'num_contracts', 'contracts_amount', 'rank']

    stmt = """
        select
            entity_id,
            me.name,
            cycle,
            count(*),
            sum(non_firm_spending) as non_firm_spending_total,
            sum(firm_income) as firm_income_total
        from agg_lobbying_totals -- doesn't work, this table doesn't keep any totals for lobbyist entities
            inner join matchbox_entity me on me.id = entity_id
        where type = 'individual'
            and cycle = %s
        group by entity_id, me.name, cycle
        order by sum(non_firm_spending) desc, sum(firm_income) desc, count(*) desc
        limit %s
        ;
    """


class TopLobbyistBundlersHandler(TopListHandler):
    args = ['cycle', 'limit']
    fields = 'entity_id name count amount'.split()

    stmt = """
        select
            lobbyist_id,
            me.name,
            count(*),
            sum(amount)
        from
            agg_bundling ab
            inner join matchbox_entity me on me.id = ab.lobbyist_id
        where
            cycle = %s
        group by
            lobbyist_id,
            me.name
        order by
            sum(amount) desc,
            count(*) desc
        limit %s;
    """


class TopIndustryContributorsToPartyHandler(TopListHandler):
    args = ['party', 'limit', 'cycle']
    fields = ['entity_id', 'name', 'party', 'cycle', 'count', 'amount', 'rank']

    stmt = """
        select * from (
            select
                organization_entity,
                name,
                recipient_party,
                cycle,
                count,
                amount,
                rank() over (partition by cycle, recipient_party order by amount desc, count desc) as rank
            from agg_party_from_org
            inner join matchbox_entity me on me.id = organization_entity
            inner join matchbox_entityattribute mea on me.id = mea.entity_id and mea.namespace = 'urn:crp:industry'
            where type = 'industry'
                and name not ilike '%%unknown%%' 
                and name not ilike '%%retired%%' 
                and name not ilike '%%self%%' 
                and name not ilike '%%own campaign%%'
        ) x
        where
            upper(recipient_party) = %s
            and rank <= %s
            and cycle = %s
        ;
    """

