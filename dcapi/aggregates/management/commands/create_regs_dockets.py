from django.core.management import BaseCommand, CommandError
from django.db import connection
import csv, re

def create_dockets(outfile):
    writer = csv.writer(outfile)
    writer.writerow(['docket_id', 'title', 'agency', 'date'])
    
    comment_cursor = connection.cursor()
    notice_cursor = connection.cursor()
    
    agency_splitter = re.compile("[-_]")
    
    comment_cursor.execute("select distinct docket_id from regulations_comments_full")
    for row in comment_cursor:
        docket_id = row[0]
        
        agency = agency_splitter.split(docket_id)[0]
        
        # see if there's a most-common commented-on thing
        notice_id = None
        notice_date = None
        
        notice_cursor.execute("""
            select on_id, count(on_id) as count from regulations_comments_full
            where docket_id = %s and on_id != ''
            group by on_id order by count desc limit 1
            """,
            [docket_id]
        )
        
        if notice_cursor.rowcount > 0:
            notice_row = notice_cursor.fetchone()
            notice_cursor.execute("select document_id, date_posted, title from regulations_comments_full where document_id = %s", [notice_row[0]])
            
            if notice_cursor.rowcount > 0:
                notice_row = notice_cursor.fetchone()
                notice_id = notice_row[0]
                notice_date = notice_row[1] if notice_row[1] else None
                notice_title = notice_row[2]
                print docket_id, 'succeeded with comment_on'
        
        # if that didn't work, look for the oldest notice or rule in the docket
        if notice_id is None:
            notice_cursor.execute("""
                select document_id, date_posted, title, type from regulations_comments_full
                where docket_id = %s and (type = 'notice' or type = 'rule' or type = 'proposed_rule')
                order by date_posted asc limit 1
                """,
                [docket_id]
            )
            if notice_cursor.rowcount > 0:
                notice_row = notice_cursor.fetchone()
                notice_id = notice_row[0]
                notice_date = notice_row[1] if notice_row[1] else None
                notice_title = notice_row[2]
                print docket_id, 'succeeded with oldest notice/rule/proposed'
        
        # if we still don't know, grab the oldest document in the docket to date it, and make up a name
        if notice_date is None:
            notice_cursor.execute("""
                select document_id, date_posted from regulations_comments_full where docket_id = 'OSHA-H048-2006-0823' order by date_posted asc limit 1;
                """,
                [docket_id]
            )
            notice_row = notice_cursor.fetchone()
            notice_date = notice_row[1]
        
        if notice_id is None:
            notice_title = 'Untitled %s docket (%s)' % (agency, docket_id)
            print docket_id, 'used oldest document and fake title'
        
        writer.writerow([docket_id, notice_title.encode('utf-8', 'ignore'), agency, notice_date])

class Command(BaseCommand):
    args = "<output_file>"
    
    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError("Exactly one argument is required.")
        
        file = open(args[0], 'wb')
        create_dockets(file)
        file.close()