
USE_RAW = False


import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

# to do: even in raw mode, should get DB name and other parameters from Djanog settings file.
# otherwise this script is broken when run in unit tests.
if USE_RAW:
    import MySQLdb
    connection = MySQLdb.Connect(host='localhost', db='datacommons', user='root')
else:
    from django.db import connection


from datetime import datetime
from matchbox.models import Entity, entity_types , EntityAttribute, EntityAlias, sql_names

def quote(value):
    return value.replace("\\","\\\\").replace("'","\\'")


def populate_entities(transaction_table, entity_name_column, entity_id_column, alias_columns=[], attribute_columns=[],
                      type_=None, reviewer=__name__, timestamp = datetime.now()):
    """
    Create the entities table based on transactional records.
    
    Uses the normalization table to find all unique names,
    then creates an entity for every unique name and links
    each matching transactional record to the entity.
    
    """
    
    cursor = connection.cursor()
    
    def retrieve_entity_ids():
        loop_cursor = connection.cursor()
        stmt = "select distinct `%s` from `%s`" % (entity_id_column, transaction_table)
        loop_cursor.execute(stmt)
        return loop_cursor
    
    def retrieve_names(id):
        stmt = "select distinct `%s` from `%s` where `%s` = %%s" % (entity_name_column, transaction_table, entity_id_column)
        cursor.execute(stmt, [id])
        return [name.strip() for (name,) in cursor if name.strip()]
    
    def retrieve_attributes(id):
        result = set()
        for attribute_column in attribute_columns:
            stmt = "select distinct `%s` from `%s` where `%s` = %%s" % (attribute_column, transaction_table, entity_id_column)
            cursor.execute(stmt,[id])
            for (attribute,) in cursor:
                (namespace, value) = attribute_name_value_pair(attribute) or ('', '')
                if namespace and value:
                    result.add((namespace, value))
        return result      
    
    def attribute_name_value_pair(attribute):
        attribute = attribute.strip()
        last_colon = attribute.rfind(":")
        if (last_colon >= 0):
            return (attribute[0:last_colon], attribute[last_colon + 1:])
        else:
            return None
    
    def create_entity(id):
        aliases = retrieve_names(id) or ['Unknown']
        
        e = Entity(id=id, name=aliases[0], type=type_, reviewer=reviewer, timestamp=timestamp)
        e.save()
        
        for alias in aliases:
            e.aliases.add(EntityAlias(alias=alias))
            
        e.attributes.create(namespace=EntityAttribute.ENTITY_ID_NAMESPACE, value=e.id)
        for (namespace, value) in retrieve_attributes(id):
            e.attributes.add(EntityAttribute(namespace=namespace, value=value))
        
        return e.id

    
    for (id,) in retrieve_entity_ids():
        if id:
            create_entity(id)
    

    