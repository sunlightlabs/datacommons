

import sys

from matchbox.models import Normalization
from dcdata.contribution.models import sql_names

def normalize(connection, source_columns, normalizer):
    """
    Populate the normalizations table using normalizer on source_columns.
    
    Arguments:
        connection -- a DB API connection
        source_columns -- a dictionary from table names to lists of column names
        normalizer -- a string mapping function
    """
    
    def add_column(cursor, source_table, source_column, result_set):
        """ Add all strings from the given column to result_set. """
        
        stmt = "select distinct %(column)s from %(table)s" % \
                {'column': source_column, 'table': source_table}
        cursor.execute(stmt)
        for row in cursor:
            assert len(row) == 1
            try:
                result_set.add(row[0].decode('utf_8'))
            except UnicodeDecodeError:
                sys.stderr.write("Could not decode string '%s'. Skipping string.\n" % (row[0],))


    cursor = connection.cursor()
    source_names = set()
    
    # to do: when loading the resulting SQL into the DB we're getting lots of duplicate warnings.
    # this is probably because the source_name set is case sensitive, whereas the DB is case insensitive.
    # should probably lowercase every string before adding to source_names. 
    
    for (table, column_list) in source_columns:
        for column in column_list:
            add_column(cursor, sql_names[table], sql_names[column], source_names)
            
    for name in source_names:
        row = Normalization(original=name, normalized=normalizer(name))
        row.save()
        
        
    