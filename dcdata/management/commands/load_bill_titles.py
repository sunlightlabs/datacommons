from dcdata.lobbying.models import Bill, BillTitle
from django.core.management.base import BaseCommand
from django.db import transaction
import os.path
import urllib2
import urllib
try:
    import json
except:
    import simplejson as json


class Command(BaseCommand):

    @transaction.autocommit
    def handle(self, *args, **options):
        unique_bills = Bill.objects.exclude(bill_type__isnull=True).filter(congress_no__gt=108).values('congress_no', 'bill_type', 'bill_no').distinct()
        unique_bills_count = unique_bills.count()

        i = 1
        for bill in unique_bills:
            url = self.format_url('http://www.opencongress.org/api/bills', congress=bill['congress_no'], type=bill['bill_type'], number=bill['bill_no'])
            print "{0}/{1}: {2}".format(i, unique_bills_count, url)
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

            i = i + 1


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

