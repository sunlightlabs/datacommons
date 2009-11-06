

from django.db import connection

def edits(old_table, new_table, key_column, value_columns):
    """
    Compute the insert, update and delete operations needed to transform the old table into the new table.
    
    Retuns a triple (inserts, updates, deletes), where:
        inserts is a list of keys of records that need to be inserted into the old table from the new table
        updates is a list of (key, update) pairs, where update is a list of new column values for the record
        deletes is a list of keys of records to delete from the old table
    """
    
    cursor = connection.cursor()
    
    cursor.execute("""select new.%(id)s \
                        from %(old_table)s old \
                        right join %(new_table)s new \
                        on old.id = new.id \
                        where old.%(id)s is null""" % \
                        {'id': key_column, 'old_table': old_table, 'new_table': new_table})
    inserts = [id for (id,) in cursor]
    
    cursor.execute("""select old.%(id)s \
                        from %(old_table)s old \
                        left join %(new_table)s new \
                        on old.id = new.id \
                        where new.%(id)s is null""" % \
                        {'id': key_column, 'old_table': old_table, 'new_table': new_table})
    deletes = [id for (id,) in cursor]
    
    value_columns_string = ", ".join(map((lambda c: "new." + c), value_columns))
    value_inequalities = " or ".join(map((lambda c: "old.%s != new.%s" % (c, c)), value_columns))
    cursor.execute("""select new.%(id)s, %(value_columns)s \
                        from %(old_table)s old \
                        inner join %(new_table)s new \
                        on old.%(id)s = new.%(id)s \
                        where %(value_inequalities)s""" % \
                    {'id': key_column,
                     'old_table': old_table,
                     'new_table': new_table,
                     'value_columns': value_columns_string,
                     'value_inequalities': value_inequalities})
    updates = [row for row in cursor]
    
    return (inserts, updates, deletes)