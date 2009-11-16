
from django.db import connection
import re

from dcdata.utils.sql import dict_union, is_disjoint, augment
from dcdata.contribution.models import sql_names as contribution_names
from matchbox.models import sql_names as matchbox_names, Normalization, EntityAlias, EntityAttribute, Entity
assert is_disjoint(contribution_names, matchbox_names)
sql_names = dict_union(contribution_names, matchbox_names)    

from strings.normalizer import basic_normalizer


def search_entities_by_name(query):
    """
    Search for all entities with a normalized name prefixed by the normalized query string.
    
    Returns an iterator over triples (id, name, count).
    """
    
    if query.strip():
        stmt = "select matches.%(entity_id)s, matches.%(entity_name)s, count(c.%(contribution_organization_entity)s) \
                from \
                (select distinct e.id, e.name \
                    from \
                        (select distinct %(normalization_original)s from %(normalization)s where %(normalization_normalized)s like %%s \
                         union distinct \
                        select distinct %(normalization_original)s from %(normalization)s where match(%(normalization_original)s) against(%%s in boolean mode)) n \
                    inner join %(entityalias)s a on a.%(entityalias_alias)s = n.%(normalization_original)s \
                    inner join %(entity)s e on e.%(entity_id)s = a.%(entityalias_entity)s) matches \
                left join %(contribution)s c on c.%(contribution_organization_entity)s = matches.%(entity_id)s \
                group by matches.%(entity_id)s order by count(c.%(contribution_organization_entity)s) desc;" % \
                sql_names
                 
        return _execute_stmt(stmt, basic_normalizer(query) + '%', _prepend_pluses(query))
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
    
    # a bit of type checking, since these will go into raw SQL
    #entity_ids = map(long, entity_ids)
    entity_ids = map(str, entity_ids)
    
    new_entity.save()
    assert(new_entity.id not in entity_ids)

    # make sure normalization exists for the new name
    norm = Normalization(original = new_entity.name, normalized = basic_normalizer(new_entity.name))
    norm.save()

    # update contribution foreign keys
    stmt = "update %(contribution)s \
            set %(contribution_organization_entity)s = %%s \
            where %(contribution_organization_entity)s in (%(old_ids)s)" % \
            augment(sql_names, old_ids = ",".join(map(lambda x: "'%s'" % x, entity_ids)))
    _execute_stmt(stmt, new_entity.id)
    
    # update alias and attribute tables
    _merge_aliases(entity_ids, new_entity)
    _merge_attributes(entity_ids, new_entity)

    # remove the old entity objects
    Entity.objects.filter(id__in=entity_ids).delete()
            
    return new_entity.id


def _merge_aliases(old_ids, new_entity):
    entity_ids = old_ids + [new_entity.id]
    existing_aliases = [entity_alias.alias for entity_alias in EntityAlias.objects.filter(entity__in=entity_ids)]
    existing_aliases.append(new_entity.name)
    
    EntityAlias.objects.filter(entity__in=entity_ids).delete()
    
    for alias in set(existing_aliases):
        new_entity.aliases.create(alias=alias)
    
    
def _merge_attributes(old_ids, new_entity):    
    entity_ids = old_ids + [new_entity.id]
    existing_attributes = [(attr.namespace, attr.value) for attr in EntityAttribute.objects.filter(entity__in=entity_ids)]
    existing_attributes.append((EntityAttribute.ENTITY_ID_NAMESPACE, new_entity.id))
    
    EntityAttribute.objects.filter(entity__in=entity_ids).delete()
    
    for (namespace, value) in set(existing_attributes):
        new_entity.attributes.create(namespace=namespace, value=value)
    
    


def _execute_stmt(stmt, *args):
    cursor = connection.cursor()
    cursor.execute(stmt, args)
    return cursor

NON_WHITESPACE_EXP = re.compile("\S+", re.U)
def _prepend_pluses(query):
    terms = NON_WHITESPACE_EXP.findall(query)
    return " ".join(["+" + term for term in terms])
