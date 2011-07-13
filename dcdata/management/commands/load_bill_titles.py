from dcdata.lobbying.models import Bill, BillTitle
from django.core.management.base import BaseCommand
from django.db import transaction
from optparse import make_option
import os.path
import urllib2
import urllib
try:
    import json
except:
    import simplejson as json


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option("-b", "--begin_at", dest="begin_at", help="Begin at a particular count", metavar="INTEGER"),
    )

    @transaction.autocommit
    def handle(self, *args, **options):
        print 'Starting...'
        unique_bills = Bill.objects.exclude(bill_type__isnull=True).filter(congress_no__gt=108).values('congress_no', 'bill_type', 'bill_no').distinct()
        unique_bills_count = unique_bills.count()

        for i, bill in enumerate(unique_bills):
            print i+1
            if i + 1 < int(options['begin_at']):
                continue
            url = self.format_url('http://www.opencongress.org/api/bills', congress=bill['congress_no'], type=bill['bill_type'], number=bill['bill_no'])
            print "{0}/{1}: {2}".format(i + 1, unique_bills_count, url)
            json = self.get_url_json(url)

            title = ''

            if json.has_key('bills'):
                titles = json['bills'][0]['bill_titles']
                title = self.get_right_title(titles)

            print '------> {0}'.format(title)

            BillTitle.objects.create(
                congress_no=bill['congress_no'],
                bill_type=bill['bill_type'],
                bill_no=bill['bill_no'],
                title=title
            )


    def get_url_json(self, path):
        try:
            fp = urllib2.urlopen(path)
            return json.loads(fp.read())
        except urllib2.HTTPError, e:
            if e.code == 404:
                raise Http404
            else:
                #retry once
                try:
                    fp = urllib2.urlopen(path)
                    return json.loads(fp.read())
                except urllib2.HTTPError, e:
                    raise e


    def get_right_title(self, titles):
        preferred_titles = [ x for x in titles if x['title_type'] == 'short' or x['is_default'] ]

        if not len(preferred_titles): return ''

        default_first = sorted(preferred_titles, lambda x,y: cmp(x['is_default'], y['is_default']), reverse=True)
        short_and_default_first = sorted(default_first, lambda x,y: cmp(x['title_type'], y['title_type']), reverse=True)

        return short_and_default_first[0]['title']


    def format_url(self, path, **params):
        params.update({'key': 'a34dd813faff9072ff2753ff56bd2a1e73300976'})
        params.update({'format': 'json'})

        return '?'.join([path, urllib.urlencode(params)])

