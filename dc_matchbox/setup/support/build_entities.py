

from datetime import datetime

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.db import connection

from matchbox.models import Entity, entity_types 

def quote(value):
    return value.replace("\\","\\\\").replace("'","\\'")


def populate_entities(transaction_table, entity_name_column, entity_id_column, 
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
        stmt = "select distinct `%s` from `%s` limit 100" % (entity_name_column, transaction_table)
        loop_cursor.execute(stmt)
        return loop_cursor
    
    def create_entity(name):
        e = Entity(name=name, type=type, reviewer=reviewer, timestamp=timestamp)
        e.save()
        return e.id



    def update_transactions(name, id):
        stmt = ("update `%s` set `%s`='%s' where `%s` = '%s'") % \
                (transaction_table, entity_id_column, id, entity_name_column, quote(name))
        cursor.execute(stmt)
    
    for (name,) in retrieve_names():
        if name:
            print("creating entity '%s'" % name)
            id = create_entity(name)
            update_transactions(name, id)
    

    