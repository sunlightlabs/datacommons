import urllib, urllib2, logging, pprint

from dcentity.models             import VotesmartInfo, PoliticianRelative
from django.conf                 import settings
from django.core.management.base import BaseCommand
from django.db                   import connections, transaction
from lxml                        import etree
from name_cleaver.name_cleaver   import PoliticianNameCleaver, RunningMatesNames
from votesmart                   import votesmart, VotesmartApiError

import os
import os.path
import re

try:
    import json
except:
    import simplejson as json

class Command(BaseCommand):
    args = '<limit> <offset (optional)>'

    help = 'Find politicians\' relatives from Wikipedia via DBPedia'

    def __init__(self):
        self.set_up_logger()
        self.pp = pprint.PrettyPrinter(width=50)
        votesmart.apikey = '52b1e53c3d62bf531e8dd482067d043a'
        self.partner_re = re.compile(r'(Single|Divorced|(Married, )?(Wife|Husband|Spouse|Partner|Engaged): (?P<partner>[^,;]+))')
        self.child_re = re.compile(r'(Step)?[cC]hild(ren)?: (?P<children>[^,;]*(, [^,;]+)*);?')

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

    @transaction.commit_on_success
    def handle(self, *args, **options):
        self.log.info("Starting...")
        # load up politicians with VoteSmart ID's
        politicians = VotesmartInfo.objects.all()

        for pol in politicians:
            try:
                bio = votesmart.candidatebio.getBio(pol.votesmart_id)
            except VotesmartApiError:
                try:
                    bio = votesmart.candidatebio.getBio(pol.votesmart_id)
                except VotesmartApiError:
                    continue


            pol_name_obj = PoliticianNameCleaver(pol.entity.name).parse()

            if hasattr(pol_name_obj, 'mates'):
                pol_name_obj = pol_name_obj.mates()[0]

            #match = re.match(r'^((Wife|Husband): (?P<partner>\w+))?((; )?\d+ Child(ren)?(: (?P<children>\w+(, \w+)*))?)?$', bio.family)
            if bio.family:
                partner_match = self.partner_re.match(bio.family)
                child_match = self.child_re.search(bio.family)
                if partner_match or child_match:
                    partner = partner_match.groupdict()['partner'] if partner_match else ''
                    children = child_match.groupdict()['children'] if child_match else ''

                    if partner:
                        if not ' ' in partner:
                            partner = ' '.join([partner, pol_name_obj.last])

                        print u'{0} {1} - Loading partner {2}.'.format(bio.firstName, bio.lastName, partner)

                        partner_name_obj = PoliticianNameCleaver(partner).parse()
                        PoliticianRelative.objects.create(
                            entity = pol.entity,
                            raw_name = partner,
                            first_name = partner_name_obj.first,
                            middle_name = partner_name_obj.middle,
                            last_name = partner_name_obj.last,
                            relation = 'partner',
                        )

                    if children:
                        if ',' in children or '&' in children:
                            children = re.split(r'[,&]', children)
                            children = [ x.strip() for x in children ]
                        else:
                            children = [children]

                        for child in children:
                            if not ' ' in child:
                                child = ' '.join([child, pol_name_obj.last])

                            print u'{0} {1} - Loading child {2}'.format(bio.firstName, bio.lastName, child)
                            child_name_obj = PoliticianNameCleaver(child).parse()
                            PoliticianRelative.objects.create(
                                entity = pol.entity,
                                raw_name = child,
                                first_name = child_name_obj.first,
                                middle_name = child_name_obj.middle,
                                last_name = child_name_obj.last,
                                relation = 'child'
                            )


                    #print '{0} {1}'.format(bio.firstName, bio.lastName)
                    #print '------ {0} '.format(bio.family)
                    #print '--- partner: {0}'.format(partner)
                    ##print '--- Other partner: {0}'.format(relatives['other_partner'])
                    #print '--- Children: {0}'.format(children)


