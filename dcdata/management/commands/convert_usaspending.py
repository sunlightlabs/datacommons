from dcdata.scripts.usaspending.converter import USASpendingDenormalizer
from django.core.management.base import BaseCommand
import os


class Command(BaseCommand):

    def handle(self, in_path, out_path, **options):
        out_grants_path = os.path.join(os.path.abspath(out_path), 'grants.out')
        out_contracts_path = os.path.join(os.path.abspath(out_path), 'contracts.out')
    
        USASpendingDenormalizer().parse_directory(os.path.abspath(in_path), None, out_grants_path, out_contracts_path)
