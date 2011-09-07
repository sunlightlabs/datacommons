
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

class RegulationsDocketTextHandler(EntityTopListHandler):
    
    fields = "document_id title type date_posted files".split()
    args = ['entity_id', 'docket_id', 'limit']
    
    stmt = """
        select regulations_text_matches.document_id as document_id, min(title) as title, min(type) as type, min(date_posted) as date_posted, array_agg('objectId=' || object_id || '&disposition=inline&contentType=' || file_type) as files
        from regulations_comments_full, regulations_text_matches
        where
            regulations_comments_full.document_id = regulations_text_matches.document_id
            and entity_id = %s
            and docket_id = %s
        group by regulations_text_matches.document_id
        order by date_posted desc
        limit %s"""

class RegulationsDocketSubmitterHandler(EntityTopListHandler):
    
    fields = "document_id title type date_posted".split()
    args = ['entity_id', 'docket_id', 'limit']
    
    stmt = """
        select regulations_comments_full.document_id as document_id, title, type, date_posted
        from regulations_comments_full, regulations_submitter_matches
        where
            regulations_comments_full.document_id = regulations_submitter_matches.document_id
            and entity_id = %s
            and docket_id = %s
        order by date_posted desc
        limit %s"""
