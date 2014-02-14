from dcapi.aggregates.handlers import EntityTopListHandler, \
    EntitySingletonHandler, TopListHandler, PieHandler, SummaryHandler, \
    SummaryRollupHandler, SummaryBreakoutHandler, \
    ALL_CYCLES, execute_one, execute_top, check_empty, execute_all
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

class OrgOfficeTypeBreakdownHandler(PieHandler):

    categories = [ 'state:judicial', 'state:upper', 'state:lower', 'federal:president', 'federal:house', 'state:governor', 'federal:senate', 'state:office' ]
    category_map = dict(zip(categories, categories))

    stmt = """
         select seat, count, amount
         from agg_office_type_from_org
         where
            organization_entity = %s
            and cycle = %s
    """

class PolLocalBreakdownHandler(PieHandler):

    category_map = {'out-of-state': 'Out-of-State', 'in-state': 'In-State'}
    default_key = 'Unknown'

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
    args = 'office limit office limit'.split()
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
                s.candidate_name,
                c.office,
                total_receipts,
                rank() over (partition by office order by total_receipts desc)
            from
                fec_candidate_summaries s
                inner join fec_candidates c using (candidate_id, cycle)
                inner join matchbox_entityattribute a on s.candidate_id = a.value and a.namespace = 'urn:fec:candidate'
                inner join politician_metadata_latest_cycle_view pm using (entity_id, cycle)
            where 
                c.candidate_status = 'C' and 
                c.incumbent_challenger_open is not null
        ) x
        where
            office = upper(substring(%s from 1 for 1))
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
            inner join politician_metadata_latest_cycle_view pm using (entity_id, cycle)
        where
            (%s = 'governor' and seat = 'state:governor')
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

class TopIndividualContributorsByAreaHandler(TopListHandler):
    args = ['area', 'limit', 'cycle']
    fields = ['entity_id', 'name', 'area', 'cycle', 'count', 'amount', 'rank']

    stmt = """
        select * from (
            select
                contributor_entity,
                name,
                namespace,
                cycle,
                count,
                amount,
                rank() over (partition by cycle, namespace order by amount desc, count desc) as rank
            from agg_indivs_by_namespace
            inner join matchbox_entity me on me.id = contributor_entity
            where type = 'individual'
        ) x
        where
            namespace = case when %s = 'state' then 'urn:nimsp:transaction' else 'urn:fec:transaction' end
            and rank <= %s
            and cycle = %s
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


class TopOrgContributorsByAreaContributorTypeHandler(TopListHandler):
    args = 'area pac_or_employee cycle limit'.split()
    fields = 'entity_id name count amount'.split()

    stmt = """
        select
            organization_entity,
            e.name,
            count,
            amount
        from
            agg_from_org_by_namespace_contributor_type a
            inner join matchbox_entity e on e.id = a.organization_entity
        where
            transaction_namespace = case when %s = 'state' then 'urn:nimsp:transaction' else 'urn:fec:transaction' end
            and contributor_type = case when %s = 'employee' then 'I' else 'C' end
            and cycle = %s
        order by
            amount desc, count desc
        limit %s
    """


class SubIndustryTotalsHandler(BaseHandler):
    args = ['cycle']
    fields =  ['subindustry_id', 'industry_id', 'sector_id', 'total_contributions']

    stmt = """
        select
            subindustry_id,
            industry_id,
            sector_id,
            total_contributions
        from
            agg_subindustry_totals st
        where
            not exists (select 1 from agg_suppressed_catcodes sc where column1 = subindustry_id)
             %s
        order by sector_id,industry_id,subindustry_id
    """

    def read(self, request):
        cycle = request.GET.get('cycle', ALL_CYCLES)

        if cycle == ALL_CYCLES:
            cycle_where = 'and cycle = -1'
        else:
            cycle_where = 'and cycle = %d' % int(cycle)

        result = execute_all(self.stmt % cycle_where,[cycle])

        if result:
            result = [dict(zip(self.fields, row)) for row in result]

        return result

class TopIndustriesTimeSeriesHandler(BaseHandler):
    args = ['limit', 'cycle']
    fields = ['industry_id', 'industry', 'cycle', 'contributions_to_democrats',
              'contributions_to_republicans', 'total_contributions']

    stmt = """
            select
                aitp.industry_id,aitp.industry,
                cycle,
                sum(contributions_to_democrats) as contributions_to_democrats,
                sum(contributions_to_republicans) as contributions_to_republicans,
                sum(total_contributions) as total_contributions
            from
                agg_industry_to_party aitp
            join
                (   select
                        industry_id
                    from
                        (   select
                                industry_id,
                                cycle,
                                sum(total_contributions),
                                rank() over (partition by cycle order by sum(total_contributions) desc) as rank
                            from
                                agg_industry_to_party
                            where
                                subindustry_id not in ('Y0000','Y4000','Y2000','Y1200','Y1000','X1200')
                            group by
                                industry_id,cycle) as x
                    where
                        rank <= %s
                        and
                        cycle = %s ) topn on aitp.industry_id = topn.industry_id
            where
                cycle > 0
            group by
                aitp.industry_id,aitp.industry,cycle
            order by
                aitp.industry, aitp.cycle;
    """

    def read(self, request, **kwargs):
        kwargs.update({'cycle': request.GET.get('cycle', ALL_CYCLES)})
        limit = request.GET.get('limit')
        print request.GET

        raw_result = execute_all(self.stmt, *[kwargs[param] for param in self.args])

        if raw_result:
            labeled_result = [dict(zip(self.fields, row)) for row in raw_result]

        return labeled_result

### PARENTMOST ORGANIZATIONS

## ORGS: PARTY
class OrgPartyTotalsHandler(SummaryRollupHandler):

    category_map = {'R':'Republicans', 'D':'Democrats'}
    default_key = 'Other'

    stmt = """
        select 
            recipient_party, 
            total_count as count, 
            total_amount as amount 
        from
            summary_parentmost_orgs_by_party
        where cycle = %s
    """

class OrgPartyTopBiggestOrgsByContributionsHandler(SummaryBreakoutHandler):

    args = ['cycle', 'limit']

    fields = ['name', 'id', 'recipient_party', 'amount']

    stmt = """
        select 
            organization_name as name, 
            organization_entity as id, 
            recipient_party, 
            amount
        from 
            summary_parentmost_orgs_by_party
        where cycle = %s and rank_by_amount <= %s;
    """

class OrgPartySummaryHandler(SummaryHandler):
    rollup = OrgPartyTotalsHandler()
    breakout = OrgPartyTopBiggestOrgsByContributionsHandler()
    def key_function(self,x):
        recipient_party = x['recipient_party']
        if recipient_party in self.rollup.category_map:
            return self.rollup.category_map[recipient_party]
        else:
            return self.rollup.default_key

## ORGS: STATE/FED
class OrgStateFedTotalsHandler(SummaryRollupHandler):

    category_map = {'federal':'Federal',
                    'state':'State'}

    stmt = """
        select 
            state_or_federal, 
            total_count as count, 
            total_amount as amount 
        from
            summary_parentmost_orgs_by_state_fed
        where cycle = %s
    """

class OrgStateFedTopBiggestOrgsByContributionsHandler(SummaryBreakoutHandler):

    args = ['cycle', 'limit']

    fields = ['name', 'id', 'state_or_federal', 'amount']

    stmt = """
        select 
            organization_name as name, 
            organization_entity as id, 
            state_or_federal, 
            amount
        from 
            summary_parentmost_orgs_by_state_fed
        where cycle = %s and rank_by_amount <= %s;
    """

class OrgStateFedSummaryHandler(SummaryHandler):
    rollup = OrgStateFedTotalsHandler()
    breakout = OrgStateFedTopBiggestOrgsByContributionsHandler()
    def key_function(self,x):
        state_or_federal = x['state_or_federal']
        if state_or_federal in self.rollup.category_map:
            return self.rollup.category_map[state_or_federal]
        else:
            return self.rollup.default_key

## ORGS: SEAT
class OrgSeatTotalsHandler(SummaryRollupHandler):

    default_key = 'no_seat'

    category_map = {'state:judicial':'State Judicial',
                    'state:lower':'State Lower House',
                    'state:governor':'Governor', 
                    'federal:house':'US House',
                    'state:upper':'State Upper House',
                    'federal:president':'US President',
                    'federal:senate':'US Senate',
                    'state:office':'State Office'}


    stmt = """
        select 
            seat, 
            total_count as count, 
            total_amount as amount 
        from
            summary_parentmost_orgs_by_seat
        where cycle = %s
    """

class OrgSeatTopBiggestOrgsByContributionsHandler(SummaryBreakoutHandler):

    args = ['cycle', 'limit']

    fields = ['name', 'id', 'seat', 'amount']

    stmt = """
        select 
            organization_name as name, 
            organization_entity as id, 
            seat, 
            amount
        from 
            summary_parentmost_orgs_by_seat
        where cycle = %s and rank_by_amount <= %s;
    """

class OrgSeatSummaryHandler(SummaryHandler):
    rollup = OrgSeatTotalsHandler()
    breakout = OrgSeatTopBiggestOrgsByContributionsHandler()
    def key_function(self,x):
        seat = x['seat']
        if seat in self.rollup.category_map:
            return self.rollup.category_map[seat]
        else:
            return self.rollup.default_key

## ORGS: PAC/INDIV
class OrgFromPacIndivTotalsHandler(SummaryRollupHandler):
    category_map = {'direct':'Org PAC',
                    'indiv':'Org Individuals'}

    stmt = """
        select 
            direct_or_indiv, 
            total_count as count, 
            total_amount as amount
        from 
            summary_parentmost_orgs_by_indiv_pac
        where cycle = %s
    """

class OrgFromPacIndivTopBiggestOrgsByContributionsHandler(SummaryBreakoutHandler):

    args = ['cycle', 'limit']

    fields = ['name', 'id', 'direct_or_indiv', 'amount','cycle', 'rank']

    stmt = """
        select 
            organization_name as name, 
            organization_entity as id, 
            direct_or_indiv, 
            amount, cycle, rank_by_amount as rank
        from 
            summary_parentmost_orgs_by_indiv_pac
        where cycle = %s and rank_by_amount <= %s;
    """

class OrgFromPacIndivSummaryHandler(SummaryHandler):
    rollup = OrgFromPacIndivTotalsHandler()
    breakout = OrgFromPacIndivTopBiggestOrgsByContributionsHandler()
    def key_function(self,x):
        direct_or_indiv = x['direct_or_indiv']
        if direct_or_indiv in self.rollup.category_map:
            return self.rollup.category_map[direct_or_indiv]
        else:
            return self.rollup.default_key

## ORGS: RECIPIENT TYPE

class OrgRecipientTypeTotalsHandler(SummaryRollupHandler):

    category_map = {'P':'Politician',
                    'C':'Committee'}

    stmt = """
        select 
            recipient_type, 
            total_count as count, 
            total_amount as amount 
        from
            summary_parentmost_orgs_by_recipient_type
        where cycle = %s
    """

class OrgRecipientTypeTopOrgsByContributionsHandler(SummaryBreakoutHandler):

    args = ['cycle', 'limit']

    fields = ['name', 'id', 'recipient_type', 'amount']

    stmt = """
        select 
            organization_name as name, 
            organization_entity as id, 
            recipient_type, 
            amount
        from
            summary_parentmost_orgs_by_recipient_type
        where cycle = %s and rank_by_amount <= %s;
    """

class OrgRecipientTypeSummaryHandler(SummaryHandler):
    rollup = OrgRecipientTypeTotalsHandler()
    breakout = OrgRecipientTypeTopOrgsByContributionsHandler()
    def key_function(self,x):
        recipient_type = x['recipient_type']
        if recipient_type in self.rollup.category_map:
            return self.rollup.category_map[recipient_type]
        else:
            return self.rollup.default_key


### INDIVIDUALS

# INDIV PARTY
class IndividualPartyTotalsHandler(SummaryRollupHandler):

    category_map = {'R':'Republicans', 'D':'Democrats'}
    default_key = 'Other'

    stmt = """
        select 
            recipient_party,
            total_count as count,
            total_amount as amount
        from
            summary_individuals_by_party
        where 
            cycle = %s
    """

class IndividualPartyTopIndividualsByContributionsHandler(SummaryBreakoutHandler):

    args = ['cycle', 'limit']

    fields = ['name', 'id', 'recipient_party', 'amount']

    stmt = """
        select 
            individual_name as name, 
            individual_entity as id, 
            recipient_party, 
            amount
        from 
            summary_individuals_by_party
        where cycle = %s and rank_by_amount <= %s;
    """

class IndividualPartySummaryHandler(SummaryHandler):
    rollup = IndividualPartyTotalsHandler()
    breakout = IndividualPartyTopIndividualsByContributionsHandler()
    def key_function(self,x):
        recipient_party = x['recipient_party']
        if recipient_party in self.rollup.category_map:
            return self.rollup.category_map[recipient_party]
        else:
            return self.rollup.default_key

# INDIVS STATE/FED
class IndividualStateFedTotalsHandler(SummaryRollupHandler):

    category_map = {'federal':'Federal',
                    'state':'State'}

    stmt = """
        select 
            state_or_federal, 
            total_count as count, 
            total_amount as amount 
        from
            summary_individuals_by_state_fed
        where 
            cycle = %s
    """

class IndividualStateFedTopIndividualsByContributionsHandler(SummaryBreakoutHandler):

    args = ['cycle', 'limit']

    fields = ['name', 'id', 'state_or_federal', 'amount']

    stmt = """
        select 
            individual_name as name, 
            individual_entity as id, 
            state_or_federal, 
            amount
        from 
            summary_individuals_by_state_fed
        where cycle = %s and rank_by_amount <= %s;
    """

class IndividualStateFedSummaryHandler(SummaryHandler):
    rollup = IndividualStateFedTotalsHandler()
    breakout = IndividualStateFedTopIndividualsByContributionsHandler()
    def key_function(self,x):
        state_or_federal = x['state_or_federal']
        if state_or_federal in self.rollup.category_map:
            return self.rollup.category_map[state_or_federal]
        else:
            return self.rollup.default_key

# INDIVS SEAT
class IndividualSeatTotalsHandler(SummaryRollupHandler):

    category_map = {'state:judicial':'State Judicial',
                    'state:lower':'State Lower House',
                    'state:governor':'Governor', 
                    'federal:house':'US House',
                    'state:upper':'State Upper House',
                    'federal:president':'US President',
                    'federal:senate':'US Senate',
                    'state:office':'State Office'}

    stmt = """
        select 
            seat, 
            total_count as count, 
            total_amount as amount 
        from
            summary_individuals_by_seat
        where 
            cycle = %s
    """

class IndividualSeatTopIndividualsByContributionsHandler(SummaryBreakoutHandler):

    args = ['cycle', 'limit']

    fields = ['name', 'id', 'seat', 'amount']

    stmt = """
        select 
            individual_name as name, 
            individual_entity as id, 
            seat, 
            amount
        from 
            summary_individuals_by_seat
        where 
            cycle = %s and rank_by_amount <= %s;
    """

class IndividualSeatSummaryHandler(SummaryHandler):
    rollup = IndividualSeatTotalsHandler()
    breakout = IndividualSeatTopIndividualsByContributionsHandler()
    def key_function(self,x):
        seat = x['seat']
        if seat in self.rollup.category_map:
            return self.rollup.category_map[seat]
        else:
            return self.rollup.default_key

# INDIVS RECIPIENT TYPE
class IndividualRecipientTypeTotalsHandler(SummaryRollupHandler):

    category_map = {'P':'Politician',
                    'C':'Committee'}

    stmt = """
        select 
            recipient_type, 
            total_count as count, 
            total_amount as amount 
        from
            summary_individuals_by_recipient_type
        where cycle = %s
    """

class IndividualRecipientTypeTopIndividualsByContributionsHandler(SummaryBreakoutHandler):

    args = ['cycle', 'limit']

    fields = ['name', 'id', 'recipient_type', 'amount']

    stmt = """
        select 
            individual_name as name, 
            individual_entity as id, 
            recipient_type, 
            amount
        from
            summary_individuals_by_recipient_type
        where cycle = %s and rank_by_amount <= %s;
    """

class IndividualRecipientTypeSummaryHandler(SummaryHandler):
    rollup = IndividualRecipientTypeTotalsHandler()
    breakout = IndividualRecipientTypeTopIndividualsByContributionsHandler()
    def key_function(self,x):
        recipient_type = x['recipient_type']
        if recipient_type in self.rollup.category_map:
            return self.rollup.category_map[recipient_type]
        else:
            return self.rollup.default_key

# INDIV IN/OUT OF STATE
class IndividualInStateOutOfStateTotalsHandler(SummaryRollupHandler):

    category_map = {'in-state':'In-State',
                    'out-of-state':'Out-Of-State'}

    stmt = """
        select 
            in_state_out_of_state, 
            total_count as count, 
            total_amount as amount 
        from
            summary_individuals_by_in_state_out_of_state
        where cycle = %s
    """

class IndividualInStateOutOfStateTopIndividualsByContributionsHandler(SummaryBreakoutHandler):

    args = ['cycle', 'limit']

    fields = ['name', 'id', 'in_state_out_of_state', 'amount']

    stmt = """
        select 
            individual_name as name, 
            individual_entity as id, 
            in_state_out_of_state, 
            amount
        from 
            summary_individuals_by_in_state_out_of_state
        where 
            cycle = %s and rank_by_amount <= %s;
    """

class IndividualInStateOutOfStateSummaryHandler(SummaryHandler):
    rollup = IndividualInStateOutOfStateTotalsHandler()
    breakout = IndividualInStateOutOfStateTopIndividualsByContributionsHandler()
    def key_function(self,x):
        in_state_out_of_state = x['in_state_out_of_state']
        if in_state_out_of_state in self.rollup.category_map:
            return self.rollup.category_map[in_state_out_of_state]
        else:
            return self.rollup.default_key

### LOBBYIST HANDLERS
# LOBBYIST PARTY
class LobbyistPartyTotalsHandler(SummaryRollupHandler):

    category_map = {'R':'Republicans', 'D':'Democrats'}
    default_key = 'Other'

    stmt = """
        select 
            recipient_party,
            total_count as count,
            total_amount as amount
        from
            summary_lobbyists_by_party
        where 
            cycle = %s
    """

class LobbyistPartyTopLobbyistsByContributionsHandler(SummaryBreakoutHandler):

    args = ['cycle', 'limit']

    fields = ['name', 'id', 'recipient_party', 'amount']

    stmt = """
        select 
            lobbyist_name as name, 
            lobbyist_entity as id, 
            recipient_party, 
            amount
        from 
            summary_lobbyists_by_party
        where cycle = %s and rank_by_amount <= %s;
    """

class LobbyistPartySummaryHandler(SummaryHandler):
    rollup = LobbyistPartyTotalsHandler()
    breakout = LobbyistPartyTopLobbyistsByContributionsHandler()
    def key_function(self,x):
        recipient_party = x['recipient_party']
        if recipient_party in self.rollup.category_map:
            return self.rollup.category_map[recipient_party]
        else:
            return self.rollup.default_key

# LOBBYISTS STATE/FED
class LobbyistStateFedTotalsHandler(SummaryRollupHandler):

    category_map = {'federal':'Federal',
                    'state':'State'}

    stmt = """
        select 
            state_or_federal, 
            total_count as count, 
            total_amount as amount 
        from
            summary_lobbyists_by_state_fed
        where 
            cycle = %s
    """

class LobbyistStateFedTopLobbyistsByContributionsHandler(SummaryBreakoutHandler):

    args = ['cycle', 'limit']

    fields = ['name', 'id', 'state_or_federal', 'amount']

    stmt = """
        select 
            lobbyist_name as name, 
            lobbyist_entity as id, 
            state_or_federal, 
            amount
        from 
            summary_lobbyists_by_state_fed
        where cycle = %s and rank_by_amount <= %s;
    """

class LobbyistStateFedSummaryHandler(SummaryHandler):
    rollup = LobbyistStateFedTotalsHandler()
    breakout = LobbyistStateFedTopLobbyistsByContributionsHandler()
    def key_function(self,x):
        state_or_federal = x['state_or_federal']
        if state_or_federal in self.rollup.category_map:
            return self.rollup.category_map[state_or_federal]
        else:
            return self.rollup.default_key

# LOBBYISTS SEAT
class LobbyistSeatTotalsHandler(SummaryRollupHandler):

    category_map = {'state:judicial':'State Judicial',
                    'state:lower':'State Lower House',
                    'state:governor':'Governor', 
                    'federal:house':'US House',
                    'state:upper':'State Upper House',
                    'federal:president':'US President',
                    'federal:senate':'US Senate',
                    'state:office':'State Office'}

    stmt = """
        select 
            seat, 
            total_count as count, 
            total_amount as amount 
        from
            summary_lobbyists_by_seat
        where 
            cycle = %s
    """

class LobbyistSeatTopLobbyistsByContributionsHandler(SummaryBreakoutHandler):

    args = ['cycle', 'limit']

    fields = ['name', 'id', 'seat', 'amount']

    stmt = """
        select 
            lobbyist_name as name, 
            lobbyist_entity as id, 
            seat, 
            amount
        from 
            summary_lobbyists_by_seat
        where 
            cycle = %s and rank_by_amount <= %s;
    """

class LobbyistSeatSummaryHandler(SummaryHandler):
    rollup = LobbyistSeatTotalsHandler()
    breakout = LobbyistSeatTopLobbyistsByContributionsHandler()
    def key_function(self,x):
        seat = x['seat']
        if seat in self.rollup.category_map:
            return self.rollup.category_map[seat]
        else:
            return self.rollup.default_key

# LOBBYISTS RECIPIENT TYPE
class LobbyistRecipientTypeTotalsHandler(SummaryRollupHandler):

    category_map = {'P':'Politician',
                    'C':'Committee'}

    stmt = """
        select 
            recipient_type, 
            total_count as count, 
            total_amount as amount 
        from
            summary_lobbyists_by_recipient_type
        where cycle = %s
    """

class LobbyistRecipientTypeTopLobbyistsByContributionsHandler(SummaryBreakoutHandler):

    args = ['cycle', 'limit']

    fields = ['name', 'id', 'recipient_type', 'amount']

    stmt = """
        select 
            lobbyist_name as name, 
            lobbyist_entity as id, 
            recipient_type, 
            amount
        from
            summary_lobbyists_by_recipient_type
        where cycle = %s and rank_by_amount <= %s;
    """

class LobbyistRecipientTypeSummaryHandler(SummaryHandler):
    rollup = LobbyistRecipientTypeTotalsHandler()
    breakout = LobbyistRecipientTypeTopLobbyistsByContributionsHandler()
    def key_function(self,x):
        recipient_type = x['recipient_type']
        if recipient_type in self.rollup.category_map:
            return self.rollup.category_map[recipient_type]
        else:
            return self.rollup.default_key

# LOBBYISTS IN/OUT OF STATE
class LobbyistInStateOutOfStateTotalsHandler(SummaryRollupHandler):

    category_map = {'in-state':'In-State',
                    'out-of-state':'Out-Of-State'}

    stmt = """
        select 
            in_state_out_of_state, 
            total_count as count, 
            total_amount as amount 
        from
            summary_lobbyists_by_in_state_out_of_state
        where cycle = %s
    """

class LobbyistInStateOutOfStateTopLobbyistsByContributionsHandler(SummaryBreakoutHandler):

    args = ['cycle', 'limit']

    fields = ['name', 'id', 'in_state_out_of_state', 'amount']

    stmt = """
        select 
            lobbyist_name as name, 
            lobbyist_entity as id, 
            in_state_out_of_state, 
            amount
        from 
            summary_lobbyists_by_in_state_out_of_state
        where 
            cycle = %s and rank_by_amount <= %s;
    """

class LobbyistInStateOutOfStateSummaryHandler(SummaryHandler):
    rollup = LobbyistInStateOutOfStateTotalsHandler()
    breakout = LobbyistInStateOutOfStateTopLobbyistsByContributionsHandler()
    def key_function(self,x):
        in_state_out_of_state = x['in_state_out_of_state']
        if in_state_out_of_state in self.rollup.category_map:
            return self.rollup.category_map[in_state_out_of_state]
        else:
            return self.rollup.default_key

## LOBBYING ORGS

## LOBBYING ORGS: PARTY
class LobbyingOrgPartyTotalsHandler(SummaryRollupHandler):

    category_map = {'R':'Republicans', 'D':'Democrats'}
    default_key = 'Other'

    stmt = """
        select 
            recipient_party, 
            total_count as count, 
            total_amount as amount 
        from
            summary_lobbying_orgs_by_party
        where cycle = %s
    """

class LobbyingOrgPartyTopBiggestLobbyingOrgsByContributionsHandler(SummaryBreakoutHandler):

    args = ['cycle', 'limit']

    fields = ['name', 'id', 'recipient_party', 'amount']

    stmt = """
        select 
            lobbying_org_name as name, 
            lobbying_org_entity as id, 
            recipient_party, 
            amount
        from 
            summary_lobbying_orgs_by_party
        where cycle = %s and rank_by_amount <= %s;
    """

class LobbyingOrgPartySummaryHandler(SummaryHandler):
    rollup = LobbyingOrgPartyTotalsHandler()
    breakout = LobbyingOrgPartyTopBiggestLobbyingOrgsByContributionsHandler()
    def key_function(self,x):
        recipient_party = x['recipient_party']
        if recipient_party in self.rollup.category_map:
            return self.rollup.category_map[recipient_party]
        else:
            return self.rollup.default_key

## LOBBYING ORGS: STATE/FED
class LobbyingOrgStateFedTotalsHandler(SummaryRollupHandler):

    category_map = {'federal':'Federal',
                    'state':'State'}

    stmt = """
        select 
            state_or_federal, 
            total_count as count, 
            total_amount as amount 
        from
            summary_lobbying_orgs_by_state_fed
        where cycle = %s
    """

class LobbyingOrgStateFedTopBiggestLobbyingOrgsByContributionsHandler(SummaryBreakoutHandler):

    args = ['cycle', 'limit']

    fields = ['name', 'id', 'state_or_federal', 'amount']

    stmt = """
        select 
            lobbying_org_name as name, 
            lobbying_org_entity as id, 
            state_or_federal, 
            amount
        from 
            summary_lobbying_orgs_by_state_fed
        where cycle = %s and rank_by_amount <= %s;
    """

class LobbyingOrgStateFedSummaryHandler(SummaryHandler):
    rollup = LobbyingOrgStateFedTotalsHandler()
    breakout = LobbyingOrgStateFedTopBiggestLobbyingOrgsByContributionsHandler()
    def key_function(self,x):
        state_or_federal = x['state_or_federal']
        if state_or_federal in self.rollup.category_map:
            return self.rollup.category_map[state_or_federal]
        else:
            return self.rollup.default_key

## LOBBYING ORGS: SEAT
class LobbyingOrgSeatTotalsHandler(SummaryRollupHandler):

    category_map = {'state:judicial':'State Judicial',
                    'state:lower':'State Lower House',
                    'state:governor':'Governor', 
                    'federal:house':'US House',
                    'state:upper':'State Upper House',
                    'federal:president':'US President',
                    'federal:senate':'US Senate',
                    'state:office':'State Office'}

    stmt = """
        select 
            seat, 
            total_count as count, 
            total_amount as amount 
        from
            summary_lobbying_orgs_by_seat
        where cycle = %s
    """

class LobbyingOrgSeatTopBiggestLobbyingOrgsByContributionsHandler(SummaryBreakoutHandler):

    args = ['cycle', 'limit']

    fields = ['name', 'id', 'seat', 'amount']

    stmt = """
        select 
            lobbying_org_name as name, 
            lobbying_org_entity as id, 
            seat, 
            amount
        from 
            summary_lobbying_orgs_by_seat
        where cycle = %s and rank_by_amount <= %s;
    """

class LobbyingOrgSeatSummaryHandler(SummaryHandler):
    rollup = LobbyingOrgSeatTotalsHandler()
    breakout = LobbyingOrgSeatTopBiggestLobbyingOrgsByContributionsHandler()
    def key_function(self,x):
        seat = x['seat']
        if seat in self.rollup.category_map:
            return self.rollup.category_map[seat]
        else:
            return self.rollup.default_key

## LOBBYING ORGS: PAC/INDIV
class LobbyingOrgFromPacIndivTotalsHandler(SummaryRollupHandler):
    category_map = {'direct':'Org PAC',
                    'indiv':'Org Individuals'}

    stmt = """
        select 
            direct_or_indiv, 
            total_count as count, 
            total_amount as amount
        from 
            summary_lobbying_orgs_by_indiv_pac
        where cycle = %s
    """

class LobbyingOrgFromPacIndivTopBiggestLobbyingOrgsByContributionsHandler(SummaryBreakoutHandler):

    args = ['cycle', 'limit']

    fields = ['name', 'id', 'direct_or_indiv', 'amount','cycle', 'rank']

    stmt = """
        select 
            lobbying_org_name as name, 
            lobbying_org_entity as id, 
            direct_or_indiv, 
            amount, cycle, rank_by_amount as rank
        from 
            summary_lobbying_orgs_by_indiv_pac
        where cycle = %s and rank_by_amount <= %s;
    """

class LobbyingOrgFromPacIndivSummaryHandler(SummaryHandler):
    rollup = LobbyingOrgFromPacIndivTotalsHandler()
    breakout = LobbyingOrgFromPacIndivTopBiggestLobbyingOrgsByContributionsHandler()
    def key_function(self,x):
        direct_or_indiv = x['direct_or_indiv']
        if direct_or_indiv in self.rollup.category_map:
            return self.rollup.category_map[direct_or_indiv]
        else:
            return self.rollup.default_key


## POL GROUPS

## POL GROUPS: PARTY
class PolGroupPartyTotalsHandler(SummaryRollupHandler):

    category_map = {'R':'Republicans', 'D':'Democrats'}
    default_key = 'Other'

    stmt = """
        select 
            recipient_party, 
            total_count as count, 
            total_amount as amount 
        from
            summary_pol_groups_by_party
        where cycle = %s
    """

class PolGroupPartyTopBiggestPolGroupsByContributionsHandler(SummaryBreakoutHandler):

    args = ['cycle', 'limit']

    fields = ['name', 'id', 'recipient_party', 'amount']

    stmt = """
        select 
            pol_group_name as name, 
            pol_group_entity as id, 
            recipient_party, 
            amount
        from 
            summary_pol_groups_by_party
        where cycle = %s and rank_by_amount <= %s;
    """

class PolGroupPartySummaryHandler(SummaryHandler):
    rollup = PolGroupPartyTotalsHandler()
    breakout = PolGroupPartyTopBiggestPolGroupsByContributionsHandler()
    def key_function(self,x):
        recipient_party = x['recipient_party']
        if recipient_party in self.rollup.category_map:
            return self.rollup.category_map[recipient_party]
        else:
            return self.rollup.default_key

## POL GROUPS: STATE/FED
class PolGroupStateFedTotalsHandler(SummaryRollupHandler):

    category_map = {'federal':'Federal',
                    'state':'State'}

    stmt = """
        select 
            state_or_federal, 
            total_count as count, 
            total_amount as amount 
        from
            summary_pol_groups_by_state_fed
        where cycle = %s
    """

class PolGroupStateFedTopBiggestPolGroupsByContributionsHandler(SummaryBreakoutHandler):

    args = ['cycle', 'limit']

    fields = ['name', 'id', 'state_or_federal', 'amount']

    stmt = """
        select 
            pol_group_name as name, 
            pol_group_entity as id, 
            state_or_federal, 
            amount
        from 
            summary_pol_groups_by_state_fed
        where cycle = %s and rank_by_amount <= %s;
    """

class PolGroupStateFedSummaryHandler(SummaryHandler):
    rollup = PolGroupStateFedTotalsHandler()
    breakout = PolGroupStateFedTopBiggestPolGroupsByContributionsHandler()
    def key_function(self,x):
        state_or_federal = x['state_or_federal']
        if state_or_federal in self.rollup.category_map:
            return self.rollup.category_map[state_or_federal]
        else:
            return self.rollup.default_key

## POL GROUPS: SEAT
class PolGroupSeatTotalsHandler(SummaryRollupHandler):

    category_map = {'state:judicial':'State Judicial',
                    'state:lower':'State Lower House',
                    'state:governor':'Governor', 
                    'federal:house':'US House',
                    'state:upper':'State Upper House',
                    'federal:president':'US President',
                    'federal:senate':'US Senate',
                    'state:office':'State Office'}

    stmt = """
        select 
            seat, 
            total_count as count, 
            total_amount as amount 
        from
            summary_pol_groups_by_seat
        where cycle = %s
    """

class PolGroupSeatTopBiggestPolGroupsByContributionsHandler(SummaryBreakoutHandler):

    args = ['cycle', 'limit']

    fields = ['name', 'id', 'seat', 'amount']

    stmt = """
        select 
            pol_group_name as name, 
            pol_group_entity as id, 
            seat, 
            amount
        from 
            summary_pol_groups_by_seat
        where cycle = %s and rank_by_amount <= %s;
    """

class PolGroupSeatSummaryHandler(SummaryHandler):
    rollup = PolGroupSeatTotalsHandler()
    breakout = PolGroupSeatTopBiggestPolGroupsByContributionsHandler()
    def key_function(self,x):
        seat = x['seat']
        if seat in self.rollup.category_map:
            return self.rollup.category_map[seat]
        else:
            return self.rollup.default_key

## POL GROUPS: PAC/INDIV
class PolGroupFromPacIndivTotalsHandler(SummaryRollupHandler):
    category_map = {'direct':'Org PAC',
                    'indiv':'Org Individuals'}

    stmt = """
        select 
            direct_or_indiv, 
            total_count as count, 
            total_amount as amount
        from 
            summary_pol_groups_by_indiv_pac
        where cycle = %s
    """

class PolGroupFromPacIndivTopBiggestPolGroupsByContributionsHandler(SummaryBreakoutHandler):

    args = ['cycle', 'limit']

    fields = ['name', 'id', 'direct_or_indiv', 'amount','cycle', 'rank']

    stmt = """
        select 
            pol_group_name as name, 
            pol_group_entity as id, 
            direct_or_indiv, 
            amount, cycle, rank_by_amount as rank
        from 
            summary_pol_groups_by_indiv_pac
        where cycle = %s and rank_by_amount <= %s;
    """

class PolGroupFromPacIndivSummaryHandler(SummaryHandler):
    rollup = PolGroupFromPacIndivTotalsHandler()
    breakout = PolGroupFromPacIndivTopBiggestPolGroupsByContributionsHandler()
    def key_function(self,x):
        direct_or_indiv = x['direct_or_indiv']
        if direct_or_indiv in self.rollup.category_map:
            return self.rollup.category_map[direct_or_indiv]
        else:
            return self.rollup.default_key

## INDUSTRIES: PARTY
class IndustryPartyTotalsHandler(SummaryRollupHandler):

    category_map = {'R':'Republicans', 'D':'Democrats'}
    default_key = 'Other'

    stmt = """
        select 
            recipient_party, 
            total_count as count, 
            total_amount as amount 
        from
            summary_industries_by_party
        where cycle = %s
    """

class IndustryPartyTopBiggestIndustriesByContributionsHandler(SummaryBreakoutHandler):

    args = ['cycle', 'limit']

    fields = ['name', 'id', 'recipient_party', 'amount']

    stmt = """
        select 
            industry_name as name, 
            industry_entity as id, 
            recipient_party, 
            amount
        from 
            summary_industries_by_party
        where cycle = %s and rank_by_amount <= %s;
    """

class IndustryPartySummaryHandler(SummaryHandler):
    rollup = IndustryPartyTotalsHandler()
    breakout = IndustryPartyTopBiggestIndustriesByContributionsHandler()
    def key_function(self,x):
        recipient_party = x['recipient_party']
        if recipient_party in self.rollup.category_map:
            return self.rollup.category_map[recipient_party]
        else:
            return self.rollup.default_key

## INDUSTRIES: STATE/FED
class IndustryStateFedTotalsHandler(SummaryRollupHandler):

    category_map = {'federal':'Federal',
                    'state':'State'}

    stmt = """
        select 
            state_or_federal, 
            total_count as count, 
            total_amount as amount 
        from
            summary_industries_by_state_fed
        where cycle = %s
    """

class IndustryStateFedTopBiggestIndustriesByContributionsHandler(SummaryBreakoutHandler):

    args = ['cycle', 'limit']

    fields = ['name', 'id', 'state_or_federal', 'amount']

    stmt = """
        select 
            industry_name as name, 
            industry_entity as id, 
            state_or_federal, 
            amount
        from 
            summary_industries_by_state_fed
        where cycle = %s and rank_by_amount <= %s;
    """

class IndustryStateFedSummaryHandler(SummaryHandler):
    rollup = IndustryStateFedTotalsHandler()
    breakout = IndustryStateFedTopBiggestIndustriesByContributionsHandler()
    def key_function(self,x):
        state_or_federal = x['state_or_federal']
        if state_or_federal in self.rollup.category_map:
            return self.rollup.category_map[state_or_federal]
        else:
            return self.rollup.default_key

### INDUSTRIES: SEAT
#class IndustrySeatTotalsHandler(SummaryRollupHandler):
#
#    default_key = 'no_seat'
#
#    category_map = {'state:judicial':'State Judicial',
#                    'state:lower':'State Lower House',
#                    'state:governor':'Governor', 
#                    'federal:house':'US House',
#                    'state:upper':'State Upper House',
#                    'federal:president':'US President',
#                    'federal:senate':'US Senate',
#                    'state:office':'State Office'}
#
#
#    stmt = """
#        select 
#            seat, 
#            total_count as count, 
#            total_amount as amount 
#        from
#            summary_industries_by_seat
#        where cycle = %s
#    """
#
#class IndustrySeatTopBiggestIndustriesByContributionsHandler(SummaryBreakoutHandler):
#
#    args = ['cycle', 'limit']
#
#    fields = ['name', 'id', 'seat', 'amount']
#
#    stmt = """
#        select 
#            industry_name as name, 
#            industry_entity as id, 
#            seat, 
#            amount
#        from 
#            summary_industries_by_seat
#        where cycle = %s and rank_by_amount <= %s;
#    """
#
#class IndustrySeatSummaryHandler(SummaryHandler):
#    rollup = IndustrySeatTotalsHandler()
#    breakout = IndustrySeatTopBiggestIndustriesByContributionsHandler()
#    def key_function(self,x):
#        seat = x['seat']
#        if seat in self.rollup.category_map:
#            return self.rollup.category_map[seat]
#        else:
#            return self.rollup.default_key

## INDUSTRIES: PAC/INDIV
class IndustryFromPacIndivTotalsHandler(SummaryRollupHandler):
    category_map = {'direct':'Org PAC',
                    'indiv':'Org Individuals'}

    stmt = """
        select 
            direct_or_indiv, 
            total_count as count, 
            total_amount as amount
        from 
            summary_industries_by_indiv_pac
        where cycle = %s
    """

class IndustryFromPacIndivTopBiggestIndustriesByContributionsHandler(SummaryBreakoutHandler):

    args = ['cycle', 'limit']

    fields = ['name', 'id', 'direct_or_indiv', 'amount','cycle', 'rank']

    stmt = """
        select 
            industry_name as name, 
            industry_entity as id, 
            direct_or_indiv, 
            amount, cycle, rank_by_amount as rank
        from 
            summary_industries_by_indiv_pac
        where cycle = %s and rank_by_amount <= %s;
    """

class IndustryFromPacIndivSummaryHandler(SummaryHandler):
    rollup = IndustryFromPacIndivTotalsHandler()
    breakout = IndustryFromPacIndivTopBiggestIndustriesByContributionsHandler()
    def key_function(self,x):
        direct_or_indiv = x['direct_or_indiv']
        if direct_or_indiv in self.rollup.category_map:
            return self.rollup.category_map[direct_or_indiv]
        else:
            return self.rollup.default_key


## INDUSTRIES: RECIPIENT TYPE

class IndustryRecipientTypeTotalsHandler(SummaryRollupHandler):

    category_map = {'P':'Politician',
                    'C':'Committee'}

    stmt = """
        select 
            recipient_type, 
            total_count as count, 
            total_amount as amount 
        from
            summary_industries_by_recipient_type
        where cycle = %s
    """

class IndustryRecipientTypeTopIndustriesByContributionsHandler(SummaryBreakoutHandler):

    args = ['cycle', 'limit']

    fields = ['name', 'id', 'recipient_type', 'amount']

    stmt = """
        select 
            industry_name as name, 
            industry_entity as id, 
            recipient_type, 
            amount
        from
            summary_industries_by_recipient_type
        where cycle = %s and rank_by_amount <= %s;
    """

class IndustryRecipientTypeSummaryHandler(SummaryHandler):
    rollup = IndustryRecipientTypeTotalsHandler()
    breakout = IndustryRecipientTypeTopIndustriesByContributionsHandler()
    def key_function(self,x):
        recipient_type = x['recipient_type']
        if recipient_type in self.rollup.category_map:
            return self.rollup.category_map[recipient_type]
        else:
            return self.rollup.default_key

## POLITICIANS: ORGS, ORG's INDIVS, and INDIVIDUALS

class PoliticianOrgPacIndivTotalsHandler(SummaryRollupHandler):

    category_map = {'org_pac':'Org PAC',
                    'org_indiv':'Org Individuals',
                    'indiv':'Individuals'}

    stmt = """
        select 
            org_pac_indiv, 
            total_count as count, 
            total_amount as amount 
        from
            summary_politicians_by_org_pac_indiv
        where cycle = %s
    """

class PoliticianOrgPacIndivTopPoliticiansByContributionsHandler(SummaryBreakoutHandler):

    args = ['cycle', 'limit']

    fields = ['name', 'id', 'org_pac_indiv', 'amount']

    stmt = """
        select 
            politician_name as name, 
            politician_entity as id, 
            org_pac_indiv, 
            amount
        from
            summary_politicians_by_org_pac_indiv
        where cycle = %s and rank_by_amount <= %s;
    """

class PoliticianOrgPacIndivSummaryHandler(SummaryHandler):
    rollup = PoliticianOrgPacIndivTotalsHandler()
    breakout = PoliticianOrgPacIndivTopPoliticiansByContributionsHandler()
    def key_function(self,x):
        org_pac_indiv = x['org_pac_indiv']
        if org_pac_indiv in self.rollup.category_map:
            return self.rollup.category_map[org_pac_indiv]
        else:
            return self.rollup.default_key

## POLITICIANS: RECEIPTS FROM INDIVIDUALS IN-STATE/OUT-OF-STATE

class PoliticianInStateOutOfStateTotalsHandler(SummaryRollupHandler):

    category_map = {'in-state':'In-State',
                    'out-of-state':'Out-Of-State'}

    stmt = """
        select 
            in_state_out_of_state, 
            total_count as count, 
            total_amount as amount 
        from
            summary_politicians_from_individuals_by_in_state_out_of_state
        where cycle = %s
    """

class PoliticianInStateOutOfStateTopPoliticiansByContributionsHandler(SummaryBreakoutHandler):

    args = ['cycle', 'limit']

    fields = ['name', 'id', 'in_state_out_of_state', 'amount']

    stmt = """
        select 
            politician_name as name, 
            politician_entity as id, 
            in_state_out_of_state, 
            amount
        from
            summary_politicians_from_individuals_by_in_state_out_of_state
        where cycle = %s and rank_by_amount <= %s;
    """

class PoliticianInStateOutOfStateSummaryHandler(SummaryHandler):
    rollup = PoliticianInStateOutOfStateTotalsHandler()
    breakout = PoliticianInStateOutOfStateTopPoliticiansByContributionsHandler()
    def key_function(self,x):
        in_state_out_of_state = x['in_state_out_of_state']
        if in_state_out_of_state in self.rollup.category_map:
            return self.rollup.category_map[in_state_out_of_state]
        else:
            return self.rollup.default_key

## POLITICIANS: RECEIPTS FROM INDUSTRIES

class PoliticianIndustryTotalsHandler(SummaryRollupHandler):

    stmt = """
        select 
            industry_name, 
            total_count as count, 
            total_amount as amount 
        from
            summary_politicians_from_industries
        where cycle = %s
    """

class PoliticianIndustryTopPoliticiansByContributionsHandler(SummaryBreakoutHandler):

    args = ['cycle', 'limit']

    fields = ['name', 'id', 'industry_name', 'amount']

    stmt = """
        select 
            politician_name as name, 
            politician_entity as id, 
            industry_name, 
            amount
        from
            summary_politicians_from_industries
        where cycle = %s and rank_by_amount <= %s;
    """

class PoliticianIndustrySummaryHandler(SummaryHandler):
    rollup = PoliticianIndustryTotalsHandler()
    breakout = PoliticianIndustryTopPoliticiansByContributionsHandler()
    def key_function(self,x):
        industry_name = x['industry_name']
        if industry_name in self.rollup.category_map:
            return self.rollup.category_map[industry_name]
        else:
            return self.rollup.default_key
