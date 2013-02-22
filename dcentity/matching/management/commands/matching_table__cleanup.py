from django.core.management.base import CommandError, BaseCommand
from django.db import connections, transaction


class Command(BaseCommand):

    @transaction.commit_on_success
    def handle(self, *args, **kwargs):
        table_prefix = args[-1]

        cursor = connections['default'].cursor()
        cursor.execute('select tablename from pg_catalog.pg_tables where tablename ilike %s order by tablename desc', (table_prefix + '_%',))
        tables = cursor.fetchall()
        print "Tables found:"
        print tables

        if len(tables) > 1:
            for table in [ x[0] for x in tables[1:] ]:
                cursor.execute('drop table {}'.format(table), None)

            print "Dropped {} tables.".format(len(tables) - 1)
        else:
            print "Not enough tables found to operate on. (Must have more than one.)"




