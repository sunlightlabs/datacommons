from optparse import make_option

from django.core.management.base import BaseCommand
from django.db import transaction

from dcdata.fec.importer import reload_fec

class Command(BaseCommand):

    
    @transaction.commit_on_success
    def handle(self, data_dir, **options):
        reload_fec(data_dir)