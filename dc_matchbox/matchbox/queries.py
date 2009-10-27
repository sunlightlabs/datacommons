
from django.db import connection


from dcdata.utils.sql import dict_union, is_disjoint, augment
from dcdata.contribution.models import sql_names as contribution_names
from matchbox.models import sql_names as matchbox_names, Normalization
assert is_disjoint(contribution_names, matchbox_names)
sql_names = dict_union(contribution_names, matchbox_names)    

from strings.normalizer import basic_normalizer


def search_entities_by_name(query):
    """
    Search for all entities with a normalized name prefixed by the normalized query string.
    
    Returns an iterator over triples (id, name, count).
    """
    
    if query.strip():
        stmt = "select e.%(entity_id)s, e.%(entity_name)s, count(*) \
            from %(entity)s e inner join %(contribution)s c inner join %(normalization)s n\
            on e.%(entity_id)s = c.%(contribution_organization_entity)s and e.%(entity_name)s = n.%(normalization_original)s \
            where n.%(normalization_normalized)s like %%s \
            group by e.%(entity_id)s order by count(*) desc;" % \
            sql_names
        return _execute_stmt(stmt, basic_normalizer(query) + '%')
    else:
        return []

transaction_result_columns = ['Contributor Name', 'Reported Organization', 'Recipient Name', 'Amount', 'Date']

def search_transactions_by_entity(entity_id):
    """
    Search for all transactions that belong to a particular entity.
    
    Note: once transactions have donor and recipient entities in addition to employer entities
    this function will have to be adapted.
    """    
    stmt = "select %(contribution_contributor_name)s, %(contribution_organization_name)s, %(contribution_recipient_name)s, %(contribution_amount)s, %(contribution_datestamp)s \
            from %(contribution)s \
            where %(contribution_organization_entity)s = %%s \
            order by %(contribution_amount)s desc" % \
            sql_names
    return _execute_stmt(stmt, int(entity_id))


def merge_entities(entity_ids, new_entity):
    """
    Merge the given entity IDs into the new entity.
    
    Updates normalization table with normalized name of new entity,
    saves the new entity, updates the transactional records of old
    entities to point to new entity, and deletes the old entities.
    
    Arguments:
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
            set %(contribution_organization_entity)s = %%s \
            where %(contribution_organization_entity)s in (%(old_ids)s)" % \
            augment(sql_names, old_ids = old_ids_sql_string)
    _execute_stmt(stmt, new_entity.id)
    
    stmt = "delete from %(entity)s where %(entity_id)s in (%(old_ids)s)" % \
            augment(sql_names, old_ids = old_ids_sql_string)
    _execute_stmt(stmt)        
            
    return new_entity.id


def _execute_stmt(stmt, *args):
    cursor = connection.cursor()
    cursor.execute(stmt, args)
    return cursor
