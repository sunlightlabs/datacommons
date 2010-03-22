#!/usr/bin/env python
import cookielib
import csv
import datetime
import logging
import os
import re
import urllib, urllib2
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

LOGIN_URL = "http://www.opensecrets.org/MyOS/index.php"
MYOSHOME_URL = "http://www.opensecrets.org/MyOS/home.php"
BULKDATA_URL = "http://www.opensecrets.org/MyOS/bulk.php"
DOWNLOAD_URL = "http://www.opensecrets.org/MyOS/download.php?f=%s"

REQUEST_HEADERS = {
    "User-Agent": "CRPPYDWNLDR v1.0 ~ CRP Python Downloader",
}

META_FIELDS = ['filename','ext','description','filesize','updated','url']

class CRPDownloader(object):
    
    def __init__(self, email, password, path=None):
        
        self.email = email
        self.password = password
        self.path = path or os.path.abspath(os.path.dirname(__file__))
        
        # setup opener
        self.opener = urllib2.build_opener(
            urllib2.HTTPCookieProcessor(
                cookielib.LWPCookieJar()
            )
        )
        
        self.meta = { }
        meta_path = os.path.join(self.path, 'meta.csv')
        if os.path.exists(meta_path):
            meta_file = open(meta_path, 'r')
            reader = csv.DictReader(meta_file, fieldnames=META_FIELDS)
            for record in reader:
                self.meta[record['url']] = record
            meta_file.close()
    
    def go(self, redownload=False):
        self._bulk_download(self.get_resources(), redownload)
    
    def _bulk_download(self, resources, redownload=False):
        
        meta_file = open(os.path.join(self.path, 'meta.csv'), 'w+')
        meta = csv.DictWriter(meta_file, fieldnames=META_FIELDS)
        
        for res in resources:
            
            if not redownload and res['url'] in self.meta:
                if res['updated'] == self.meta[res['url']]['updated']:
                    logging.info('ignoring %s.%s, local file is up to date' % (res['filename'], res['ext']))
                    meta.writerow(self.meta[res['url']])
                    continue
            
            file_path = os.path.join(self.path, "%s.%s" % (res['filename'], res['ext']))
            
            logging.info('downloading %s.%s' % (res['filename'], res['ext']))
            
            r = self.opener.open(res['url'])
                            
            outfile = open(file_path, 'w')
            outfile.write(r.read())
            outfile.close()
            
            res['filesize'] = "%iMB" % (os.path.getsize(file_path) / 1024 / 1024)
            
            meta.writerow(res)
        
        meta_file.close()
        
    def get_resources(self):
        
        now = datetime.datetime.now()
        updated = now.date().isoformat()
        
        resources = []
        
        # "visit" myos page and authenticate

        r = self.opener.open(LOGIN_URL)

        params = urllib.urlencode({'email': self.email, 'password': self.password, 'Submit': 'Log In'})
        r = self.opener.open(LOGIN_URL, params)

        # get bulk download url

        r = self.opener.open(BULKDATA_URL)

        DL_RE = re.compile(r'<li>\s*<a href="download.php\?f=(?P<filename>\w+)\.(?P<ext>\w{3})">(?P<description>.+?)</a>\s*(?P<filesize>\d{1,3}MB) -- Last updated: (?P<updated>\d{1,2}/\d{1,2}/\d{2})\s*</li>', re.I | re.M)

        for m in DL_RE.findall(r.read()):
    
            res = dict(zip(['filename','ext','description','filesize','updated'], m))
            res['url'] = DOWNLOAD_URL % "%s.%s" % (res['filename'], res['ext'])
            
            resources.append(res)  
        
        # PFD data range spreadsheet
        
        resources.append({
            'filename': 'CRP_PFDRangeData',
            'ext': 'xls',
            'description': 'PFD Range Data',
            'filesize': None,
            'updated': updated,
            'url': 'http://www.opensecrets.org/downloads/crp/CRP_PFDRangeData.xls',
        })    
        
        # CRP category codes
        
        resources.append({
            'filename': 'CRP_Categories',
            'ext': 'txt',
            'description': 'CRP Category Codes',
            'filesize': None,
            'updated': updated,
            'url': 'http://www.opensecrets.org/downloads/crp/CRP_Categories.txt',
        })    
        
        # a whole host of CRP IDs
        
        resources.append({
            'filename': 'CRP_IDs',
            'ext': 'xls',
            'description': 'CRP ID spreadsheet',
            'filesize': None,
            'updated': updated,
            'url': 'http://www.opensecrets.org/downloads/crp/CRP_IDs.xls',
        })
        
        return resources
    
class CRPDownloadCommand(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("-f", "--force", action="store_true", dest="force", default=False,
                          help="force re-download of all files"),
        make_option("-d", "--dataroot", dest="dataroot",
                          help="path to data directory", metavar="PATH"),
        make_option("-m", "--meta", action="store_true", dest="meta", default=False,
                          help="show the metadata for currently available CRP downloads"),
        make_option("-b", "--verbose", action="store_true", dest="verbose", default=False,
                          help="noisy output"))
    
    def handle(self, *args, **options):
        if 'dataroot' not in options:
            raise CommandError("path to dataroot is required")
        
        if options['meta']:
            
            dl = CRPDownloader('jcarbaugh@sunlightfoundation.com', '5unlight')
            for res in dl.get_resources():
                print res
        
        else:
            
            path = os.path.join(os.path.abspath(options['dataroot']), 'download', 'crp')
            
            if not os.path.exists(path):
                os.makedirs(path)
            
            dl = CRPDownloader('jcarbaugh@sunlightfoundation.com', '5unlight', path)
            dl.go(redownload=options['force'])

    
Command = CRPDownloadCommand