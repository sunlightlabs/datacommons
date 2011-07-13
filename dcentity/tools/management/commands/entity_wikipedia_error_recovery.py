import os
import datetime

from django.core.management.base import BaseCommand
from django.conf import settings

from dcentity.tools import utils
from dcentity.tools.models import EntityPlus
from dcentity.tools.management.commands.entity_wikipedia_scrape import find_wikipedia_url

class Command(BaseCommand):
    args = '<error_file> <output_file>'
    help = """Debugging tool for recovering from errors that arose while
running "entity_wikipedia_scrape".  Requires two arguments:

    <error_file> filename for error file from which to read
    <output_file> filename for output file to store results

Unlike `entity_wikipedia_scrape` which catches all errors in order to get
through all 100,000+ entities efficiently, this command allows errors to be
thrown, allowing you to fix whatever code might be causing them.
"""

    def handle(self, *args, **kwargs):
        if len(args) < 2:
            print "Requires two arguments: <error_file> <output_file>"
            print
            print self.help
            return
        error_file = args[0]
        output_file = args[1]

        # Retrieve previous results
        results = {}
        if os.path.exists(output_file):
            with open(output_file) as fh:
                reader = utils.UnicodeReader(fh)
                for row in reader:
                    results[row[0]] = row

        # Fetch and record new results
        with open(output_file, 'w') as fh:
            writer = utils.UnicodeWriter(fh)
            for eid, row in results.iteritems():
                writer.writerow(row)

            eids = []
            with open(error_file) as fh:
                error_reader = utils.UnicodeReader(fh)
                for row in error_reader:
                    eids.append(row[0])

            for eid in eids:
                if eid in results:
                    continue
                entity = EntityPlus.objects.get(id=eid)

                print
                print "Attempting:", eid, entity.name

                # Allow errors to be thrown.
                wp = find_wikipedia_url(entity) or ['', '', '']
                url, excerpt, image_url = wp
                row = (entity.id, url, image_url, excerpt, unicode(datetime.datetime.now()))
                results[row[0]] = row
                writer.writerow(row)
                print "  %i/%i" % (len(results), len(eids)),
                print (entity.name, row[1])
