#!/usr/bin/env python

# this was a hacky one-off script that's been turned into a still-hacky
# management command.  It should be reworked to use the database instead of the
# API at some point.
import csv, sys
from django.core.management import BaseCommand, CommandError
from django.conf import settings

class Command(BaseCommand):
    def handle(self, *args, **options):
        # check args
        if len(args) != 1:
            raise CommandError("Please specify one argument.")
        
        in_name = args[0]
        out_name = args[0].replace('.csv', '_matched.csv')
        
        in_file = open(in_name, 'r')
        out_file = open(out_name, 'w')
        
        fields = ['td_id', 'type', 'name', 'ie_url', 'majority_non_yes', 'match']
        in_csv = csv.DictReader(in_file)
        out_csv = csv.DictWriter(out_file, fields, extrasaction='ignore')
        out_csv.writeheader()
        
        # set up api
        from influenceexplorer import InfluenceExplorer
        api = InfluenceExplorer(settings.SYSTEM_API_KEY, 'http://transparencydata.com/api/1.0/')
        
        # set up standardizers
        from name_cleaver import IndividualNameCleaver, OrganizationNameCleaver, PoliticianNameCleaver
        from django.template.defaultfilters import slugify
        standardizers = {
            'individual': IndividualNameCleaver,
            'organization': OrganizationNameCleaver,
            'politician': PoliticianNameCleaver
        }
        def standardize(type, name):
            return standardizers[type](name).parse().__str__()
            
        for row in in_csv:
            meta = api.entities.metadata(row['td_id'])
            if meta['type'] == 'organization':
                row['type'] = 'organization'
            elif meta['type'] == 'politician':
                row['type'] = meta['metadata']['seat'].split(':')[0]
            
            row['name'] = standardize(meta['type'], meta['name'])
            row['ie_url'] = 'http://influenceexplorer.com/%s/%s/%s' % (meta['type'], slugify(row['name']), row['td_id'])
            
            row['match'] = 'presumed correct' if str(row['majority_non_yes']).lower() == 'false' else ''
            
            out_csv.writerow(row)
