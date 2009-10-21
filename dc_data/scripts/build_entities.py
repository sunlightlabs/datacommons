

import MySQLdb


def quote(value):
    return value.replace("\\","\\\\").replace("'","\\'")


def populate_entities(connection, data_model):
    """
    Create the entities table based on transactional records.
    
    Uses the normalization table to find all unique names,
    then creates an entity for every unique name and links
    each matching transactional record to the entity.
    
    """
    
    cursor = connection.cursor()
    
    def retrieve_names():
        loop_cursor = connection.cursor()
        stmt = "select %(column_normalizations_original)s from %(table_normalizations)s" % data_model
        loop_cursor.execute(stmt)
        return loop_cursor
    
    def create_entity(name):
        params = {'name': quote(name)}
        params.update(data_model)
        stmt = "insert into `%(table_entities)s` (`%(column_entities_name)s`) values ('%(name)s')" % params
        cursor.execute(stmt)
        return connection.insert_id()
    
    def update_transactions(name, id):
        params = {'id': id, 'name': quote(name)}
        params.update(data_model)
        stmt = ("update `%(table_transactions)s` " + \
                "set `%(column_transactions_employer_id)s`='%(id)s' " + \
                "where `%(column_transactions_name)s` = '%(name)s'") % \
                params
        cursor.execute(stmt)
    
    for (name,) in retrieve_names():
        if name:
            print("creating entity '%s'" % name)
            id = create_entity(name)
            update_transactions(name, id)
    
    