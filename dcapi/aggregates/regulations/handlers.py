
from dcapi.aggregates.handlers import EntityTopListHandler

class RegulationsTextHandler(EntityTopListHandler):
    
    fields = "agency docket year count title".split()
    
    stmt = """
        select agg_regulations_text.agency as agency, docket, cast(year as int) as year, count, title
        from agg_regulations_text, regulations_dockets
        where
            entity_id = %s
            and cycle = %s
            and agg_regulations_text.docket = regulations_dockets.docket_id
        order by count desc
        limit %s"""

class RegulationsSubmitterHandler(EntityTopListHandler):

    fields = "agency docket year count title".split()

    stmt = """
        select agg_regulations_submitter.agency as agency, docket, cast(year as int) as year, count, title
        from agg_regulations_submitter, regulations_dockets
        where
            entity_id = %s
            and cycle = %s
            and agg_regulations_submitter.docket = regulations_dockets.docket_id
        order by count desc
        limit %s"""
