#!/usr/bin/env python

import os
import MySQLdb

from settings import OTHER_DATABASES

from scripts.nimsp.common import CSV_SQL_MAPPING, SQL_DUMP_FILE
from optparse import make_option
from django.core.management.base import BaseCommand
    
    
class NIMSPDump2CSV(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("-o", "--outfile", dest="outfile", help="csv file to create (default %s)" % SQL_DUMP_FILE),
        make_option("-c", "--cycle", dest="cycle", metavar='YYYY',
                          help="cycle to process (default all)"),
        make_option("-n", "--number", dest="n", metavar='ROWS',
                          help="number of rows to process"),
        make_option("-b", "--verbose", action='store_true', dest="verbose", 
                          help="noisy output"))
    
    def handle(self, **options):
        
        outfile = os.path.abspath(options['outfile']) if 'outfile' in options and options['outfile'] else  os.path.abspath(SQL_DUMP_FILE)
    
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
                   outfile)
       
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

