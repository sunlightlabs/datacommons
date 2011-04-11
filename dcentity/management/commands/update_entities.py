import logging

from django.db                   import connections, transaction
from dcentity.entity             import build_entity
from django.core.management.base import BaseCommand
from dcdata.contribution.models  import CRP_TRANSACTION_NAMESPACE, NIMSP_TRANSACTION_NAMESPACE
from datetime                    import datetime
from optparse                    import make_option


INDIVIDUAL_CREATE_MAX_WARN = 100
INDIVIDUAL_DELETE_MAX_WARN = 30

POLITICIAN_CREATE_MAX_WARN = 300
POLITICIAN_DELETE_MAX_WARN = 50

ORGANIZATION_CREATE_MAX_WARN = 100

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('-d', '--dry-run',
            action='store_true',
            dest='dry_run',
            default=False,
            help='Don\'t have the entity creation do anything but report the entities that would be created.',
        ),
        make_option('-i', '--force-indivs',
            action='store_true',
            dest='force_indivs',
            default=False,
            help='Force creation of individuals despite warnings about number of entities to be created.',
        ),
        make_option('-p', '--force-pols',
            action='store_true',
            dest='force_pols',
            default=False,
            help='Force creation of politicians despite warnings about number of entities to be created.',
        ),
        make_option('-o', '--force-orgs',
            action='store_true',
            dest='force_orgs',
            default=False,
            help='Force creation of organizations despite warnings about number of entities to be created.',
        ),
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
        self.dry_run = options['dry_run']
        self.force_indivs = options['force_indivs']
        self.force_pols = options['force_pols']
        self.force_orgs = options['force_orgs']

        self.today = datetime.today().strftime("%Y%m%d")
        self.cursor = connections['default'].cursor()

        if not options['skip_indivs']:
            self.flag_individuals_for_deletion()
        if not options['skip_pols']:
            self.flag_politicians_for_deletion()

        try:
            if not options['skip_indivs']:
                self.create_individuals()
            if not options['skip_pols']:
                self.create_politicians()
            if not options['skip_orgs']:
                self.create_organizations()
        except EntityManagementError as e:
            self.log.error(e)


    @transaction.commit_on_success()
    def create_individuals(self):
        self.log.info("Starting to find individuals to create...")

        creation_sql = """
            create table tmp_individuals_{0} as
                select min(name) as name, id from (
                    select min(lobbyist_name) as name, lobbyist_ext_id as id
                    from lobbying_lobbyist
                    inner join lobbying_report using (transaction_id)
                    where
                        lobbyist_name != ''
                        and not exists (select * from matchbox_entityattribute where value = lobbyist_ext_id)
                        and not use
                    group by lobbyist_ext_id

                    union

                    select min(contributor_name) as name, contributor_ext_id as id
                    from contribution_contribution
                    where
                        contributor_name != ''
                        and contributor_ext_id like 'U%'
                        and not exists (select * from lobbying_lobbyist where lobbyist_ext_id = contributor_ext_id)
                        and not exists (select * from matchbox_entityattribute where value = contributor_ext_id)
                    group by contributor_ext_id
                )x
                group by id
        """.format(self.today)

        self.cursor.execute(creation_sql, None)
        transaction.set_dirty()
        self.log.info("- Table tmp_individuals_%s populated." % self.today)

        self.cursor.execute("select name, id from tmp_individuals_%s" % self.today)
        results = self.cursor.fetchall()

        if not self.force_indivs and len(results) > INDIVIDUAL_CREATE_MAX_WARN:
            raise EntityManagementError("The number of individuals set to be created is {0}. The max this script will create automatically is {1}.".format(len(results), INDIVIDUAL_CREATE_MAX_WARN))

        for result in results:
            name, crp_id = result
            if self.dry_run:
                self.log.info("- Would build entity {0}|{1}".format(name, crp_id))
            else:
                build_entity(name, 'individual', [('urn:crp:individual', crp_id)])

        self.log.info("- Created {0} individual entities.".format(len(results)))


    @transaction.commit_on_success()
    def create_organizations(self):
        self.log.info("Starting to find organizations to create...")

        tmp_sql = """
            create table tmp_lobbying_orgs_{0} as
                select 0 as crp_id, 0 as nimsp_id, max(l.registrant_name) as name
                from lobbying_lobbying l
                where
                    l.use = 't'
                    and registrant_name != ''
                    and not exists (
                        select *
                        from matchbox_entity e
                        inner join matchbox_entityalias a on e.id = a.entity_id
                        where
                            e.type = 'organization'
                            and lower(l.registrant_name) = lower(a.alias)
                    )
                group by lower(registrant_name)
        """.format(self.today)
        self.cursor.execute(tmp_sql, None)
        transaction.set_dirty()
        self.log.info("- Table tmp_lobbying_orgs_{0} populated.".format(self.today))

        self.cursor.execute("select name, nimsp_id, crp_id from tmp_lobbying_orgs_{0}".format(self.today))
        results = self.cursor.fetchall()

        if not self.force_orgs and len(results) > ORGANIZATION_CREATE_MAX_WARN:
            raise EntityManagementError("The number of organizations set to be created is {0}. The max this script will create automatically is {1}.".format(len(results), ORGANIZATION_CREATE_MAX_WARN))

        for result in results:
            name, nimsp_id, crp_id = result
            if self.dry_run:
                self.log.info("- Would build entity {0}".format(result))
            else:
                attributes = []
                if nimsp_id and nimsp_id != '0':
                    attributes.append(('urn:nimsp:organization', nimsp_id))
                if crp_id and crp_id != '0':
                    attributes.append(('urn:crp:organization', crp_id))

                build_entity(name, 'organization', attributes)

        self.log.info("- Created {0} organization entities.".format(len(results)))


    @transaction.commit_on_success()
    def create_politicians(self):
        self.log.info("Starting to find politicians to create...")

        tmp_sql = """
            create table tmp_politicians_{0} as
                select min(recipient_name) as name, transaction_namespace as namespace, recipient_ext_id as id
                from contribution_contribution
                where
                    recipient_type = 'P'
                    and recipient_name != ''
                    and recipient_ext_id != ''
                    and not exists (select * from matchbox_entityattribute where value = recipient_ext_id)
                group by transaction_namespace, recipient_ext_id
        """.format(self.today)
        self.cursor.execute(tmp_sql, None)
        transaction.set_dirty()
        self.log.info("- Table tmp_politicians_{0} populated.".format(self.today))

        self.cursor.execute("select name, namespace, id from tmp_politicians_{0}".format(self.today), None)
        results = self.cursor.fetchall()

        if not self.force_pols and len(results) > POLITICIAN_CREATE_MAX_WARN:
            raise EntityManagementError("The number of politicians set to be created is {0}. The max this script will create automatically is {1}.".format(len(results), POLITICIAN_CREATE_MAX_WARN))

        for result in results:
            name, namespace, id = result
            if self.dry_run:
                self.log.info("- Would build entity %s|%s|%s" % (name, namespace, id))
            else:
                attributes = []
                if id:
                    if namespace == NIMSP_TRANSACTION_NAMESPACE:
                        attributes.append(('urn:nimsp:recipient', id))
                    elif namespace == CRP_TRANSACTION_NAMESPACE:
                        attributes.append(('urn:crp:recipient', id))
                    else:
                        raise Exception('Unknown namespace: %s' % namespace)

                build_entity(name, 'politician', attributes)

        self.log.info("- Created {0} politician entities.".format(len(results)))


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
                    and not exists (
                        select *
                        from contribution_contribution c
                        where c.contributor_ext_id = a.value)
                    and not exists (
                        select *
                        from lobbying_lobbyist
                        inner join lobbying_report using (transaction_id)
                        where
                            lobbyist_ext_id = a.value
                            and use
                    )
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
            where id in (
                select
                    e.id
                from
                    matchbox_entity e
                where
                    e.type = 'politician'
                    and not exists (
                        select *
                        from contribution_contribution c
                        inner join matchbox_entityattribute a on e.id = a.entity_id
                        where c.recipient_ext_id = a.value
                    )
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



class EntityManagementError(Exception):
    pass

