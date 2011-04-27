from lxml import objectify
from django.db import transaction
from django.core.management.base import BaseCommand
from dcentity.models import Entity, PoliticianCommittee
import os.path

CYCLES_BY_SESSION = {
        '101': 1990, '102': 1992, '103': 1994, '104': 1996,
        '105': 1998, '106': 2000, '107': 2002, '108': 2004,
        '109': 2006, '110': 2008, '111': 2010, '112': 2012,
}

class Command(BaseCommand):
    @transaction.commit_on_success
    def handle(self, session, committees_path, people_path, **args):
        # take in people file, committees file
        # people file:
        # parse for person:id, person:osid (crp id) so that we can link the data to ours.
        # committess file:
        # parse for committee:displayname committee:member(s):id committee:member(s):role
        # role can be "Chairman"/"Ranking Member"

        committees_tree = objectify.parse(os.path.abspath(committees_path))
        people_tree = objectify.parse(os.path.abspath(people_path))

        committees_root = committees_tree.getroot()
        people_root = people_tree.getroot()

        self.people_ids = {}
        for person in people_root.findall('person'):
            self.people_ids[person.attrib['id']] = person.attrib['osid']

        for committee in committees_root.findall('committee'):
            shortest_name = self.find_shortest_name_for_committee(committee, session)
            code = committee.attrib.get('code', '')

            for member in committee.findall('member'):
                pol = self.find_politician_entity_for_member(member)
                if not pol: continue
                PoliticianCommittee.objects.create(
                    entity=pol,
                    code=committee.attrib.get('code', ''),
                    name=shortest_name,
                    is_chair=member.attrib.get('role', '')=='Chairman',
                    is_ranking=member.attrib.get('role', '')=='Ranking Member',
                    cycle=CYCLES_BY_SESSION[session]
                )
            for subcommittee in committee.findall('subcommittee'):
                subcommittee_shortest_name = self.find_shortest_name_for_committee(subcommittee, session)

                for member in subcommittee.findall('member'):
                    pol = self.find_politician_entity_for_member(member)
                    if not pol: continue
                    PoliticianCommittee.objects.create(
                        entity=pol,
                        code=subcommittee.attrib.get('code', ''),
                        name=subcommittee_shortest_name,
                        is_chair=member.attrib.get('role', '')=='Chairman',
                        is_ranking=member.attrib.get('role', '')=='Ranking Member',
                        is_subcommittee=True,
                        parent_code=code,
                        cycle=CYCLES_BY_SESSION[session]
                    )

    def find_politician_entity_for_member(self, member):
        print u'Looking for {0} with CRP ID {1}'.format(member.attrib.get('name', ''), self.people_ids[member.attrib['id']])
        try:
            return Entity.objects.get(
                attributes__namespace='urn:crp:recipient',
                attributes__value=self.people_ids[member.attrib['id']]
            )
        except:
            return False

    def find_shortest_name_for_committee(self, committee, session):
        # we have either a name in a child node or the name in the attribute (different formats)
        # we'll try both.
        node_name = committee.find("/thomas-names/name[@session='{0}']".format(session))
        attr_name = committee.attrib.get('thomasname')

        # we might not have either, in which case we'll fall back to the longer displayname
        return node_name or attr_name or committee.attrib['displayname']





