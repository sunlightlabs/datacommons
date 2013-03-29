from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
from dcdata.fec.importer import FECImporter
from optparse import make_option


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--skip-download',
            action='store_true',
            dest='skip_dl',
            default=False,
            help='Skip the download/extract/convert to UTF-8 step'),
        )

    @transaction.commit_on_success
    def handle(self, *args, **options):

        if args:
            data_dir = args[0]
            cycle = args[1]
        else:
            data_dir = None
            cycle = settings.DEFAULT_CYCLE

        i = FECImporter(data_dir, cycle, skip_download=options['skip_dl'])
        i.run()
