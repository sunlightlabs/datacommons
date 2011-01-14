from dcdata.grants.models import Grant
from dcdata.scripts.usaspending.loader import Loader
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):

    @transaction.commit_on_success
    def handle(self, grant_path, **options):
        print Grant.objects.all().count()
        
        Loader().insert_faads(grant_path)
        transaction.set_dirty()

        print Grant.objects.all().count()
