from dcdata.scripts.usaspending.converter import USASpendingDenormalizer
from django.core.management.base import BaseCommand
import os
import logging


class Command(BaseCommand):

    def __init__(self):
        self.set_up_logger()


    def set_up_logger(self):
        # create logger
        self.log = logging.getLogger("command")
        self.log.setLevel(logging.DEBUG)
        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        # create formatter
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        ch.setFormatter(formatter)
        self.log.addHandler(ch)


    def handle(self, in_path, out_path, **options):
        self.log.info("Starting...")

        out_grants_path = os.path.join(os.path.abspath(out_path), 'grants.out')
        out_contracts_path = os.path.join(os.path.abspath(out_path), 'contracts.out')

        self.log.debug("The output file paths will be:")
        self.log.debug("    " + out_grants_path)
        self.log.debug("    " + out_contracts_path)

        USASpendingDenormalizer(logger=self.log).parse_directory(os.path.abspath(in_path), None, out_grants_path, out_contracts_path)

        self.log.info("Done.")
