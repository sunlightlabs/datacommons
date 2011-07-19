#!/usr/bin/env python

import os, csv
from django.db import connection, transaction

class NicknameImporter(object):

    def set_base_path(self):
        filepath = os.path.abspath(__file__)
        self.path = os.path.split(filepath)[0]

    def download_or_update_source_file(self):
        if not os.path.join(self.path, 'apidata'):
            os.system('git clone git://github.com/sunlightlabs/apidata.git')
        else:
            os.system('cd apidata && git pull')

    def get_file_reader(self):
        legislators_file = os.path.join(self.path, 'apidata', 'legislators', 'legislators.csv')

        return csv.DictReader(open(legislators_file), dialect="excel")

    def parse(self, reader):
        nicknames_by_crp_id = []
        count = 0
        for row in reader:
            nicknames_by_crp_id.append((row['crp_id'], row['firstname'], row['nickname'], row['lastname']))
            count += 1

        print "{0} lines ready for import".format(count)
        return nicknames_by_crp_id

    @transaction.commit_manually
    def load(self, data):
        cursor = connection.cursor()

        cursor.execute("create temp table tmp_legislator_nicknames(entity_id varchar(32), crp_id varchar(24), first varchar(48), nick varchar(48), last varchar(48))")

        insert_sql = "insert into tmp_legislator_nicknames (crp_id, first, nick, last) values "
        insert_sql += ','.join(["('{0}', '{1}', '{2}', '{3}')".format(id, first, nick, last) for (id, first, nick, last) in data])
        cursor.execute(insert_sql)

        cursor.execute("update tmp_legislator_nicknames set entity_id = attr.entity_id from matchbox_entityattribute attr where (namespace in ('urn:crp:recipient')) and attr.value = crp_id")

        cursor.execute("select count(*) from matchbox_entityalias")
        num_before = cursor.fetchone()[0]

        cursor.execute("""
            insert into matchbox_entityalias (entity_id, alias)
                select
                    entity_id, nick || ' ' || last
                from
                    tmp_legislator_nicknames
                where
                    entity_id in (
                        select entity_id from tmp_legislator_nicknames where (entity_id, nick || ' ' || last) not in (select entity_id, alias from matchbox_entityalias) and entity_id is not null
                    )
                    and nick is not null and nick != ''

                 union

                select
                    entity_id, first || ' ' || last, 't'::boolean
                from
                    tmp_legislator_nicknames
                where
                    entity_id in (
                        select entity_id from tmp_legislator_nicknames where (entity_id, first || ' ' || last) not in (select entity_id, alias from matchbox_entityalias) and entity_id is not null
                    )
        """)

        cursor.execute("select count(*) from matchbox_entityalias")
        num_after = cursor.fetchone()[0]
        print "Aliases gained: {0}".format(num_after - num_before)

        transaction.commit()

    def run(self):
        #prepare
        self.set_base_path()
        self.download_or_update_source_file()
        #parse
        reader = self.get_file_reader()
        data = self.parse(reader)
        #load
        self.load(data)


if __name__ == '__main__': NicknameImporter().run()
