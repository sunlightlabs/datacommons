
from dcapi.aggregates.queries import execute_top, execute_one


search_stmt = """
    select e.id, e.name, e.type, a.contributor_count, a.recipient_count, a.contributor_amount, a.recipient_amount
    from matchbox_entity e
    join agg_entities a 
        on e.id = a.entity_id
    where 
        a.cycle = -1
        and to_tsvector('datacommons', e.name) @@ to_tsquery('datacommons', %s)
        and (a.contributor_count > 0 or a.recipient_count > 0)
"""


get_entity_totals_stmt = """
    select contributor_count, recipient_count, contributor_amount, recipient_amount
    from agg_entities e
    where
        entity_id = %s
        and cycle = %s
"""


def search_names(query):
    parsed_query = ' & '.join(query.split(' '))
    
    return execute_top(search_stmt, parsed_query)



def get_entity_totals(entity_id, cycle):
    result = execute_one(get_entity_totals_stmt, entity_id, cycle)
    
    if not result:
        return [0, 0, 0, 0]
    return result
