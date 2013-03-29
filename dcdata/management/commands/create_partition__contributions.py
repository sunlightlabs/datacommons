from django.core.management.base import CommandError, BaseCommand
from django.db import connections, transaction

class Command(BaseCommand):

    full_namespaces = {
            'nimsp': 'urn:nimsp:transaction',
            'crp': 'urn:fec:transaction',
    }

    columns_to_index = 'transaction_namespace cycle'.split()

    def handle(self, *args, **kwargs):

        namespace = kwargs.get('namespace')
        cycle = kwargs.get('cycle')

        if namespace is None:
            raise CommandError("You must specify a namespace")
        if cycle is None:
            raise CommandError("You must specify a namespace")

        table_name = 'contributions_{}_{}'.format(namespace, cycle[-2:])

        create_stmt = """
            create table {} (
                check ( transaction_namespace = '{}' and cycle = {} )
            ) inherits (contribution_contribution)
        """.format(table_name, self.full_namespaces[namespace], cycle)

        indexes_stmt = ' '.join(['create index {0}__{1} on {0} ({1})'.format(table_name, column_name) for column_name in self.columns_to_index ])
