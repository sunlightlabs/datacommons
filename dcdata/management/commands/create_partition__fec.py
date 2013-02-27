from django.core.management.base import CommandError, BaseCommand
from django.db import connections, transaction


class Command(BaseCommand):

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

        base_table = args[-2]
        cycle = args[-1]

        if base_table is None:
            raise CommandError("You must specify a table")
        if cycle is None:
            raise CommandError("You must specify a cycle")

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
