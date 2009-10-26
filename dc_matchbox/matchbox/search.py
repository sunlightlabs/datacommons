

from sql_utils import dict_union, is_disjoint, augment
from dcdata.contribution.models import sql_names as contribution_names
from matchbox.models import sql_names as matchbox_names
assert is_disjoint(contribution_names, matchbox_names)
sql_names = dict_union(contribution_names, matchbox_names)    

from normalizer import basic_normalizer

def entity_search(connection, query):
    """
    Search for all entities with a normalized name prefixed by the normalized query string.
    
    Returns an iterator over triples (id, name, count).
    """
    
    stmt = "select e.%(entity_id)s, e.%(entity_name)s, count(*) \
        from %(entity)s e inner join %(contribution)s c inner join %(normalization)s n\
        on e.%(entity_id)s = c.%(contribution_organization_entity)s and e.%(entity_name)s = n.%(normalization_original)s \
        where n.%(normalization_normalized)s like '%(query)s%%' \
        group by e.%(entity_id)s order by count(*) desc;" % \
        augment(sql_names, query=basic_normalizer(query))
    return _execute_stmt(connection, stmt)


transaction_result_columns = ['Contributor Name', 'Recipient Name', 'Amount', 'Date']

def transaction_search(connection, entity_id, result_columns=transaction_result_columns):
    """
    Search for all transactions that belong to a particular entity.
    
    Note: once transactions have donor and recipient entities in addition to employer entities
    this function will have to be adapted.
    """
    
    stmt = "select %(contribution_contributor_name)s, %(contribution_recipient_name)s, %(contribution_amount)s, %(contribution_datestamp)s \
            from %(contribution)s \
            where %(contribution_organization_entity)s = %(entity_id)s \
            order by %(contribution_amount)s desc" % \
            augment(sql_names, entity_id= int(entity_id))
    return _execute_stmt(connection, stmt)


def _execute_stmt(connection, stmt):
    cursor = connection.cursor()
    cursor.execute(stmt)
    return cursor