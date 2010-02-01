import time

from django.db.models import Q
from django.db import connection
import re

from dcdata.utils.sql import dict_union, is_disjoint
from dcdata.contribution.models import sql_names as contribution_names, Contribution
from matchbox.models import sql_names as matchbox_names, Normalization, EntityAlias, EntityAttribute, Entity, entityref_cache, EntityNote
assert is_disjoint(contribution_names, matchbox_names)
sql_names = dict_union(contribution_names, matchbox_names)    

from strings.normalizer import basic_normalizer

# todo use the global logger and debug settings
DEBUG_SEARCH = True

def search_entities_by_name(query, type_filter=[]):
    """
    Search for all entities with a normalized name prefixed by the normalized query string.
    
    Returns an iterator over triples (id, name, count, total_amount).
    """
    
    start_time = time.time()
    if DEBUG_SEARCH:
        print("Entity search for ('%s', '%s') beginning..." % (query, type_filter))
    
    if query.strip():
        type_clause = "where " + " or ".join(["e.type = '%s'" % type for type in type_filter]) if type_filter else ""
        
        stmt = """
                select distinct e.id, e.name, e.contribution_count, e.contribution_amount 
                from                                 
                    (select distinct original from matchbox_normalization where normalized like %%s 
                    union distinct                                 
                    select distinct original from matchbox_normalization where to_tsvector('simple', original) @@ to_tsquery('simple', %%s)
                    limit 1000) n                             
                    inner join matchbox_entityalias a on a.alias = n.original                             
                    inner join matchbox_entity e on e.id = a.entity_id                             
                    %s
                order by e.contribution_count desc;
                """ % type_clause
        
        cursor = connection.cursor()
        cursor.execute(stmt, [basic_normalizer(query) + '%', ' & '.join(query.split(' '))])
        
        runtime = time.time() - start_time
        if DEBUG_SEARCH:
            result = list(cursor)
            print("Entity search for ('%s', '%s') returned %d results in %f seconds." % (query, type_filter, len(result), runtime))
            return result
        
        return cursor         
    else:
        return []



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
    
    new_entity.save()
    assert(new_entity.id not in entity_ids)

    # make sure normalization exists for the new name
    norm = Normalization(original = new_entity.name, normalized = basic_normalizer(new_entity.name))
    norm.save()

    # update transactions
    for entity_field in entityref_cache.get(Contribution, None):
        query = reduce(lambda x, y: x | y, [Q(**{entity_field: old_id}) for old_id in entity_ids])
        Contribution.objects.filter(query).update(**{entity_field: new_entity.id})
    
    # update alias and attribute tables
    _merge_aliases(entity_ids, new_entity)
    _merge_attributes(entity_ids, new_entity)
    _merge_notes(entity_ids, new_entity)

    # remove the old entity objects
    Entity.objects.filter(id__in=entity_ids).delete()
            
    return new_entity.id

def _merge_notes(old_ids, new_entity):
    notes = EntityNote.objects.filter(entity__in=old_ids)
    for note in notes:
        new_entity.notes.add(note)

def _merge_aliases(old_ids, new_entity):
    entity_ids = list(old_ids)
    entity_ids.append(new_entity) 
    existing_aliases = [entity_alias.alias for entity_alias in EntityAlias.objects.filter(entity__in=entity_ids)]
    existing_aliases.append(new_entity.name)
    
    EntityAlias.objects.filter(entity__in=entity_ids).delete()
    
    for alias in set(existing_aliases):
        new_entity.aliases.create(alias=alias)
    
    
def _merge_attributes(old_ids, new_entity):    
    entity_ids = list(old_ids)
    entity_ids.append(new_entity) 
    existing_attributes = [(attr.namespace, attr.value) for attr in EntityAttribute.objects.filter(entity__in=entity_ids)]
    existing_attributes.append((EntityAttribute.ENTITY_ID_NAMESPACE, new_entity.id))
    
    EntityAttribute.objects.filter(entity__in=entity_ids).delete()
    
    for (namespace, value) in set(existing_attributes):
        new_entity.attributes.create(namespace=namespace, value=value)
    
    
NON_WHITESPACE_EXP = re.compile("\S+", re.U)
def _prepend_pluses(query):
    terms = NON_WHITESPACE_EXP.findall(query)
    return " ".join(["+" + term for term in terms])
