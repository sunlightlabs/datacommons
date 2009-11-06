

from django.db import connection

def edits(old_table, new_table, key_column, value_columns):
    """
    Compute the insert, update and delete operations needed to transform the old table into the new table.
    
    Return a triple (inserts, updates, deletes), where:
        inserts is an iterator over rows that should be inserted
        updates is an iterator over rows that should be updated
        deletes is an iterator over single tuples of ids that should be deleted
    For inserts and deletes, each row consists of the id followed by values for each value_column.
    """
    

    value_columns_string = ", ".join(map((lambda c: "new." + c), value_columns))
    value_inequalities = " or ".join(map((lambda c: "old.%s != new.%s" % (c, c)), value_columns))
    
    insertsCursor = connection.cursor()
    insertsCursor.execute("""select new.%(id)s, %(value_columns)s \
                        from %(old_table)s old \
                        right join %(new_table)s new \
                        on old.id = new.id \
                        where old.%(id)s is null""" % \
                        {'id': key_column, 'old_table': old_table, 'new_table': new_table, 
                         'value_columns': value_columns_string})
    
    deletesCursor = connection.cursor()
    deletesCursor.execute("""select old.%(id)s \
                        from %(old_table)s old \
                        left join %(new_table)s new \
                        on old.id = new.id \
                        where new.%(id)s is null""" % \
                        {'id': key_column, 'old_table': old_table, 'new_table': new_table})

    updatesCursor = connection.cursor()
    updatesCursor.execute("""select new.%(id)s, %(value_columns)s \
                        from %(old_table)s old \
                        inner join %(new_table)s new \
                        on old.%(id)s = new.%(id)s \
                        where %(value_inequalities)s""" % \
                    {'id': key_column,
                     'old_table': old_table,
                     'new_table': new_table,
                     'value_columns': value_columns_string,
                     'value_inequalities': value_inequalities})
    
    return (insertsCursor, updatesCursor, deletesCursor)