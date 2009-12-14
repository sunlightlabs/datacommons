

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'


from datetime import datetime
from matchbox.models import EntityAttribute, sql_names
from matchbox_scripts.build_matchbox import log


def quote(value):
    return value.replace("\\","\\\\").replace("'","\\'")


def populate_entities(transaction_table, entity_id_column, name_column, attribute_column,
                      type, reviewer=__name__, timestamp = datetime.now()):
    """
    Create the entities table based on transactional records.
    
    Uses the normalization table to find all unique names,
    then creates an entity for every unique name and links
    each matching transactional record to the entity.
    
    """
    
    from django.db import connection, transaction
    cursor = connection.cursor()
    
    def query_entity_data():
        loop_cursor = connection.cursor()
        stmt = """select %(entity)s, %(name)s, %(attribute)s 
                from %(table)s 
                where %(entity)s is not null 
                group by %(entity)s, %(name)s, %(attribute)s""" \
                % {'table': transaction_table,
                   'entity': entity_id_column,
                   'name': name_column,
                   'attribute': attribute_column}
        loop_cursor.execute(stmt)
        return loop_cursor
    
    def attribute_name_value_pair(attribute):
        attribute = attribute.strip()
        last_colon = attribute.rfind(":")
        if (last_colon >= 0):
            return (attribute[0:last_colon], attribute[last_colon + 1:])
        else:
            return None

    def create_entity(id, aliases, attributes):
        if not id:
            return

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
            
            name = aliases.__iter__().next() if len(aliases) > 0 else 'Unknown'
            
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
    prev_id = None
    names = set()
    attributes = set()
    
    for (id, name, attribute) in query_entity_data():            
        if prev_id != id:
            create_entity(prev_id, names, attributes)
            
            i += 1
            if i % 1000 == 0:
                transaction.commit()
                log("processed %d entities..." % i)
            
            prev_id = id
            names.clear()
            attributes.clear()

        if name:
            names.add(name)
        if attribute:
            (namespace, value) = attribute_name_value_pair(attribute) or ('', '')
            if namespace and value:
                attributes.add((namespace, value))

    create_entity(prev_id, names, attributes)
    
    transaction.commit()


    