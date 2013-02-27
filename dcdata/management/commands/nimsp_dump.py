#!/usr/bin/env python

import os
import MySQLdb

from django.conf import settings

from dcdata.scripts.nimsp.common import CSV_SQL_MAPPING, SQL_DUMP_FILE
from dcdata.management.base.nimsp_importer import BaseNimspImporter


class NIMSPDump2CSV(BaseNimspImporter):
    IN_DIR       = '/home/datacommons/data/auto/nimsp/dump/IN'
    DONE_DIR     = '/home/datacommons/data/auto/nimsp/dump/DONE'
    REJECTED_DIR = '/home/datacommons/data/auto/nimsp/dump/REJECTED'
    OUT_DIR      = '/home/datacommons/data/auto/nimsp/denormalized/IN'
    FILE_PATTERN = 'do_dump.txt'

    def __init__(self):
        super(NIMSPDump2CSV, self).__init__()


    def do_for_file(self, file_path):
        # The file and file_path arguments are irrelevant for this particular
        # script, since it's pulling all the data out of MySQL.
        # We'll just ignore them, except to archive the file when we're done.

        outfile_path = os.path.join(self.OUT_DIR, SQL_DUMP_FILE)

        select_fields = ",".join([sql_field for (name, sql_field, conversion_func) in CSV_SQL_MAPPING])

        create_indexes_stmt = """
            create index recipid_idx on Recipients (RecipientID);
            create index rrbid_idx on RecipientReportsBundle (RecipientReportsBundleID);
            create index syrid_idx on StateYearReports(StateYearReportsID);
            create index candid_idx on Candidates(CandidateID);
            create index osid_idx on OfficeSeats(OfficeSeatID);
            create index ocid_idx on OfficeCodes(OfficeCode);
            create index commid_idx on Committees(CommitteeID);
            create index ccid_idx on CatCodes(CatCode);
            create index p_candid_idx on PartyLookup(PartyLookupID );
        """

        stmt = """
            select %s
               from Contributions c
                   left outer join RecipientReportsBundle rrb on c.RecipientReportsBundleID = rrb.RecipientReportsBundleID
                   left outer join Recipients r on rrb.RecipientID = r.RecipientID
                   left outer join StateYearReports syr on rrb.StateYearReportsID = syr.StateYearReportsID
                   left outer join Candidates cand on r.CandidateID = cand.CandidateID
                   left outer join OfficeSeats os on cand.OfficeSeatID = os.OfficeSeatID
                   left outer join OfficeCodes oc on os.OfficeCode = oc.OfficeCode
                   left outer join Committees comm on r.CommitteeID = comm.CommitteeID
                   left outer join CatCodes cc on c.CatCode = cc.CatCode
                   left outer join PartyLookup p_cand on cand.PartyLookupID = p_cand.PartyLookupID
                   left outer join PartyLookup p_comm on comm.PartyLookupID = p_comm.PartyLookupID
                into outfile '%s'
                    fields terminated by ',' enclosed by '"'
                    lines terminated by '\\n'
            """ % (select_fields, outfile_path)

        connection = MySQLdb.connect(
            db=settings.OTHER_DATABASES['nimsp']['DATABASE_NAME'],
            user=OTHER_DATABASES['nimsp']['DATABASE_USER'],
            host=OTHER_DATABASES['nimsp']['DATABASE_HOST'] if 'DATABASE_HOST' in OTHER_DATABASES['nimsp'] else 'localhost',
            passwd=OTHER_DATABASES['nimsp']['DATABASE_PASSWORD'],
        )

        try:
            cursor = connection.cursor()
            self.log.info('Creating indexes...'.format(outfile_path))
            cursor.execute(create_indexes_stmt)
            cursor.close()
        except cursor.OperationalError as e:
            self.log.info('Tried to create database indexes but they already existed. Moving on.')
            self.log.info(e)

        cursor = connection.cursor()
        self.log.info('Dumping data to {0}...'.format(outfile_path))
        self.log.info(stmt)
        cursor.execute(stmt)
        cursor.close()
        self.log.info('Data dump complete.')

        self.archive_file(file_path, timestamp=True)


Command = NIMSPDump2CSV

