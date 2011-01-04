
from dcapi.aggregates.handlers import EntityTopListHandler

class OrgFedSpendingHandler(EntityTopListHandler):
    fields = ['recipient_name', 'type', 'fiscal_year', 'agency_name', 'description', 'amount']
    
    stmt = """
        select recipient_name, spending_type as type, fiscal_year, agency_name, description, amount
        from agg_spending_org
        where
            recipient_entity = %s
            and cycle = %s
        order by amount desc
        limit %s
    """