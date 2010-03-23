

from django.db import connection

# an experiment to see how we might discover the chnages between two versions of the database.
# not used, but keeping around as documentation of an approach we might someday take
# - epg

def edits(old_table, new_table, key_column, value_columns):
    """
    Compute the insert, update and delete operations needed to transform the old table into the new table.
    
    Return a triple (inserts, updates, deletes), where:
        inserts is an iterator over rows that should be inserted
        updates is an iterator over rows that should be updated
        deletes is an iterator over single tuples of ids that should be deleted
    For inserts and deletes, each row consists of the id followed by values for each value_column.
    """
    

    value_columns_string = ", ".join(map((lambda c: "new_table." + c), value_columns))
    value_inequalities = " or ".join(map((lambda c: "old_table.%s != new_table.%s" % (c, c)), value_columns))
    
    insertsCursor = connection.cursor()
    insertsCursor.execute("""select new_table.%(id)s, %(value_columns)s \
                        from %(old_table)s old_table \
                        right join %(new_table)s new_table \
                        on old_table.id = new_table.id \
                        where old_table.%(id)s is null""" % \
                        {'id': key_column, 'old_table': old_table, 'new_table': new_table, 
                         'value_columns': value_columns_string})
    
    deletesCursor = connection.cursor()
    deletesCursor.execute("""select old_table.%(id)s \
                        from %(old_table)s old_table \
                        left join %(new_table)s new_table \
                        on old_table.id = new_table.id \
                        where new_table.%(id)s is null""" % \
                        {'id': key_column, 'old_table': old_table, 'new_table': new_table})

    updatesCursor = connection.cursor()
    updatesCursor.execute("""select new_table.%(id)s, %(value_columns)s \
                        from %(old_table)s old_table \
                        inner join %(new_table)s new_table \
                        on old_table.%(id)s = new_table.%(id)s \
                        where %(value_inequalities)s""" % \
                    {'id': key_column,
                     'old_table': old_table,
                     'new_table': new_table,
                     'value_columns': value_columns_string,
                     'value_inequalities': value_inequalities})
    
    return (insertsCursor, updatesCursor, deletesCursor)


def update(old_table, new_table, id_column, value_columns):
    """
    Perform all necessary insertions, deletions and update statements in order to make old_table contain the same data as new_table.
    
    This would be a silly thing to do, except that the value_columns argument can be a subset of the actual columns in the table.
    This allows you to update some columns to the new data, while leaving other columns unchanged.
    """
    cursor = connection.cursor()
    
    (inserts, updates, deletes) = edits(old_table, new_table, id_column, value_columns)
    
    for values in inserts:
        values_string = ", ".join(map((lambda v: "'%s'" % v), values))
        cursor.execute("insert into %(old_table)s (%(id_column)s, %(value_columns)s) values (%(values)s)" % \
                       {'old_table': old_table, 
                        'id_column': id_column, 
                        'value_columns': ", ".join(value_columns),
                        'values': values_string})
        
    for row in updates:
        (id, values) = (row[0], row[1:])
        update_string = ", ".join(["%s = '%s'" % (column, value) for (column, value) in zip(value_columns, values)])
        cursor.execute("update %(old_table)s set %(updates)s where %(id_column)s = '%(id)s'" % \
                       {'old_table': old_table,
                        'updates': update_string,
                        'id_column': id_column,
                        'id': id})
        
    for (id,) in deletes:
        cursor.execute("delete from %(old_table)s where %(id_column)s = '%(id)s'" % \
                       {'old_table': old_table,
                        'id_column': id_column,
                        'id': id})
        
        
                                            
                                            
        
        
        
        
        