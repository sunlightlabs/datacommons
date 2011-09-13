from dcapi.aggregates.handlers import EntityTopListHandler


class FACAAgenciesHandler(EntityTopListHandler):
    
    fields = ['agencyabbr', 'agencyname', 'member_count', 'committee_count']
    
    stmt = """
        select agencyabbr, agencyname, count(distinct MemberName) as member_count, count(distinct CommitteeName) as committee_count
        from faca_records, (values (%s::uuid, %s::integer)) as params (entity_id, cycle)
        where
            org_id = params.entity_id
            and (params.cycle = -1 or params.cycle between extract(year from StartDate) and extract(year from EndDate) + 1)
        group by agencyabbr, agencyname
        order by count(*) desc
        limit %s
    """

class FACACommitteeMembersHandler(EntityTopListHandler):
    
    args = ['entity_id', 'agency', 'cycle', 'limit']
    
    fields = ['ComitteeName', 'MemberName', 'Chair', 'Affiliation', 'StartDate', 'EndDate']
    
    stmt = """
        select CommitteeName, MemberName, Chair, Affiliation, StartDate, EndDate
        from faca_records, (values (%s::uuid, %s, %s::integer)) as params (entity_id, agency, cycle)
        where
            org_id = params.entity_id
            and AgencyAbbr = params.agency
            and (params.cycle = -1 or params.cycle between extract(year from StartDate) and extract(year from EndDate) + 1)
        order by CommitteeName, MemberName, StartDate
        limit %s
    """