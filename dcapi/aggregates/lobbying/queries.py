
from dcapi.aggregates.queries import execute_top


get_top_registrants_for_client_stmt = """
    select registrant_name, registrant_entity, amount
    from agg_lobbying_registrants_for_client
    where
        client_entity = %s
        and cycle = %s
    order by amount desc
    limit %s
"""


get_top_issues_for_client_stmt = """
    select issue, count
    from agg_lobbying_issues_for_client
    where
        client_entity = %s
        and cycle = %s
    order by count desc
    limit %s
"""


get_top_lobbyists_for_client_stmt = """
    select lobbyist_name, lobbyist_entity, count
    from agg_lobbying_lobbyists_for_client
    where
        client_entity = %s
        and cycle = %s
    order by count desc
    limit %s    
"""


def get_top_registrants_for_client(org_id, cycle, limit):
    return execute_top(get_top_registrants_for_client_stmt, org_id, cycle, limit)

def get_top_issues_for_client(org_id, cycle, limit):
    return execute_top(get_top_issues_for_client_stmt, org_id, cycle, limit)

def get_top_lobbyists_for_client(org_id, cycle, limit):
    return execute_top(get_top_lobbyists_for_client_stmt, org_id, cycle, limit)

