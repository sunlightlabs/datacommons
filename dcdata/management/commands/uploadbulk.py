import os, sys
from optparse import make_option
from datetime import datetime

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand

try:
    import boto
    from boto.s3.key import Key
except ImportError:
    raise ImproperlyConfigured, "Could not load Boto's S3 bindings. See http://code.google.com/p/boto/"

def progress(complete, total):
    sys.stdout.write('Uploaded %s bytes of %s (%s%%)\n' % (complete, total, int(100*complete/total)))

class Command(BaseCommand):
    args = "<filename>"
    help = "Uploads a bulk file to S3."
    option_list = BaseCommand.option_list + (
        make_option('-z', '--zip', action='store_true', dest='zip', default=False, help='Compress the file using zip (caution: compressed file will be stored in-memory)'),
    )
    
    def handle(self, *files, **options):
        conf = getattr(settings, 'BULKDATA', None)
        if not conf:
            raise ImproperlyConfigured("No BULKDATA setting found.")
        
        sys.stdout.write('Connecting to S3...\n')
        self.conn = boto.connect_s3(conf['AWS_KEY'], conf['AWS_SECRET'])
        self.bucket = self.conn.get_bucket(conf['AWS_BUCKET'])
        
        for file in files:
            self.upload_file(file, options)
    
    def upload_file(self, filename, options):
        conf = getattr(settings, 'BULKDATA', None)
        
        url = conf['AWS_PREFIX']
        try:
            url = url % datetime.now().strftime('%Y%m%d')
        except:
            pass

        
        # just the name of the uncompressed file that was passed in
        upload_filename = os.path.basename(filename)
        
        # the name it will have on S3 (uncompressed)
        url = os.path.join(url, upload_filename)

        if options['zip']:
            url = url + '.zip'
            upload_filename = upload_filename + '.zip'

        sys.stdout.write("Preparing to upload %s to path %s...\n" % (filename, url))
        if options['zip']:
            import zipfile

            sys.stdout.write("Compressing file...\n")
            zfile = zipfile.ZipFile(upload_filename, 'w', allowZip64=True)
            zfile.write(filename, compress_type=zipfile.ZIP_DEFLATED)
            zfile.close()

        upload = open(upload_filename)
        
        k = Key(self.bucket)
        k.key = url
        
        sys.stdout.write('Uploading...\n')
        k.set_contents_from_file(upload, cb=progress, num_cb=20)
        k.make_public()

        upload.close()
        
        sys.stdout.write('Upload complete.\n')
