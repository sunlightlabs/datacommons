import os, sys, urllib, tempfile, os.path
from optparse import make_option
from datetime import datetime
from django.core.exceptions import ImproperlyConfigured
from dcentity.models import WikipediaInfo, SunlightInfo

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

try:
    import boto
    from boto.s3.key import Key
except ImportError:
    raise ImproperlyConfigured, "Could not load Boto's S3 bindings. See http://code.google.com/p/boto/"

def progress(complete, total):
    sys.stdout.write('Uploaded %s bytes of %s (%s%%)\n' % (complete, total, int(100*complete/total)))

class AppURLopener(urllib.FancyURLopener):
    version = "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.2b4) Gecko/20091124 Firefox/3.6b4"

class Command(BaseCommand):
    args = "<filename>"
    help = "Uploads a bulk file to S3."

    def handle(self, **options):
        self.conf = getattr(settings, 'MEDIASYNC', None)
        if not self.conf:
            raise ImproperlyConfigured("No MEDIASYNC setting found.")

        # change the user-agent string so that wikipedia will allow us in.
        urllib._urlopener = AppURLopener()

        sys.stdout.write('Connecting to S3...\n')
        self.conn = boto.connect_s3(self.conf['AWS_KEY'], self.conf['AWS_SECRET'])
        self.bucket = self.conn.get_bucket(self.conf['AWS_BUCKET'])

        #for wp_info in WikipediaInfo.objects.filter(entity__type='organization').exclude(photo_url__isnull=True).exclude(photo_url=''):
        for wp_info in WikipediaInfo.objects.filter(entity__type='organization').exclude(photo_url__isnull=True).exclude(photo_url='').exclude(entity__sunlight_info__photo_url__isnull=False):
            wikipedia_url = wp_info.photo_url
            s3_url = self.get_s3_url(wikipedia_url)

            try:
                self.upload_file(s3_url, wikipedia_url, options)
            except:
                sys.stdout.write('Error uploading.')
                continue

            sys.stdout.write('Setting photo_url on SunlightInfo...\n')
            entity = wp_info.entity
            sunlight_info = SunlightInfo.objects.get_or_create(entity=wp_info.entity)[0]
            sunlight_info.photo_url = os.path.join('https://s3.amazonaws.com/assets.transparencydata.org', urllib.pathname2url(s3_url))
            sunlight_info.save()
            sys.stdout.write('Done.\n')


    def get_s3_url(self, wiki_url):
        prefix = 'resources/images/corporate_logos'
        upload_basename = urllib.unquote(os.path.basename(wiki_url))
        return os.path.join(prefix, upload_basename)


    def upload_file(self, s3_url, wiki_url, options):
        # open the wikipedia file
        local_filename = os.path.basename(s3_url)
        filename, headers = urllib.urlretrieve(wiki_url, os.path.join('/tmp', local_filename))
        print local_filename
        print os.path.getsize(filename)
        print headers.gettype()

        file_handle = open(filename, 'rb')
        #meta = remote_file.info()
        #content_type = meta.gettype()

        #sys.stdout.write(u"Preparing to upload {0} to path {1}...\n".format(local_filename.decode('utf-8'), s3_url))

        k = Key(self.bucket)
        k.key = s3_url

        sys.stdout.write('Uploading...\n')
        k.set_contents_from_file(file_handle, cb=progress, num_cb=20)
        k.make_public()

        sys.stdout.write('Upload complete.\n')

        return os.path.join(self.conf['AWS_BUCKET'], s3_url)


