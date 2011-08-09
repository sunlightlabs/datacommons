
from dcapi.aggregates.handlers import EntityTopListHandler

class RegulationsTextHandler(EntityTopListHandler):
    
    fields = "agency docket year count".split()
    
    stmt = """
        select agency, docket, cast(year as int) as year, count
        from agg_regulations_text
        where
            entity_id = %s
            and cycle = %s
        order by count desc
        limit %s"""

class RegulationsSubmitterHandler(EntityTopListHandler):

    fields = "agency docket year count".split()

    stmt = """
        select agency, docket, cast(year as int) as year, count
        from agg_regulations_submitter
        where
            entity_id = %s
            and cycle = %s
        order by count desc
        limit %s"""
