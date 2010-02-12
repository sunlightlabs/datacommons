import time

from django.db.models import Q
from django.db import connection, transaction
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


def _pairs_to_dict(pairs):
    result = dict()
    for (key, value) in pairs:
        result.setdefault(key, set()).add(value)
        
    return result


def associate_transactions(entity_id, column, transactions):
    transaction.set_dirty()
    cursor = connection.cursor()
    
    # make sure we update any entities that the transactions already belonged to
    disassociate_transactions(column, transactions)
    
    for (namespace, ids) in _pairs_to_dict(transactions).iteritems():
        contribution_update_stmt = """
            update contribution_contribution
            set %s = %%s
            where transaction_namespace = %%s
                and transaction_id in %s
        """ % (column, "(%s)" % ", ".join(['%s'] * len(ids)))
        cursor.execute(contribution_update_stmt, [entity_id, namespace] + list(ids))
        
    recompute_aggregates(entity_id)
    

def disassociate_transactions(column, transactions):
    transaction.set_dirty()
    cursor = connection.cursor()
    
    updated_entities = set()
    
    for (namespace, ids) in _pairs_to_dict(transactions).iteritems():
        # find all entities that will change
        entity_stmt = """
            select %s
            from contribution_contribution
            where transaction_namespace = %%s
                and transaction_id in %s
                and %s != ''
        """ % (column, "(%s)" % ", ".join(['%s'] * len(ids)), column)
        cursor.execute(entity_stmt, [namespace] + list(ids))
        if cursor.rowcount > 0:
            updated_entities |= set([id for (id) in cursor])
          
            # remove entity references from transactions    
            contribution_update_stmt = """
                update contribution_contribution
                set %s = ''
                where transaction_namespace = %%s
                    and transaction_id in %s
            """ % (column, "(%s)" % ", ".join(['%s'] * len(ids)))
            cursor.execute(contribution_update_stmt, [namespace] + list(ids))
       
    for id in updated_entities:
        recompute_aggregates(id)   
    
    
def recompute_aggregates(entity_id):
    cursor = connection.cursor()
    
    aggregate_count_stmt = """
        update matchbox_entity set contribution_count = (
            select count(*) from contribution_contribution 
            where contributor_entity = matchbox_entity.id
                or organization_entity = matchbox_entity.id
                or parent_organization_entity = matchbox_entity.id
                or committee_entity = matchbox_entity.id
                or recipient_entity = matchbox_entity.id)
        where id = %s
    """
    cursor.execute(aggregate_count_stmt, [entity_id])
    
    aggregate_amount_stmt = """
        update matchbox_entity set contribution_amount = (
            select sum(amount) from contribution_contribution
            where contributor_entity = matchbox_entity.id
                or organization_entity = matchbox_entity.id
                or parent_organization_entity = matchbox_entity.id
                or committee_entity = matchbox_entity.id
                or recipient_entity = matchbox_entity.id)
        where id = %s
    """
    cursor.execute(aggregate_amount_stmt, [entity_id])
    
    _recompute_aliases(entity_id)
    _recompute_attributes(entity_id)


def _recompute_aliases(entity_id):    
    cursor = connection.cursor()
    
    delete_aliases_stmt = """
        delete from matchbox_entityalias
        where entity_id = %s
        and verified = FALSE
    """
    cursor.execute(delete_aliases_stmt, [entity_id])
    
    aggregate_aliases_stmt = """
        insert into matchbox_entityalias (entity_id, alias, verified)
        select * from (
                select contributor_entity as id, contributor_name as alias, FALSE as verified
                from contribution_contribution
                where contributor_entity = %s
                    and contributor_name != ''
                group by contributor_entity, contributor_name
            union
                select organization_entity, organization_name, FALSE
                from contribution_contribution
                where organization_entity = %s
                    and organization_name != ''
                group by organization_entity, organization_name
            union
                select organization_entity, contributor_employer, FALSE
                from contribution_contribution
                where organization_entity = %s
                    and contributor_employer != ''
                group by organization_entity, contributor_employer
            union
                select parent_organization_entity, parent_organization_name, FALSE
                from contribution_contribution
                where parent_organization_entity = %s
                    and parent_organization_name != ''
                group by parent_organization_entity, parent_organization_name, FALSE
            union
                select committee_entity, committee_name, FALSE
                from contribution_contribution
                where committee_entity = %s
                    and committee_name != ''
                group by committee_entity, committee_name
            union
                select recipient_entity, recipient_name, FALSE
                from contribution_contribution
                where recipient_entity = %s
                    and recipient_name != ''
                group by recipient_entity, recipient_name
            ) inserts
        where not exists 
            (select 1 from matchbox_entityalias a
            where
                a.entity_id = inserts.id
            and a.alias = inserts.alias)
    """  
    cursor.execute(aggregate_aliases_stmt, [entity_id] * 6)
    
    
def _recompute_attributes(entity_id):    
    cursor = connection.cursor()
    
    # re-compute attribute aggregates
    delete_attributes_stmt = """
        delete from matchbox_entityattribute
        where entity_id = %s
        and verified = FALSE
    """
    cursor.execute(delete_attributes_stmt, [entity_id])
    
    subquery_prototype = """
        select 
            %(role)s_entity as id, 
            case 
                when transaction_namespace = 'urn:fec:transaction' then 'urn:crp:%(role)s' 
                when transaction_namespace = 'urn:nimsp:transaction' then 'urn:nimsp:%(role)s'
                when transaction_namespace = 'urn:unittest:transaction' then 'urn:unittest:%(role)s'
            end as namespace,
            %(role)s_ext_id as value,
            FALSE as verified
        from contribution_contribution
        where
            %(role)s_entity = %%s
            and %(role)s_ext_id != ''
        group by %(role)s_entity, transaction_namespace, %(role)s_ext_id
        """
        
    contribution_subqueries = " union ".join(subquery_prototype % {'role': role} for role in ['contributor', 'organization', 'parent_organization', 'committee', 'recipient'])

    aggregate_attributes_stmt = """ 
        insert into matchbox_entityattribute (entity_id, namespace, value, verified) 
        select * 
        from (%s) inserts
        where not exists
            (select 1 from matchbox_entityattribute a
            where
                a.entity_id = inserts.id
            and a.namespace = inserts.namespace
            and a.value = inserts.value)
    """ % (contribution_subqueries)

    cursor.execute(aggregate_attributes_stmt, [entity_id] * 5)


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
    verified_aliases = [entity_alias.alias for entity_alias in EntityAlias.objects.filter(entity__in=entity_ids, verified=True)]
    verified_aliases.append(new_entity.name)
    
    unverified_aliases = [entity_alias.alias for entity_alias in EntityAlias.objects.filter(entity__in=entity_ids, verified=False)]
    
    EntityAlias.objects.filter(entity__in=entity_ids).delete()
    
    for alias in set(verified_aliases):
        new_entity.aliases.create(alias=alias, verified=True)

    for alias in set(unverified_aliases):
        if alias not in verified_aliases:
            new_entity.aliases.create(alias=alias, verified=False)
    
    
def _merge_attributes(old_ids, new_entity):    
    entity_ids = list(old_ids)
    entity_ids.append(new_entity) 
    verified_attributes = [(attr.namespace, attr.value) for attr in EntityAttribute.objects.filter(entity__in=entity_ids, verified=True)]
    verified_attributes.append((EntityAttribute.ENTITY_ID_NAMESPACE, new_entity.id))
    
    unverified_attributes = [(attr.namespace, attr.value) for attr in EntityAttribute.objects.filter(entity__in=entity_ids, verified=False)]
    
    EntityAttribute.objects.filter(entity__in=entity_ids).delete()
    
    for (namespace, value) in set(verified_attributes):
        new_entity.attributes.create(namespace=namespace, value=value, verified=True)
        
    for (namespace, value) in set(unverified_attributes):
        if (namespace, value) not in verified_attributes:
            new_entity.attributes.create(namespace=namespace, value=value, verified=False)
    
    
NON_WHITESPACE_EXP = re.compile("\S+", re.U)
def _prepend_pluses(query):
    terms = NON_WHITESPACE_EXP.findall(query)
    return " ".join(["+" + term for term in terms])
