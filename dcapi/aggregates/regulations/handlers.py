
from dcapi.aggregates.handlers import EntityTopListHandler

class RegulationsHandler(EntityTopListHandler):
    
    fields = "agency docket year count".split()
    
    stmt = """
        select agency, docket, year, count
        from agg_regulations
        where
            entity_id = %s
            and cycle = %s
        order by count desc
        limit %s"""