from dcapi.aggregates.handlers import EntityTopListHandler, TopListHandler
import itertools


class FACAAgenciesHandler(EntityTopListHandler):
    
    fields = ['agency_abbr', 'agency_name', 'member_count', 'committee_count']
    
    stmt = """
        select agency_abbr, agency_name, count(distinct member_name) as member_count, count(distinct committee_name) as committee_count
        from faca_records, (values (%s::uuid, %s::integer)) as params (entity_id, cycle)
        where
            org_id = params.entity_id
            and (params.cycle = -1 or params.cycle between extract(year from start_date) and extract(year from end_date) + 1)
        group by agency_abbr, agency_name
        order by count(*) desc
        limit %s
    """

class FACACommitteeMembersHandler(TopListHandler):
    
    args = ['entity_id', 'agency', 'cycle']
    
    fields = ['committee_name', 'member_name', 'chair', 'affiliation', 'start_date', 'end_date']
    
    stmt = """
        select committee_name, member_name, chair, affiliation, min(start_date) as start_date, max(end_date) as end_date
        from faca_records, (values (%s::uuid, %s, %s::integer)) as params (entity_id, agency, cycle)
        where
            org_id = params.entity_id
            and agency_abbr = params.agency
            and (params.cycle = -1 or params.cycle between extract(year from start_date) and extract(year from end_date) + 1)
        group by committee_name, member_name, chair, affiliation
        order by committee_name, member_name, start_date
    """
    
    def read(self, request, **kwargs):
        results = super(FACACommitteeMembersHandler, self).read(request, **kwargs)
        
        grouped = [{
           'committee_name': item[0],
           'memberships': list(item[1]),
        } for item in itertools.groupby(results, lambda x: x['committee_name'])]
        
        grouped_and_sorted = sorted(grouped, key=lambda x: len(x['memberships']), reverse=True)
        
        return grouped_and_sorted