

from sql_utils import dict_union, is_disjoint, augment
from dcdata.contribution.models import sql_names as contribution_names
from matchbox.models import sql_names as matchbox_names, Normalization
assert is_disjoint(contribution_names, matchbox_names)
sql_names = dict_union(contribution_names, matchbox_names)    

from normalizer import basic_normalizer


def search_entities_by_name(connection, query):
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


transaction_result_columns = ['Contributor Name', 'Reported Organization', 'Recipient Name', 'Amount', 'Date']

def search_transactions_by_entity(connection, entity_id):
    """
    Search for all transactions that belong to a particular entity.
    
    Note: once transactions have donor and recipient entities in addition to employer entities
    this function will have to be adapted.
    """
    
    stmt = "select %(contribution_contributor_name)s, %(contribution_organization_name)s, %(contribution_recipient_name)s, %(contribution_amount)s, %(contribution_datestamp)s \
            from %(contribution)s \
            where %(contribution_organization_entity)s = %(entity_id)s \
            order by %(contribution_amount)s desc" % \
            augment(sql_names, entity_id= int(entity_id))
    return _execute_stmt(connection, stmt)


def merge_entities(connection, entity_ids, new_entity):
    """
    Merge the given entity IDs into the new entity.
    
    Updates normalization table with normalized name of new entity,
    saves the new entity, updates the transactional records of old
    entities to point to new entity, and deletes the old entities.
    
    Arguments:
    connection -- a DB connection
    entity_ids -- a list of entity IDs, as strings
    new_entity -- an Entity. Can be a Entity that is already in DB or a newly created entity.
    """
    
    for entity_id in entity_ids:
        assert isinstance(entity_id, int)
    
    old_ids_sql_string = ",".join(map(str, entity_ids))

    norm = Normalization(original = new_entity.name, normalized = basic_normalizer(new_entity.name))
    norm.save()
    
    new_entity.save()

    stmt = "update %(contribution)s \
            set %(contribution_organization_entity)s = %(new_id)s \
            where %(contribution_organization_entity)s in (%(old_ids)s)" % \
            augment(sql_names, old_ids = old_ids_sql_string, new_id = new_entity.id)
    _execute_stmt(connection, stmt)
    
    stmt = "delete from %(entity)s where %(entity_id)s in (%(old_ids)s)" % \
            augment(sql_names, old_ids = old_ids_sql_string)
    _execute_stmt(connection, stmt)        
            
    return new_entity.id


def _execute_stmt(connection, stmt):
    cursor = connection.cursor()
    cursor.execute(stmt)
    return cursor
