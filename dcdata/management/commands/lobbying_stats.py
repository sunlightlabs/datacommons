from django.db                   import connections
from django.core.management.base import BaseCommand, CommandError
from pprint                      import PrettyPrinter

class Command(BaseCommand):
    help = 'Work in progress. Prints out counts of lobbying tables, for now.'

    def handle(self, *args, **options):
        self.cursor = connections['default'].cursor()

        results = {}
        results['lobbying_count'] = int(self.get_table_count('lobbying_lobbying')[0])
        results['agency_count'] = int(self.get_table_count('lobbying_agency')[0])
        results['lobbyist_count'] = int(self.get_table_count('lobbying_lobbyist')[0])
        results['issue_count'] = int(self.get_table_count('lobbying_issue')[0])
        results['bill_count'] = int(self.get_table_count('lobbying_bill')[0])
        results['billtitle_count'] = int(self.get_table_count('lobbying_billtitle')[0])

        pp = PrettyPrinter()
        pp.pprint(results)

    def get_table_count(self, table_name):
        self.cursor.execute('select count(*) from {}'.format(table_name))
        return self.cursor.fetchone()
