

from datetime import datetime

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.db import connection

from matchbox.models import Entity, entity_types , EntityAttribute, EntityAlias

def quote(value):
    return value.replace("\\","\\\\").replace("'","\\'")


def populate_entities(transaction_table, entity_name_column, entity_id_column, alias_columns, attribute_namespace, attribute_columns,
                      type=entity_types[0][0], reviewer=__name__, timestamp = datetime.now()):
    """
    Create the entities table based on transactional records.
    
    Uses the normalization table to find all unique names,
    then creates an entity for every unique name and links
    each matching transactional record to the entity.
    
    """
    
    cursor = connection.cursor()
    
    def retrieve_names():
        loop_cursor = connection.cursor()
        stmt = "select distinct `%s` from `%s`" % (entity_name_column, transaction_table)
        loop_cursor.execute(stmt)
        return loop_cursor
    
    def create_entity(name):
        e = Entity(name=name, type=type, reviewer=reviewer, timestamp=timestamp)
        e.save()
        
        # create aliases
        aliases = set()
        for alias_column in alias_columns:
            stmt = "select distinct `%s` from `%s` where `%s` = %%s" % \
                    (alias_column, transaction_table, entity_name_column)
            cursor.execute(stmt,[name])
            for (alias,) in cursor:
                aliases.add(alias)
        for alias in aliases:
            if alias.strip():
                e.aliases.add(EntityAlias(alias=alias))
            
        # create attributes
        attributes = set()
        for attribute_column in attribute_columns:
            stmt = "select distinct `%s` from `%s` where `%s` = %%s" % \
                    (attribute_column, transaction_table, entity_name_column)
            cursor.execute(stmt,[name])
            for (attribute,) in cursor:
                attributes.add(attribute)
        for attribute in attributes:
            if attribute.strip():
                e.attributes.add(EntityAttribute(namespace=attribute_namespace, value=attribute))
        
        return e.id



    def update_transactions(name, id):
        stmt = ("update `%s` set `%s`='%s' where `%s` = %%s") % \
                (transaction_table, entity_id_column, id, entity_name_column)
        cursor.execute(stmt, [name])
    
    for (name,) in retrieve_names():
        if name:
            print("creating entity '%s'" % name)
            id = create_entity(name)
            update_transactions(name, id)
    

    