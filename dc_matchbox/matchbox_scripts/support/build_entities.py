
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
                last_colon = attribute.rfind(":")
                if (last_colon >= 0):
                    e.attributes.add(EntityAttribute(namespace=attribute[0:last_colon], value=attribute[last_colon + 1:]))
        
        return e.id

    def create_entity_raw(name):
        stmt = "insert into `%(entity)s` \
                (`%(entity_name)s`, `%(entity_type)s`, `%(entity_reviewer)s`, `%(entity_timestamp)s`, `%(entity_notes)s`) \
                values (%%s, %%s, %%s, %%s, %%s)" % \
                sql_names
        cursor.execute(stmt, [name, type, reviewer, timestamp, ''])
        entity_id = connection.insert_id()
        
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
                stmt = "insert into `%(entityalias)s` \
                        (`%(entityalias_entity)s`, `%(entityalias_alias)s`) \
                        values (%%s, %%s)" % \
                        sql_names
                cursor.execute(stmt,[entity_id, alias])
            
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
                stmt = "insert into `%(entityattribute)s` \
                        (`%(entityattribute_entity)s`, `%(entityattribute_namespace)s`, `%(entityattribute_value)`) \
                        values (%%s, %%s, %%s)" % \
                        sql_names
                cursor.execute(stmt,[entity_id, attribute_namespace, attribute])
        
        return entity_id


    def update_transactions(name, id):
        stmt = ("update `%s` set `%s`='%s' where `%s` = %%s") % \
                (transaction_table, entity_id_column, id, entity_name_column)
        cursor.execute(stmt, [name])
    
    for (name,) in retrieve_names():
        if name:
            #print("creating entity '%s'" % name)
            id = create_entity_raw(name) if USE_RAW else create_entity(name)
            update_transactions(name, id)
    

    