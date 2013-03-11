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
            help='Create partitions for the whole set of FEC tables'
        ),
        make_option('-t', '--table',
            action='store',
            dest='table',
            help='Table to create partition for'
        ),
        make_option('-c', '--cycle',
            action='store',
            dest='cycle',
            default=settings.LATEST_CYCLE,
            help='Cycle to create partition for'
        ),
    )

    @transaction.commit_on_success
    def handle(self, *args, **kwargs):
        """
        Takes a relation name and a cycle and creates a partition for it.
        Current relation names for FEC data are:
            fec_indiv*
            fec_pac2cand*
            fec_pac2pac*
            fec_committees
            fec_candidates*
            fec_candidate_summaries
            fec_committee_summaries
        """

        cycle = kwargs['cycle']

        if kwargs['all_tables']:
            for table in INDEX_COLS_BY_TABLE_FEC.keys():
                self.create_partition(cycle, table)
        elif kwargs['table']:
            self.create_partition(cycle, kwargs['table'])
        else:
            if kwargs['table'] is None:
                raise CommandError("You must specify a table")

    def create_partition(self, cycle, base_table):
        partition_name = '{}_{}'.format(base_table, cycle[-2:])

        if len(cycle) < 4:
            if int(cycle) > 80:
                cycle = '19' + cycle
            else:
                cycle = '20' + cycle

        create_stmt = """
            create table {} (
                check ( cycle = {} )
            ) inherits ({})
        """.format(partition_name, cycle, base_table)
        print create_stmt

        c = connections['default'].cursor()
        c.execute(create_stmt)

        for colname in INDEX_COLS_BY_TABLE_FEC[base_table]:
            idx_stmt = 'create index {0}__{1}_idx on {0} ({1})'.format(
                partition_name,
                colname
            )
            c.execute(idx_stmt)
