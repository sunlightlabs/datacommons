from dcapi.aggregates.handlers import EntityTopListHandler, PieHandler
import json


class TopEarmarksHandler(EntityTopListHandler):
    fields = ['fiscal_year', 'amount', 'description', 'members', 'recipients']
    
    stmt = """
        select fiscal_year, amount, description, members, recipients
        from agg_earmarks_by_amt_per_entity
        where
            entity_id = %s
            and cycle = %s
        order by amount desc, fiscal_year desc
        limit %s
    """
    
    def read(self, request, **kwargs):
        result = super(TopEarmarksHandler, self).read(request, **kwargs)
        
        # the member and recipient structures are stored in the database as JSON strings
        # need to load them here so that they can be properly interpreted by emitter
        for row in result:
            row['members'] = [json.loads(member) for member in row['members']]
            row['recipients'] = [json.loads(recipient) for recipient in row['recipients']]
        
        return result
    
    
class LocalEarmarksHandler(PieHandler):
    
    stmt = """
        select local, count, amount
        from agg_earmark_amt_by_entity_in_state_out_state
        where
            entity_id = %s
            and cycle = %s
    """