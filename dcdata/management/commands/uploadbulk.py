import os, sys, math
from optparse import make_option
from datetime import datetime

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

def progress(complete, total):
    sys.stdout.write('Uploaded %s bytes of %s (%s%%)\n' % (complete, total, int(100*complete/total)))

class Command(BaseCommand):
    args = "<filename> [<upload_filename>]"
    help = "Uploads a bulk file to S3."
    option_list = BaseCommand.option_list + (
        make_option('-z', '--gzip', action='store_true', dest='gzip', default=False, help='Compress the file using gzip (caution: compressed file will be stored in-memory)'),
    )
    
    def handle(self, filename, upload_filename='', *args, **options):
        try:
            import boto
            from boto.s3.key import Key
        except ImportError:
            raise ImproperlyConfigured, "Could not load Boto's S3 bindings. See http://code.google.com/p/boto/"
        
        conf = getattr(settings, 'BULKDATA', None)
        if not conf:
            raise ImproperlyConfigured("No BULKDATA setting found.")
        
        url = conf['AWS_PREFIX']
        try:
            url = url % datetime.now().strftime('%Y%m%d')
        except:
            pass

        if not upload_filename:
            upload_filename = os.path.basename(filename)
        
        url = os.path.join(url, upload_filename)
        
        file = open(filename)
        
        sys.stdout.write("Preparing to upload %s to path %s...\n" % (filename, url))
        if options['gzip']:
            from gzip import GzipFile
            
            sys.stdout.write("Compressing file...\n")
            upload = StringIO()
            zfile = GzipFile(mode='wb', fileobj=upload)
            zfile.writelines(file)
            zfile.close()
            file.close()
        else:
            upload = file
        
        sys.stdout.write('Connecting to S3...\n')
        conn = boto.connect_s3(conf['AWS_KEY'], conf['AWS_SECRET'])
        bucket = conn.get_bucket(conf['AWS_BUCKET'])
        k = Key(bucket)
        k.key = url
        
        sys.stdout.write('Uploading...\n')
        k.set_contents_from_file(upload, cb=progress, num_cb=20)
        k.make_public()
        
        sys.stdout.write('Upload complete.\n')