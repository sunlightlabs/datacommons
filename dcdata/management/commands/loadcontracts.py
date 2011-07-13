from dcdata.contracts.models import Contract
from dcdata.scripts.usaspending.loader import Loader
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):

    @transaction.commit_on_success
    def handle(self, contracts_file, **options):
        print Contract.objects.all().count()

        Loader().insert_fpds(contracts_file)
        transaction.set_dirty()

        print Contract.objects.all().count()
