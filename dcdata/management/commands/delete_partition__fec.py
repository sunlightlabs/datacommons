from django.core.management.base import CommandError, BaseCommand
from django.db import connections, transaction
from optparse import make_option
from django.conf import settings
from dcdata.fec.config import INDEX_COLS_BY_TABLE_FEC


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-T', '--all-tables',
            action='store_true',
            dest='all_tables',
            default=False,
            help='Delete partitions for the whole set of FEC tables (for the specified cycle)'
        ),
        make_option('-t', '--table',
            action='store',
            dest='table',
            help='Table to delete partition for'
        ),
        make_option('-c', '--cycle',
            action='store',
            dest='cycle',
            default=settings.LATEST_CYCLE,
            help='Cycle to delete partition for'
        ),
    )

    @transaction.commit_on_success
    def handle(self, *args, **kwargs):
        """
        Takes a relation name and a cycle and deletes its partition.
        (Usually with the assumption that it will be recreated for
        a fresh data load.)
        """

        all_tables = kwargs['all_tables']
        base_table = kwargs['table']
        cycle = kwargs['cycle']

        if cycle is None:
            raise CommandError("You must specify a cycle")

        if all_tables:
            for table in INDEX_COLS_BY_TABLE_FEC.keys():
                self.delete_partition(cycle, table)
        elif base_table:
            self.delete_partition(cycle, base_table)
        else:
            raise CommandError("You must specify a table (-t) or all tables (-T).")

    def delete_partition(self, cycle, table):
        partition_name = '{}_{}'.format(table, cycle[-2:])

        drop_stmt = """
            drop table if exists {}
        """.format(partition_name)
        print drop_stmt

        c = connections['default'].cursor()
        c.execute(drop_stmt)
