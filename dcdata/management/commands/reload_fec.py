from django.core.management.base import BaseCommand
from django.db import transaction

from dcdata.fec.importer import FECImporter


class Command(BaseCommand):

    @transaction.commit_on_success
    def handle(self, *args, **options):

        if args:
            data_dir = args[0]
        else:
            data_dir = None

        i = FECImporter(data_dir)
        i.update_csv()
        i.update_db()
