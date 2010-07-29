import re
import csv

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection

from dcentity.models import Entity


class Command(BaseCommand):
    args = '<output_file>'
    help = """Sample all entities according to some ruleset.  Requires one
argument: <output_file>, a file to which JSON data containing the sampled
entities will be written.  An optional second argument specifies which sampling
method to use.  It may be one of:

    'stratified' (default)
    'uniform'

The data will be returned as a CSV file with one column; a list of entity ID's.
"""
    def handle(self, *args, **kwargs):
        if len(args) == 0:
            print "Usage: python manage.py wp_sample_entities <output_file>"
            print
            print self.help
            return

        self.args = args

        outfile = args[0]
        if len(args) > 1:
            method = args[1]
        else:
            method = 'stratified'

        methods = {
            'uniform': self.get_uniform_sample,
            'stratified': self.get_stratified_sample,
        }
        samples = methods[method]()
        with open(outfile, 'w') as fh:
            writer = csv.writer(fh)
            for samp in samples:
                # Only id is needed; other fields written for ease of visual
                # inspection
                row = [samp.id, samp.name, samp.type, samp.total]
                writer.writerow(row)

    def get_uniform_sample(self, num_samples=300):
        return list(Entity.objects.raw("""
            SELECT m.*, GREATEST(a.contributor_amount, a.recipient_amount) AS total
            FROM matchbox_entity m LEFT JOIN agg_entities a ON m.id=a.entity_id
            WHERE cycle = -1
            ORDER BY random()
            LIMIT """ + str(num_samples)))
        
    def get_stratified_sample(self, samples_per_type=100, amount_divisions=10):
        cursor = connection.cursor()
        samples = []
        for etype in ("individual", "politician", "organization"):
            cursor.execute("""
                SELECT COUNT(*) FROM matchbox_entity m LEFT JOIN agg_entities a ON m.id=a.entity_id
                    WHERE cycle = -1 AND m.type = %s
                """, [etype])
            count = int(cursor.fetchone()[0])
            step = float(count) / amount_divisions
            step_limit = int(step)
            for i in range(amount_divisions):
                step_offset = int(i * step)
                rqs = list(Entity.objects.raw("""
                    SELECT * FROM (
                        SELECT m.*, GREATEST(a.contributor_amount, a.recipient_amount) AS total 
                        FROM matchbox_entity m LEFT JOIN agg_entities a ON m.id=a.entity_id
                        WHERE cycle = -1 AND m.type = %s
                        ORDER BY total LIMIT %i OFFSET %i
                    ) AS sorted ORDER BY random() LIMIT %i
                    """ % ("%s", step_limit, step_offset, amount_divisions),
                    [etype]))
                rqs.sort(key=lambda e: e.total)
                print i, etype, step_limit, step_offset, count, len(rqs)
                samples += rqs
        return samples

