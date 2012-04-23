
from django.core.management.base import BaseCommand
from django.db import transaction, connection

from dcentity.entity import build_entity


committees_stmt = """
    select committee_name, committee_id
    from fec_committees
    where
        committee_id in (select distinct spender_id from fec_indexp)
        and committee_id not in (select distinct value from matchbox_entityattribute where namespace = 'urn:fec:committee');
"""


def new_spenders():
    c = connection.cursor()
    c.execute(committees_stmt)
    
    return c


class Command(BaseCommand):
    
    @transaction.commit_on_success
    def handle(self, **options):
        print "Adding entities:"
        for (name, committee_id) in new_spenders():
            print "%s: %s" % (name, committee_id)
            build_entity(name, 'organization', [('urn:fec:committee', committee_id)])
