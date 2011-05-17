from django.core.management.base import BaseCommand, CommandError
import scrapelib
from lxml.html import document_fromstring
from lxml.cssselect import CSSSelector as css
import csv
import sys
import os
import urlparse
import re
from BeautifulSoup import UnicodeDammit

# CSV fields
CONTRACTOR_FIELDS = [
    'Contractor',
    'URL'
]
INSTANCE_FIELDS = [
    'Contractor',
    'Instance',
    'Misconduct Penalty Amount',
    'Contracting Party',
    'Court Type',
    'Date',
    'Year',
    'Significance of Date',
    'Disposition',
    'Enforcement Agency',
    'Misconduct Type',
    'Synopsis',
    'URL'
]

DOLLARS = re.compile(r'^\$[\d,]+$')

def sanitize(text):
    # munge out smart quotes
    text = re.sub(u'[\u2018\u2019]', "'", text)
    text = re.sub(u'[\u201c\u201d]', '"', text)
    text = text.replace(u'\xa0', ' ').replace(u' \u2013', ':')
    return text.encode('ascii', 'ignore')

class Command(BaseCommand):
    args = '<directory>'
    
    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError("Please specify a directory.")
        directory = args[0]
        
        if not os.path.exists(directory):
            os.mkdir(directory)
        
        # start scraper
        scraper = scrapelib.Scraper(requests_per_minute=60, allow_cookies=True, follow_robots=True)
        
        # open contractor CSV
        contractor_file = open(os.path.join(directory, 'contractors.csv'), 'wb')
        contractor_csv = csv.DictWriter(contractor_file, CONTRACTOR_FIELDS, restval='', extrasaction='ignore')
        contractor_csv.writer.writerow(CONTRACTOR_FIELDS)
        
        # first grab overall search page
        print 'Scraping main listing...'
        overall_text = scraper.urlopen("http://www.contractormisconduct.org/index.cfm/1,73,224,html?pnContractorID=0&pstDispositionTypeID=0&prtCourtTypeID=0&mcType=0&eaType=0&ContractType=0&dollarAmt=-1%2F-1&dateFrom=01%2F01%2F1985&dateTo=01%2F01%2F2025&submit=sort")
        overall_doc = document_fromstring(overall_text)
        
        # enumerate the organizations
        for org_option in css('select[name=pnContractorID] option')(overall_doc):
            if org_option.attrib['value'] != '0':
                contractor_csv.writerow({
                    'Contractor': org_option.text,
                    'URL': 'http://www.contractormisconduct.org/index.cfm/1,73,221,html?ContractorID=%s' % org_option.attrib['value']
                })
        
        contractor_file.close()
        
        # open instance CSV
        instance_file = open(os.path.join(directory, 'instances.csv'), 'wb')
        instance_csv = csv.DictWriter(instance_file, INSTANCE_FIELDS, restval='', extrasaction='ignore')
        instance_csv.writer.writerow(INSTANCE_FIELDS)
        
        # iterate over links from main page and grab their data
        links = css('td.caseRow a')(overall_doc)
        for i in range(len(links)):
            link = links[i]
            
            url = urlparse.urljoin("http://www.contractormisconduct.org/index.cfm/1,73,224,html", link.attrib['href'])
            
            print 'Scraping %s (%s of %s)' % (url, i + 1, len(links))
            
            instance_text = scraper.urlopen(url)
            instance_doc = document_fromstring(UnicodeDammit(instance_text, isHTML=True).unicode)
            
            row = {
                'Contractor': css('#primecontent > h2')(instance_doc)[0].text,
                'Instance': sanitize(css('#incident > h2')(instance_doc)[0].text),
                'URL': url
            }
            
            for field in css('#incident > p > strong')(instance_doc):
                field_name = field.text.replace(':', '')
                field_contents = sanitize(field.tail.strip())
                
                if field_name == 'Date':
                    date_parts = field_contents.split(None, 1)
                    row['Date'] = date_parts[0]
                    row['Year'] = row['Date'].split('/')[-1]
                    row['Significance of Date'] = date_parts[1][1:-1] if len(date_parts) > 1 else ''
                elif field_name == 'Amount':
                    row['Misconduct Penalty Amount'] = field_contents.replace('$', '').replace(',', '') if DOLLARS.match(field_contents) else ''
                else:
                    row[field_name] = field_contents
            
            instance_csv.writerow(row)
        
        instance_file.close()