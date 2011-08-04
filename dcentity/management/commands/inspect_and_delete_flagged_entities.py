import logging

from django.db                   import connections, transaction
from dcentity.models             import Entity
from django.core.management.base import BaseCommand
from datetime                    import datetime


DEBUG = True

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


    @transaction.commit_on_success()
    def handle(self, **kwargs):
        self.today = datetime.today().strftime("%Y%m%d")
        self.cursor = connections['default'].cursor()

        self.log.info("Starting...")

        should_delete_indiv = self.inspect_entities_for_deletion('individual')
        should_delete_pols  = self.inspect_entities_for_deletion('politician')
        should_delete_orgs  = self.inspect_entities_for_deletion('organization')

        self.delete_entities('individual', should_delete_indiv)
        self.delete_entities('politician', should_delete_pols)
        self.delete_entities('organization', should_delete_orgs)

        self.log.info("Finished.")


    def inspect_entities_for_deletion(self, entity_type):
        candidates = Entity.objects.filter(type=entity_type, should_delete=True).select_related().all()
        return self.inspect_and_prompt(candidates, entity_type)


    def delete_entities(self, entity_type, should_delete=False):
        if not should_delete:
            return

        self.log.info("Deleting {0}s...".format(entity_type))
        Entity.objects.filter(type=entity_type, should_delete=True).delete()


    def inspect_and_prompt(self, candidates, type):
        if len(candidates) > 0:
            for entity in candidates:
                self.print_formatted_entity(entity)
        else:
            self.log.info('No {0}s were flagged for deletion.'.format(type))
            return False

        choice = raw_input("Do you wish to proceed with deleting these {0}s? (Y/[N]): ".format(type))
        choice = choice.strip()

        return choice.lower() == 'y'


    def print_formatted_entity(self, entity):
        attributes_str = '|'.join([ '::'.join([x.namespace, x.value]) for x in entity.attributes.all() ])
        self.log.info('{0} ({1}): {2}'.format(entity.name.encode("utf8", "replace"), entity.id, attributes_str))

