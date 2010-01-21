from strings.normalizer import basic_normalizer

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from django.db import connection, transaction

import sys
import csv

from matchbox.models import Normalization
from matchbox_scripts.build_matchbox import log





def normalize(source_table, source_column, normalizer):
    """
    Populate the normalizations table using normalizer on source_columns.
    
    Arguments:
        source_columns -- a dictionary from table names to lists of column names
        normalizer -- a string mapping function
    """
    
    def add_column(cursor, source_table, source_column, result_set):
        """ Add all strings from the given column to result_set. """
        

        for row in cursor:
            assert len(row) == 1
            try:
                result_set.add(row[0].decode('utf_8'))
            except UnicodeDecodeError:
                sys.stderr.write("Could not decode string '%s'. Skipping string.\n" % (row[0],))


    cursor = connection.cursor()
    
    stmt = "select %(column)s from %(table)s group by %(column)s" % \
                {'column': source_column, 'table': source_table}
    cursor.execute(stmt)
            
    i = 0
    for row in cursor:
        name = row[0].decode('utf_8') 
        row = Normalization(original=name, normalized=normalizer(name))
        row.save()
        
        i += 1
        if i % 1000 == 0:
            transaction.commit()
            log("processed %d normalizations..." % i)   
    
    transaction.commit()         
        
        
    