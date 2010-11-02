from dcapi.aggregates.handlers import execute_top, TopListHandler
from dcentity.models import Entity, EntityAttribute, OrganizationMetadata, PoliticianMetadata, BioguideInfo
from django.forms.models import model_to_dict
from piston.handler import BaseHandler
from piston.utils import rc
from urllib import unquote_plus
from django.core.exceptions import ObjectDoesNotExist
from uuid import UUID



get_totals_stmt = """
     select cycle,
            coalesce(contributor_count,  0)::integer,
            coalesce(recipient_count,    0)::integer,
            coalesce(contributor_amount, 0)::float,
            coalesce(recipient_amount,   0)::float,
            coalesce(l.count,            0)::integer,
            coalesce(firm_income,        0)::float,
            coalesce(non_firm_spending,  0)::float,
            coalesce(grant_count,        0)::integer,
            coalesce(contract_count,     0)::integer,
            coalesce(loan_count,         0)::integer,
            coalesce(grant_amount,       0)::float,
            coalesce(contract_amount,    0)::float,
            coalesce(loan_amount,        0)::float
     from
         (select *
         from agg_entities
         where entity_id = %s) c
     full outer join
         (select *
         from agg_lobbying_totals
         where entity_id = %s) l
     using (cycle)
     full outer join
         (select *
         from agg_spending_totals
         where recipient_entity = %s) s
     using (cycle)
"""

def get_totals(entity_id):
    totals = dict()
    for row in execute_top(get_totals_stmt, entity_id, entity_id, entity_id):
        totals[row[0]] = dict(zip(EntityHandler.totals_fields, row[1:]))
    return totals


class EntityHandler(BaseHandler):
    allowed_methods = ('GET',)

    totals_fields = ['contributor_count', 'recipient_count', 'contributor_amount', 'recipient_amount', 'lobbying_count', 'firm_income', 'non_firm_spending', 'grant_count', 'contract_count', 'loan_count', 'grant_amount', 'contract_amount', 'loan_amount']
    ext_id_fields = ['namespace', 'id']

    def read(self, request, entity_id):

        try:
            entity_id = UUID(entity_id)
            entity = Entity.objects.select_related().get(id=entity_id)
        except ObjectDoesNotExist:
            return rc.NOT_FOUND
        except ValueError:
            return rc.NOT_FOUND

        totals = get_totals(entity_id)

        external_ids = [{'namespace': attr.namespace, 'id': attr.value} for attr in entity.attributes.all()]

        result = {'name': entity.name,
                  'id': entity.id,
                  'type': entity.type,
                  'totals': totals,
                  'external_ids': external_ids,
                  'metadata': entity.metadata}

        return result


class EntityAttributeHandler(BaseHandler):
    allowed_methods = ('GET',)
    fields = ['id']

    def read(self, request):
        namespace = request.GET.get('namespace', None)
        bioguide_id = request.GET.get('bioguide_id', None)
        id = request.GET.get('id', None)

        if (not id or not namespace) and not bioguide_id:
            error_response = rc.BAD_REQUEST
            error_response.write("Must include a 'namespace' and an 'id' parameter or a 'bioguide_id' parameter.")
            return error_response

        if bioguide_id:
            entities = BioguideInfo.objects.filter(bioguide_id = bioguide_id)
        else:
            entities = EntityAttribute.objects.filter(namespace = namespace, value = id)

        return [{'id': e.entity_id} for e in entities]


class EntitySearchHandler(BaseHandler):
    allowed_methods = ('GET',)

    fields = [
        'id', 'name', 'type',
        'count_given', 'count_received', 'count_lobbied',
        'total_given','total_received', 'firm_income', 'non_firm_spending',
        'state', 'party', 'seat', 'lobbying_firm'
    ]

    stmt = """
        select
            e.id, e.name, e.type,
            coalesce(a.contributor_count, 0), coalesce(a.recipient_count, 0), coalesce(l.count, 0),
            coalesce(a.contributor_amount, 0), coalesce(a.recipient_amount, 0),
            coalesce(l.firm_income, 0), coalesce(l.non_firm_spending, 0),
            pm.state, pm.party, pm.seat, om.lobbying_firm
        from matchbox_entity e
        inner join (select distinct entity_id
                    from matchbox_entityalias ea
                    where to_tsvector('datacommons', ea.alias) @@ to_tsquery('datacommons', quote_literal(%s))) ft_match
            on e.id = ft_match.entity_id
        left join matchbox_politicianmetadata pm
            on e.id = pm.entity_id
        left join matchbox_organizationmetadata om
            on e.id = om.entity_id
        left join agg_lobbying_totals l
            on e.id = l.entity_id
        left join agg_entities a
            on e.id = a.entity_id
        where
            (a.cycle = -1 and l.cycle = -1)
            or (a.cycle = -1 and l.cycle is null)
            or (a.cycle is null and l.cycle = -1)
    """

    def read(self, request):
        query = request.GET.get('search', None)
        if not query:
            error_response = rc.BAD_REQUEST
            error_response.write("Must include a query in the 'search' parameter.")
            return error_response

        parsed_query = ' & '.join(unquote_plus(query).split(' '))

        raw_result = execute_top(self.stmt, parsed_query)

        return [dict(zip(self.fields, row)) for row in raw_result]

class EntitySimpleHandler(BaseHandler):
    allowed_methods = ('GET',)

    fields = [
        'id', 'name', 'type',
    ]

    def read(self, request):
        entity_type = request.GET.get('type', None)
        count = request.GET.get('count', None)

        start = request.GET.get('start', None)
        end = request.GET.get('end', None)

        qs = Entity.objects.all().order_by('id')

        if entity_type:
            qs = qs.filter(type=entity_type)

        if count:
            return {'count': qs.count()}
        else:
            if start is not None and end is not None:
                try:
                    start = int(start)
                    end = int(end)
                except:
                    error_response = rc.BAD_REQUEST
                    error_response.write("Must provide integers for start and end.")
                    return error_response
            else:
                error_response = rc.BAD_REQUEST
                error_response.write("Must specify valid start and end parameters.")
                return error_response

            if (end < start or end - start > 10000):
                error_response = rc.BAD_REQUEST
                error_response.write("Only 10,000 entities can be retrieved at a time.")
                return error_response

            result = qs[start:end]
            return [{'id': row.id, 'name': row.name, 'type': row.type} for row in result]


class CurrentRaceHandler(TopListHandler):

    args = ['district', 'district', 'district', 'district']

    fields = "entity_id name state election_type district seat seat_status seat_result votesmart_id party".split()

    stmt = """
        select entity_id, name, cr.state, election_type, district, cr.seat, seat_status, seat_result, votesmart_id, party
        from matchbox_currentrace cr
        inner join matchbox_votesmartinfo vsi on cr.id = vsi.entity_id
        inner join matchbox_politicianmetadata pm using (entity_id)
        where
            case
                when district is null then lower(substring(%s for 2)) = lower(cr.state)
                else case
                        when char_length(%s) = 5 then lower(%s) = lower(district)
                        else lower(substring(%s for 2)) = lower(cr.state)
                     end
            end
            and election_type = 'G'
    """

class CurrentRaceDistrictsHandler(TopListHandler):

    args = []

    fields = ['district']

    stmt = """
        select distinct district
        from matchbox_currentrace cr
        where election_type = 'G' and district != '' and district is not null
        order by district
    """

