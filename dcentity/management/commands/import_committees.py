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
            for member in committee.findall('member'):
                pol = self.find_politician_entity_for_member(member)
                if not pol: continue
                PoliticianCommittee.objects.create(
                    entity=pol,
                    name=committee.attrib['displayname'],
                    is_chair=member.attrib.get('role', '')=='Chairman',
                    is_ranking=member.attrib.get('role', '')=='Ranking Member',
                    cycle=CYCLES_BY_SESSION[session]
                )
            for subcommittee in committee.findall('subcommittee'):
                for member in subcommittee.findall('member'):
                    pol = self.find_politician_entity_for_member(member)
                    if not pol: continue
                    PoliticianCommittee.objects.create(
                        entity=pol,
                        name=subcommittee.attrib['displayname'],
                        is_chair=member.attrib.get('role', '')=='Chairman',
                        is_ranking=member.attrib.get('role', '')=='Ranking Member',
                        is_subcommittee=True,
                        parent_name=committee.attrib['displayname'],
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




