
# Simply utility functions used by other aggregates queries

from django.db import connection

# at the database level -1 is used to indicate summation over all cycles
ALL_CYCLES = '-1'

def search_names(query, entity_types=[]):
    # entity_types is not currently used but we'll build it in at some
    # point...

    # do some freaky stuff to quote the query in case it contains
    # special characters.
    query_items = ['"'+item+'"' for item in query.split(' ')]
    parsed_query = ' & '.join(query_items)
    
    return _execute_top(search_stmt, parsed_query)
=======
DEFAULT_LIMIT = '10'
DEFAULT_CYCLE = ALL_CYCLES


def execute_one(stmt, *args):
    cursor = connection.cursor()
    cursor.execute(stmt, args)
    return cursor.fetchone()

def execute_top(stmt, *args):
    cursor = connection.cursor()
    cursor.execute(stmt, args)
    return list(cursor)

def execute_pie(stmt, *args):
    result_rows = execute_top(stmt, *args)
    return dict([(party, (count, amount)) for (party, count, amount) in result_rows])
