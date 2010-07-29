import copy
import csv
from pprint import pprint
from collections import defaultdict

from django.core.management.base import BaseCommand

from dcentity.tools.models import EntityPlus
from dcentity.tools.management.commands.entity_wikipedia_scrape import find_wikipedia_url

class colors:
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    ENDC = '\033[0m'

class Command(BaseCommand):
    args = '<csv_file> <csv_file> ...'
    help = """Tests the wikipedia matching algorithm against the given CSV files
containing coded samples."""

    def handle(self, *args, **kwargs):
        if len(args) == 0:
            print """Requires at least one CSV file argument, which should contain two columns:

    <entity id>, <wikipedia url or ''>
"""
            return

        self.coded = {}
        for csv_file in args:
            with open(csv_file) as fh:
                reader = csv.reader(fh)
                for row in reader:
                    self.coded[row[0]] = row[1]

        self.results = {}
        self.entities = {}
        for eid, url in self.coded.iteritems():
            # Annotate the entity with its total from the agg_entities table.
            entity = EntityPlus.objects.raw("""
                SELECT m.*, GREATEST(a.contributor_amount, a.recipient_amount) AS total
                FROM matchbox_entity m LEFT JOIN agg_entities a ON m.id=a.entity_id
                WHERE a.cycle=-1 AND m.id = %s
                """, [eid])[0]
            match = find_wikipedia_url(entity) or ['', '']
            print(eid,url,match[0])
            self.results[eid] = match[0]
            self.entities[eid] = entity

        self.pretty_print_results()

    def count_stratified_results(self, num_bins=10):
        """
        Return a dict of results organized by type and total amount.
        "num_bins" specifies the number of bins into which to group entities.
        Returns:
        {
            'politician': {
                0: {
                    'tp': 3,
                    'fp': 2,
                    'fn': 4,
                    'fp': 1
                },
                1: {
                    ...
                }
                ...
            },
            'organization': {
                ...
            },
        }
        """
        self.percentiles = {}
        bin_totals = defaultdict(dict)
        for etype in ('politician', 'organization'):
            ordered = [e for e in self.entities.values() if e.type == etype]
            ordered.sort(key=lambda e: e.total)
            per_bin = int(len(ordered) / num_bins)
            for i, b in enumerate(range(0, len(ordered), per_bin)):
                percentile = int(100 * (float(i) / num_bins))
                bin_totals[etype][percentile] = {
                        'tp': 0, 'fp': 0, 'tn': 0, 'fn': 0
                }
                for entity in ordered[b:b+per_bin]:
                    classification = self.classify_result(
                            self.results[entity.id], 
                            self.coded[entity.id]
                    )
                    bin_totals[etype][percentile][classification] += 1
                    self.percentiles[entity.id] = percentile
            # cast results from defaultdict to dict so pprint can pprint them
            bin_totals[etype] = dict(bin_totals[etype])
        return dict(bin_totals)

    def classify_result(self, got, wanted):
        """ 
        Return a string classifying the given wikipedia url based
        on what the coded entity has.
            'tp': true positive  (urls match, neither are None)
            'fp': false positive (urls don't match, and url isn't None)
            'tn': true negative  (both urls are None)
            'fn': false negative (url is None, real isn't)
        """
        if not wanted:
            if not got:
                return "tn"
            else:
                return "fp"
        else:
            if wanted == got:
                return "tp"
            elif not got:
                return "fn"
            else:
                return "fp"

    def results_by_class(self):
        """
        Return a dict organizing eid's of results by class, e.g.:
        {
            'tp': [eid, eid, eid, ...],
            'fp': [eid, eid...],
            'fn': [..],
            'tn': [..],
        }
        """
        classes = defaultdict(list)
        for eid in self.coded:
            if self.entities[eid].type == 'individual':
                continue
            got = self.results[eid]
            wanted = self.coded[eid]
            classes[self.classify_result(got, wanted)].append(eid)
        return classes

    def pretty_print_results(self):
        classes = self.results_by_class()
        # Display totals for each class
        for key, eids in classes.iteritems():
            pprint((key, len(eids)))
        pprint(self.count_stratified_results())

        for color, classification in ((colors.BLUE, 'fp'), (colors.RED, 'fn')):
            for eid in sorted(
                    classes.get(classification, []), 
                    key=lambda eid: self.percentiles[eid]):
                entity = self.entities[eid]
                if entity.type == 'individual':
                    continue
                type_disp = entity.type
                if entity.type == 'organization':
                    if entity.names[0].is_politician():
                        type_disp = colors.YELLOW + type_disp + colors.ENDC
                    else:
                        type_disp = colors.MAGENTA + type_disp + colors.ENDC
                    extra = ""
                    if entity.names[0].is_company():
                        extra += "inc"
                    if entity.names[0].is_politician():
                        extra += "pac"
                elif entity.type == 'politician':
                    md = entity.politician_metadata.all()[0]
                    extra = "%s-%s" % (md.party or '', md.state or '')

                print type_disp, color, self.percentiles[entity.id], (
                    entity.names[0].name, 
                    extra,
                    entity.get_search_terms(entity.names[0]),
                    "got: " + unicode(self.results[eid]) + \
                    " wanted: " + unicode(self.coded[eid]),
                ), colors.ENDC
