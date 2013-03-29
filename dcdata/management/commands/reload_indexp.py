
from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings

from dcdata.independentexpenditures.importer import reload_indexp


class Command(BaseCommand):
    
    @transaction.commit_on_success
    def handle(self, *args, **options):
        data_dir = args[-2]
        cycle = args[-1]
        reload_indexp(data_dir, cycle)
