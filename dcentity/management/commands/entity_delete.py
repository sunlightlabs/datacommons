import logging
import sys

from django.db                   import connections, transaction
from django.core.management.base import BaseCommand
from optparse                    import make_option


INDIVIDUAL_DELETE_MAX_WARN = 30
ORGANIZATION_DELETE_MAX_WARN = 50
POLITICIAN_DELETE_MAX_WARN = 50

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('-I', '--skip-indivs',
            action='store_true',
            dest='skip_indivs',
            default=False,
            help='Skip individuals',
        ),
        make_option('-P', '--skip-pols',
            action='store_true',
            dest='skip_pols',
            default=False,
            help='Skip politicians',
        ),
        make_option('-O', '--skip-orgs',
            action='store_true',
            dest='skip_orgs',
            default=False,
            help='Skip organizations',
        ),
    )

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

    def handle(self, **options):
        if self.confirm("This script is only meant to be run after aggregates have completed. Do you want to continue?"):
            self.cursor = connections['default'].cursor()

            if not options['skip_indivs']:
                self.flag_individuals_for_deletion()
            if not options['skip_pols']:
                self.flag_politicians_for_deletion()
            if not options['skip_orgs']:
                self.flag_organizations_for_deletion()


    @transaction.commit_on_success()
    def flag_individuals_for_deletion(self):
        self.log.info("Starting to flag individuals to delete...")
        update_sql = """
            update
                matchbox_entity
            set
                should_delete = 't',
                flagged_on = statement_timestamp()
            where id in (
                select
                    e.id
                from
                    matchbox_entity e
                inner join
                    matchbox_entityattribute a
                        on e.id = a.entity_id
                where
                    e.type = 'individual'
                    and a.namespace = 'urn:crp:individual'
                except
                select entity_id from contributor_associations
                except
                select entity_id from assoc_lobbying_lobbyist
            )
        """
        self.cursor.execute(update_sql)
        transaction.set_dirty()
        self.log.info("- Update finished.")

        updated = self.cursor.rowcount

        if updated > INDIVIDUAL_DELETE_MAX_WARN:
            self.log.warn("- The script marked {0} individuals to be deleted, but we typically don't see more than {1}".format(updated, INDIVIDUAL_DELETE_MAX_WARN))
        else:
            self.log.info("- Marked {0} individuals to be deleted.".format(updated))



    @transaction.commit_on_success()
    def flag_politicians_for_deletion(self):
        self.log.info("Starting to flag politicians to delete...")
        update_sql = """
            update
                matchbox_entity
            set
                should_delete = 't',
                flagged_on = statement_timestamp()
            where
                type = 'politician'
                and id not in (
                    select distinct entity_id from recipient_associations
                )
        """
        self.cursor.execute(update_sql)
        transaction.set_dirty()
        self.log.info("- Update finished.")

        updated = self.cursor.rowcount

        if updated > POLITICIAN_DELETE_MAX_WARN:
            self.log.warn("- The script marked {0} politicians to be deleted, but we typically don't see more than {1}".format(updated, POLITICIAN_DELETE_MAX_WARN))
        else:
            self.log.info("- Marked {0} politicians to be deleted.".format(updated))


    @transaction.commit_on_success()
    def flag_organizations_for_deletion(self):
        self.log.info("Starting to flag organizations to delete...")

        update_sql = """
            update
                matchbox_entity
            set
                should_delete = 't',
                flagged_on = statement_timestamp()
            where
                type = 'organization'
                and id not in (
                    select distinct entity_id from organization_associations
                    union all
                    select distinct entity_id from parent_organization_associations
                    union all
                    select distinct entity_id from assoc_lobbying_client
                    union all
                    select distinct entity_id from assoc_lobbying_registrant
                )
        """
        self.cursor.execute(update_sql)
        self.log.info("- Update finished.")
        transaction.set_dirty()

        updated = self.cursor.rowcount

        if updated > ORGANIZATION_DELETE_MAX_WARN:
            self.log.warn("- The script marked {0} organizations to be deleted, but we typically don't see more than {1}".format(updated, ORGANIZATION_DELETE_MAX_WARN))
        else:
            self.log.info("- Marked {0} organizations to be deleted.".format(updated))


    def confirm(self, question):
        sys.stdout.write(question + ' [y/N]: ')
        choice = raw_input().lower()
        if len(choice.strip())> 0:
            return choice[0].lower() == 'y'
        else:
            return False


class EntityManagementError(Exception):
    pass

