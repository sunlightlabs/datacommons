from dcapi.aggregates.handlers import EntityTopListHandler


class FACAAgenciesHandler(EntityTopListHandler):
    
    fields = ['agencyabbr', 'agencyname', 'count']
    
    stmt = """
        select agencyabbr, agencyname, count(*)
        from faca_records
        where
            org_id = %s
            and cycle = %s
        group by agencyabbr, agencyname
        order by count(*) desc
        limit %s
    """

class FACACommitteeMembersHandler(EntityTopListHandler):
    
    args = ['entity_id', 'agency', 'limit']
    
    fields = ['ComitteeName', 'Members']
    
    stmt = """
        select CommitteeName, array_agg(MemberName || ', ' || Affiliation)
        from faca_records
        where
            org_id = %s
            and AgencyAbbr = %s
        group by CommitteeName
        order by count(*) desc
        limit %s
    """