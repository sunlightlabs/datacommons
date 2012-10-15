from django.db                   import connections
from django.core.management.base import BaseCommand
from pprint                      import PrettyPrinter

class Command(BaseCommand):
    help = 'Work in progress. Prints out counts of spending tables, for now.'

    def handle(self, *args, **options):
        self.cursor = connections['default'].cursor()

        results = {}
        results['contracts_count'] = int(self.get_table_count('contracts_contract')[0])
        results['grants_count'] = int(self.get_table_count('grants_grant')[0])
        results['agg_sp_org_count'] = int(self.get_table_count('agg_spending_org')[0])
        results['agg_sp_totals_count'] = int(self.get_table_count('agg_spending_totals')[0])
        results['assoc_sp_contracts_count'] = int(self.get_table_count('assoc_spending_contracts')[0])
        results['assoc_sp_grants_count'] = int(self.get_table_count('assoc_spending_grants')[0])

        pp = PrettyPrinter()
        pp.pprint(results)

    def get_table_count(self, table_name):
        self.cursor.execute('select count(*) from {}'.format(table_name))
        return self.cursor.fetchone()
