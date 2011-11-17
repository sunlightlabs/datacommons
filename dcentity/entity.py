from dcentity.models import Entity, EntityAlias, EntityAttribute
from django.db import transaction


def build_entity(name, type, attributes):
    """ 
    Create an Entity and its associated aliases and attributes.
    
    Writes changes to DB but doesn't do any transaction management.
    """
    
    e = Entity.objects.create(name=name, type=type)
    
    EntityAlias.objects.create(entity=e, alias=name)
    
    for (namespace, value) in attributes:
        if namespace and value:
            EntityAttribute.objects.create(entity=e, namespace=namespace, value=value)


@transaction.commit_on_success()
def merge_entities(merge_ids, target_id):

    # error checking first: all entities exist and are of same type
    target = Entity.objects.get(id=target_id)
    if target_id in merge_ids:
        raise "Target entity should not be in merge entities."
    if len(merge_ids) != Entity.objects.filter(id__in=merge_ids, type=target.type).count():
        raise "All merge IDs must exist and be of same type as target."

    # update aliases
    aliases = EntityAlias.objects.filter(entity__in=merge_ids + [target_id])
    distinct_aliases = set([a.alias for a in aliases])

    aliases.delete()

    for alias in distinct_aliases:
        target.aliases.create(alias=alias)
        
    # update attributes
    attributes = EntityAttribute.objects.filter(entity__in=merge_ids + [target_id])
    distinct_attributes = set([(a.namespace, a.value) for a in attributes])

    attributes.delete()
    
    for (namespace, value) in distinct_attributes:
        target.attributes.create(namespace=namespace, value=value) 
    
    # add in old entity IDs
    for old_id in merge_ids:
        target.attributes.create(namespace=EntityAttribute.ENTITY_ID_NAMESPACE, value=old_id)
        
    # remove old entities
    Entity.objects.filter(id__in=merge_ids).delete()
