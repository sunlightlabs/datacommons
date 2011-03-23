#!/usr/bin/env python

import os
import MySQLdb

from settings import OTHER_DATABASES

from dcdata.scripts.nimsp.common import CSV_SQL_MAPPING, SQL_DUMP_FILE
from optparse import make_option
from django.core.management.base import BaseCommand
from dcdata.management.base.nimsp_importer import BaseNimspImporter


class NIMSPDump2CSV(BaseNimspImporter):
    option_list = BaseCommand.option_list + (
        make_option("-o", "--outfile", dest="outfile", help="path to csv file to create (default %s)" % SQL_DUMP_FILE),
        #make_option("-c", "--cycle", dest="cycle", metavar='YYYY',
                          #help="cycle to process (default all)"),
        #make_option("-n", "--number", dest="n", metavar='ROWS',
                          #help="number of rows to process"),
        make_option("-b", "--verbose", action='store_true', dest="verbose",
                          help="noisy output")
        make_option("-a", "--auto", dest="auto", action='store_true', help="Run with settings for automated load.", default=False)
    )

    IN_DIR       = '/home/datacommons/data/auto/nimsp/dump/IN'
    DONE_DIR     = '/home/datacommons/data/auto/nimsp/dump/DONE'
    REJECTED_DIR = '/home/datacommons/data/auto/nimsp/dump/REJECTED'
    OUT_DIR      = '/home/datacommons/data/auto/nimsp/denormalized/IN'
    FILE_PATTERN = 'do_dump.txt'

    LOG_PATH = '/home/datacommons/data/auto/log/nimsp_dump.log'


    def do_for_file(self, file, file_path):
        # The file and file_path arguments are irrelevant for this particular
        # script, since it's pulling all the data out of MySQL.
        # We'll just ignore them.

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
                %s
                %s
                into outfile '%s'
                    fields terminated by ',' enclosed by '"'
                    lines terminated by '\\n'
            """ % (select_fields,
                   ("where syr.Yearcode = %s" % options['cycle']) if 'cycle' in options and options['cycle'] else "",
                   ("limit %s" % options['n']) if 'n' in options and options['n'] else "",
                   outfile_path)

        connection = MySQLdb.connect(
            db=OTHER_DATABASES['nimsp']['DATABASE_NAME'],
            user=OTHER_DATABASES['nimsp']['DATABASE_USER'],
            host=OTHER_DATABASES['nimsp']['DATABASE_HOST'] if 'DATABASE_HOST' in OTHER_DATABASES['nimsp'] else 'localhost',
            passwd=OTHER_DATABASES['nimsp']['DATABASE_PASSWORD'],
        )
        cursor = connection.cursor()

        cursor.execute(stmt)

        # is there anything to print? Not sure
        for row in cursor:
            print row


Command = NIMSPDump2CSV

