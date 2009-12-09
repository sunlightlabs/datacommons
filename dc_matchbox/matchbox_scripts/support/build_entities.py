

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.db import connection, transaction


from datetime import datetime
from matchbox.models import EntityAttribute, sql_names
from matchbox_scripts.build_matchbox import log


def quote(value):
    return value.replace("\\","\\\\").replace("'","\\'")


def populate_entities(transaction_table, entity_name_column, entity_id_column, alias_columns=[], attribute_columns=[],
                      type_func=(lambda cursor, id: None), reviewer=__name__, timestamp = datetime.now()):
    """
    Create the entities table based on transactional records.
    
    Uses the normalization table to find all unique names,
    then creates an entity for every unique name and links
    each matching transactional record to the entity.
    
    """
    
    cursor = connection.cursor()
    
    def retrieve_entity_ids():
        loop_cursor = connection.cursor()
        stmt = "select %s from %s group by %s" % (entity_id_column, transaction_table, entity_id_column)
        loop_cursor.execute(stmt)
        return loop_cursor
    
    def transactional_aliases(id):
        result = set()
        for alias_column in alias_columns:
            stmt = "select %s from %s where %s = %%s and length(%s) > 0 group by %s" % (alias_column, transaction_table, entity_id_column, alias_column, alias_column)
            cursor.execute(stmt,[id])
            for (alias,) in cursor:
                result.add(alias)
        return result   
    
    def transactional_attributes(id):
        result = set()
        for attribute_column in attribute_columns:
            stmt = "select %s from %s where %s = %%s and length(%s) > 0 group by %s" % (attribute_column, transaction_table, entity_id_column, attribute_column, attribute_column)
            cursor.execute(stmt,[id])
            for (attribute,) in cursor:
                (namespace, value) = attribute_name_value_pair(attribute) or ('', '')
                if namespace and value:
                    result.add((namespace, value))
        return result      

    def get_a_name(id):
        stmt = "select %s from %s where %s = %%s and length(%s) > 0 limit 1" % (entity_name_column, transaction_table, entity_id_column, entity_name_column)
        cursor.execute(stmt, [id])
        if cursor.rowcount:
            return cursor.fetchone()[0]
        else:
            return 'Unknown'
    
    def attribute_name_value_pair(attribute):
        attribute = attribute.strip()
        last_colon = attribute.rfind(":")
        if (last_colon >= 0):
            return (attribute[0:last_colon], attribute[last_colon + 1:])
        else:
            return None

    def create_entity(id):
        aliases = transactional_aliases(id)
        attributes = transactional_attributes(id)

        stmt = 'select 1 from %s where %s = %%s' % (sql_names['entity'], sql_names['entity_id'])
        cursor.execute(stmt, [id])
        if cursor.rowcount:
            # don't re-add existing aliases and attributes
            stmt = 'select %s from %s where %s = %%s' % (sql_names['entityalias_alias'], sql_names['entityalias'], sql_names['entityalias_entity'])
            cursor.execute(stmt, [id])
            aliases -= set([alias for (alias,) in cursor])

            stmt = 'select %s, %s from %s where %s = %%s' % \
                (sql_names['entityattribute_namespace'], sql_names['entityattribute_value'], sql_names['entityattribute'], sql_names['entityattribute_entity'])
            cursor.execute(stmt, [id])
            attributes -= set([(namespace, value) for (namespace, value) in cursor])

        else:
            attributes.add((EntityAttribute.ENTITY_ID_NAMESPACE, id))
            
            name = get_a_name(id)
            type = type_func(cursor, id)
            
            stmt = 'insert into %s (%s, %s, %s, %s, %s) values (%%s, %%s, %%s, %%s, %%s)' % \
                (sql_names['entity'], sql_names['entity_id'], sql_names['entity_name'], sql_names['entity_type'], sql_names['entity_reviewer'], sql_names['entity_timestamp'])
            
            cursor.execute(stmt, [id, name, type, reviewer, timestamp])
            
        for alias in aliases:
            stmt = 'insert into %s (%s, %s) values (%%s, %%s)' % (sql_names['entityalias'], sql_names['entityalias_entity'], sql_names['entityalias_alias'])
            cursor.execute(stmt, [id, alias])
            
        for (namespace, value) in attributes:
            stmt = 'insert into %s (%s, %s, %s) values (%%s, %%s, %%s)' % \
                (sql_names['entityattribute'], sql_names['entityattribute_entity'], sql_names['entityattribute_namespace'], sql_names['entityattribute_value'])
            cursor.execute(stmt, [id, namespace, value])
            

    i = 0
    for (id,) in retrieve_entity_ids():            
        if id:
            create_entity(id)
            
            i += 1
            if i % 1000 == 0:
                transaction.commit()
                log("processed %d entities..." % i)
    
    transaction.commit()


    