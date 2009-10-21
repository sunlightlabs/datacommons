

import sys


def normalize(connection, source_columns, normalizer, dest_table='Normalizations', 
              dest_orig_column='Original', dest_norm_column='Normalized', out_file=sys.stdout):
    """
    Output SQL statements to populate a normalization table from the given columns.
    
    Arguments:
        connection -- a DB API connection
        source_columns -- a dictionary from table names to lists of column names
        normalizer -- a string mapping function
        dest_table -- the destination table name (default 'Normalization')
        dest_orig_column -- the column name for the original string (default 'Original')
        dest_norm_column -- the column name for the normalized column (default 'Normalized')
        out_file -- the file object to write to (default sys.stdout)
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
            add_column(cursor, table, column, source_names)
            
    for name in source_names:
        quoted_name = name.replace("\\","\\\\").replace("'","\\'")
        normalization = normalizer(name)
        quoted_normalization = normalization.replace("\\","\\\\").replace("'","\\'")
        stmt = "INSERT INTO `%s` (`%s`, `%s`) VALUES ('%s', '%s');\n" % \
                (dest_table, dest_orig_column, dest_norm_column, quoted_name, quoted_normalization)
        out_file.write(stmt)
        
        
    