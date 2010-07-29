import os
import re
import csv
import random

from django.core.management.base import BaseCommand
from django.conf import settings

from dcentity.tools import wpapi
from dcentity.tools.models import EntityPlus

class Command(BaseCommand):
    args = '<input_file> <output_file'
    help = """Manually code the correct wikipedia URL for a given sample of
entities.  First, create a sample using `./manage.py entity_sample`.  Then, run
this to code the correct URLs for each entity, which can be used to test the
automatic wikipedia fetching algorithm.

For each result, a prompt will be printed with some full text search best
guesses.  For each entity, the prompt accepts one of the following:

    * Type the number next to the entry (0-10) to choose that result.
    * Type 'n' to indicate there is no result (URL will be null).
    * Include the full correct URL ("http://...") to specify a URL manually.

"""

    def handle(self, *args, **kwargs):
        if len(args) < 2:
            print "Usage: python manage.py wp_sample_entities <input_file> <output_file>"
            print
            print self.help
            return

        input_file = args[0]
        output_file = args[1]

        results = {}
        if os.path.exists(output_file):
            with open(output_file) as fh:
                reader = csv.reader(fh)
                for row in reader:
                    results[row[0]] = row

        eids = []
        with open(input_file) as fh:
            reader = csv.reader(fh)
            for row in reader:
                eids.append(row[0])
        
        entities = EntityPlus.objects.in_bulk(eids)

        with open(output_file, 'w') as fh:
            writer = csv.writer(fh)
            for eid,row in results.iteritems():
                writer.writerow(row)

            for eid, entity in entities.iteritems():
                if eid in results:
                    continue
                wikipedia_url = self.select_search_url(entity)
                # Only eid and url are needed; other fields are written for
                # ease of visual inspection.
                writer.writerow((eid, wikipedia_url, entity.name, entity.type))

    def select_search_url(self, entity):
        search = entity.get_search_terms(entity.names[0])
        results = wpapi.full_text_search(search)
        extra = ""
        if entity.type == 'politician':
            md = entity.politician_metadata.all()[0]
            extra += md.state + ", " + md.party

        print
        print '----------------------', search, "(%s)" % entity.type, extra
        print
        for i,result in enumerate(results):
            so_wide = []
            for j in range(0, len(result['content']), 80):
                so_wide.append(result['content'][j:j + 80])
            content = "\n  ".join(so_wide)
            print i, result['title']
            print " ", wpapi.article_url(result['title'])
            print " ", content
            print

        while True:
            selection = raw_input(search + " ?> ")
            if selection == 'n':
                return None
            try:
                i = int(selection)
                return wpapi.article_url(results[i]['title'])
            except ValueError:
                pass

            if selection.startswith("http"):
                return selection


