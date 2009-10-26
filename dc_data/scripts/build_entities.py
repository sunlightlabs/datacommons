

from datetime import datetime

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from matchbox.models import Entity, entity_types, sql_names
from sql_utils import augment


def quote(value):
    return value.replace("\\","\\\\").replace("'","\\'")


def populate_entities(connection, transaction_table, entity_name_column, entity_id_column, 
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
        stmt = ("insert into `%(entity)s` (`%(entity_name)s`, `%(entity_type)s`, `%(entity_reviewer)s`, `%(entity_timestamp)s`, `%(entity_notes)s`) " + \
        "values ('%(name)s', '%(type)s', '%(reviewer)s', '%(timestamp)s', '')") % \
        augment(sql_names, name = quote(name), type=type, reviewer=quote(reviewer), timestamp=timestamp)
        cursor.execute(stmt)
        return connection.insert_id()

    def update_transactions(name, id):
        stmt = ("update `%s` set `%s`='%s' where `%s` = '%s'") % \
                (transaction_table, entity_id_column, id, entity_name_column, quote(name))
        cursor.execute(stmt)
    
    for (name,) in retrieve_names():
        if name:
            print("creating entity '%s'" % name)
            id = create_entity(name)
            update_transactions(name, id)
    

    