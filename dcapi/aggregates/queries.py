
# Simply utility functions used by other aggregates queries

from django.db import connection


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
