from django.core.management.base import BaseCommand
from django.db import transaction

from dcdata.fec.importer import reload_fec


class Command(BaseCommand):

    @transaction.commit_on_success
    def handle(self, *args, **options):

        if args:
            data_dir = args[0]
        else:
            data_dir = None

        reload_fec(data_dir)

