
from django.core.management.base import BaseCommand
from django.db import transaction

from dcdata.independentexpenditures.importer import reload_indexp


class Command(BaseCommand):
    
    @transaction.commit_on_success
    def handle(self, data_dir, **options):
        reload_indexp(data_dir)