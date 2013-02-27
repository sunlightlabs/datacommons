from django.core.management.base import CommandError, BaseCommand
from django.db import connections, transaction


class Command(BaseCommand):

    @transaction.commit_on_success
    def handle(self, *args, **kwargs):
        """
        Takes a relation name and a cycle and deletes its partition.
        (Usually with the assumption that it will be recreated for
        a fresh data load.)
        """

        base_table = args[0]
        cycle = args[1]

        if base_table is None:
            raise CommandError("You must specify a table")
        if cycle is None:
            raise CommandError("You must specify a cycle")

        partition_name = '{}_{}'.format(base_table, cycle[-2:])

        drop_stmt = """
            drop table if exists {}
        """.format(partition_name)
        print drop_stmt

        c = connections['default'].cursor()
        c.execute(drop_stmt)
