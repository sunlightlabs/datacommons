from django.core.management.base import CommandError, BaseCommand
from django.db import connections, transaction

from commando import command, true, store
from django.conf import settings


class Command(BaseCommand):
    @command(description='Create partitions (by cycle) for FEC tables.')
    @true('-T', '--all-tables', dest='all_tables', default=False,                 help="Create partitions for the whole set of FEC tables")
    @store('-t', '--table',     dest='table',      default=None,                  help="Table to create partition for")
    @store('-c', '--cycle',     dest='cycle',      default=settings.LATEST_CYCLE, help="Table to create partition for", required=True)

    # TODO
    #@store('-C', '--all-cycles', default=False, help="Create partitions for all cycles")

    idx_cols_by_table = {
        'fec_indiv':      ['filer_id'],
        'fec_candidates': [],
        'fec_pac2cand':   ['candidate_id', 'other_id'],
        'fec_pac2pac':    ['filer_id', 'other_id'],
        'fec_committees': [],
        'fec_candidates': [],
        'fec_candidate_summaries': [],
        'fec_committee_summaries': [],
    }

    @transaction.commit_on_success
    def handle(self, params):
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

        cycle = params.cycle

        if params.all_tables:
            for table in self.idx_cols_by_table.keys():
                self.create_partition(cycle, table)
        elif params.table:
            self.create_partition(cycle, params.table)
        else:
            if params.table is None:
                raise CommandError("You must specify a table")

    def create_partition(self, cycle, base_table):
        partition_name = '{}_{}'.format(base_table, cycle[-2:])

        create_stmt = """
            create table {} (
                check ( cycle = {} )
            ) inherits ({})
        """.format(partition_name, cycle, base_table)
        print create_stmt

        c = connections['default'].cursor()
        c.execute(create_stmt)

        for colname in self.idx_cols_by_table[base_table]:
            idx_stmt = 'create index {0}__{1}_idx on {0} ({1})'.format(
                partition_name,
                colname
            )
            c.execute(idx_stmt)
