
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from django.db import connection

import sys

from matchbox.models import Normalization, sql_names

def normalize(source_columns, normalizer):
    """
    Populate the normalizations table using normalizer on source_columns.
    
    Arguments:
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
    
    for (table, column_list) in source_columns:
        for column in column_list:
            add_column(cursor, sql_names[table], sql_names[column], source_names)
            
    for name in source_names:
        row = Normalization(original=name, normalized=normalizer(name))
        row.save()
        
        
    