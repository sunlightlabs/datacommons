from django.core.management.base import BaseCommand, CommandError
from django.db import connections, transaction
import csv

class Command(BaseCommand):

    @transaction.commit_manually()
    def handle(self, *args, **options):
        # Takes any number of csv files. You'll probably have two,
        # one for individuals (lobbyists) and one for their employers
        results = []

        for filename in args:
            matches = csv.DictReader(open(filename, 'r'))
            required_fieldnames = ['name', 'delete', 'match_id', 'new_match_id']

            if set(matches.fieldnames) < set(required_fieldnames):
                print 'Didn\'t find the necessary field headers: {0}'.format(', '.join(required_fieldnames))
                print 'These are the headers on the file: {0}'.format(', '.join(matches.fieldnames))

            for row in matches:
                if row['delete'] or (float(row['confidence']) == -1 and not row['new_match_id']):
                    continue
                else:
                    name = row['name']
                    entity_id = row['new_match_id'] or row['match_id']

                    results.append((name, entity_id))

        conn = connections['default'].cursor()

        insert_values_str = ', '.join([ "(E'{}', '{}')".format(name.replace("'", "\\'"), entity_id) for (name, entity_id) in results ])

        sql = """
            --drop table if exists assoc_bundler_matches_manual;
            --create table assoc_bundler_matches_manual (
            --    name varchar(255),
            --    entity_id uuid
            --);
            insert into assoc_bundler_matches_manual (name, entity_id) values {};
        """.format(insert_values_str)

        print sql

        conn.execute(sql)
        transaction.commit()





