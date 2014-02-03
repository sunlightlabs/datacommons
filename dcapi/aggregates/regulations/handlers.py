from dcapi.aggregates.handlers import EntityTopListHandler, TopListHandler

class RegulationsTextHandler(EntityTopListHandler):
    
    fields = "agency docket year count title".split()
    
    stmt = """
        select agg_regulations_text.agency as agency, docket, cast(agg_regulations_text.year as int) as year, count, title
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
        select agg_regulations_submitter.agency as agency, docket, cast(agg_regulations_submitter.year as int) as year, count, title
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
        select document_id, title, type, date_posted, array_agg(object_id || ',' || file_type) as files
        from regulations_comments_full
        inner join regulations_text_matches using (document_id)
        where
            entity_id = %s
            and docket_id = %s
        group by document_id, title, type, date_posted
        order by date_posted desc, document_id desc
        limit %s"""
    
    def read(self, request, **kwargs):
        out = super(RegulationsDocketTextHandler, self).read(request, **kwargs)
        
        for result in out:
            result['files'] = [dict(zip(['object_id', 'file_type'], file.split(','))) for file in result['files']]
        
        return out

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


class TopRegsSubmittersHandler(TopListHandler):
    args = 'cycle limit'.split()
    fields = 'entity_id name count cycle'.split()

    stmt = """
        select entity_id, name, document_count, cycle
        from agg_regulations_text_totals
        inner join matchbox_entity on matchbox_entity.id = entity_id
        where
            cycle = %s
            and type = 'organization'
            and lower(name) not in ('network', 'impact', 'member')
        order by document_count desc
        limit %s
    """
