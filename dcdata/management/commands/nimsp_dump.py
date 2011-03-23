#!/usr/bin/env python

import os
import MySQLdb

from settings import OTHER_DATABASES

from dcdata.scripts.nimsp.common import CSV_SQL_MAPPING, SQL_DUMP_FILE
from dcdata.management.base.nimsp_importer import BaseNimspImporter


class NIMSPDump2CSV(BaseNimspImporter):
    IN_DIR       = '/home/datacommons/data/auto/nimsp/dump/IN'
    DONE_DIR     = '/home/datacommons/data/auto/nimsp/dump/DONE'
    REJECTED_DIR = '/home/datacommons/data/auto/nimsp/dump/REJECTED'
    OUT_DIR      = '/home/datacommons/data/auto/nimsp/denormalized/IN'
    FILE_PATTERN = 'do_dump.txt'

    LOG_PATH = '/home/datacommons/data/auto/log/nimsp_dump.log'


    def do_for_file(self, file, file_path):
        # The file and file_path arguments are irrelevant for this particular
        # script, since it's pulling all the data out of MySQL.
        # We'll just ignore them, except to archive the file when we're done.

        outfile_path = os.path.join(self.OUT_DIR, SQL_DUMP_FILE)

        select_fields = ",".join([sql_field for (name, sql_field, conversion_func) in CSV_SQL_MAPPING])

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
                where syr.Yearcode = ''
                into outfile '%s'
                    fields terminated by ',' enclosed by '"'
                    lines terminated by '\\n'
            """ % (select_fields, outfile_path)

        connection = MySQLdb.connect(
            db=OTHER_DATABASES['nimsp']['DATABASE_NAME'],
            user=OTHER_DATABASES['nimsp']['DATABASE_USER'],
            host=OTHER_DATABASES['nimsp']['DATABASE_HOST'] if 'DATABASE_HOST' in OTHER_DATABASES['nimsp'] else 'localhost',
            passwd=OTHER_DATABASES['nimsp']['DATABASE_PASSWORD'],
        )
        cursor = connection.cursor()

        self.log.info('Dumping data to {0}...'.format(outfile_path))
        cursor.execute(stmt)
        self.log.info('Data dump complete.')

        self.archive_file(file)


Command = NIMSPDump2CSV

