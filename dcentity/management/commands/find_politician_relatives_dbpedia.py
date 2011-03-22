import urllib, urllib2, logging, pprint

from dcentity.models             import WikipediaInfo
from django.conf                 import settings
from django.core.management.base import BaseCommand
from django.db                   import connections, transaction
from lxml                        import etree
from name_cleaver.name_cleaver   import PoliticianNameCleaver, RunningMatesNames
from votesmart                   import votesmart, VotesmartApiError

import os
import os.path

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

    @transaction.commit_manually
    def handle(self, *args, **options):
        self.log.info("Starting...")

        cursor = connections['default'].cursor()

        wikipedia_infos = WikipediaInfo.objects.filter(entity__type='politician')

        #for info in wikipedia_infos:
            #entity_name = os.path.basename(info.bio_url)
        entity_name = 'Jeb_Bush'
        raw_resource = urllib2.urlopen('http://dbpedia.org/data/{0}.json'.format(entity_name)).read()
        data = json.loads(raw_resource)

        data = data['http://dbpedia.org/resource/{0}'.format(entity_name)]


        #names = []
        #names.extend(data.get('http://www.w3.org/2002/07/owl#sameAs'))
        #names.extend(data.get('http://dbpedia.org/property/name'))
        #names.extend(data.get('http://dbpedia.org/ontology/birthName'))

        spouses = data.get('http://dbpedia.org/ontology/spouse', [])
        parents = data.get('http://dbpedia.org/ontology/parent', [])
        relations = data.get('http://dbpedia.org/ontology/relation', [])
        children = data.get('http://dbpedia.org/ontology/child', [])

        print 'parents:'
        print parents
        for x in parents:
            print x.get('type')
            print x.get('value')

        print 'generic relations:'
        print relations
        for x in relations:
            print x.get('type')
            print x.get('value')

        print 'children:'
        print children
        for x in children:
            print x.get('type')
            print x.get('value')

        print 'spouses: '
        for x in spouses:
            if x['type'] == 'uri':
                spouse_page = urllib.urlopen(x['value'])
                spouse_data = json.loads(spouse_page.read())
                s_data = spouse_data[x['value']]
                s_name = 
        #import pdb; pdb.set_trace()
            #print dbp_data.read()
