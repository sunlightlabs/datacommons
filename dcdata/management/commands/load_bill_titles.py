from dcdata.lobbying.models import Bill, BillTitle
from django.core.management.base import BaseCommand
from django.db import transaction
from optparse import make_option
from time import sleep
import os.path
import urllib2
import urllib
try:
    import json
except:
    import simplejson as json


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option("-b", "--begin_at", dest="begin_at", help="Begin at a particular count", metavar="INTEGER", default=1),
    )

    @transaction.autocommit
    def handle(self, *args, **options):
        print 'Starting...'
        unique_bills = Bill.objects.exclude(bill_type__isnull=True) \
                .filter(congress_no__gt=108) \
                .extra(where=['(congress_no, bill_type, bill_no) not in (select congress_no, bill_type, bill_no from lobbying_billtitle)']) \
                .values('congress_no', 'bill_type', 'bill_no') \
                .distinct()
        unique_bills_count = unique_bills.count()

        for i, bill in enumerate(unique_bills):
            print i+1
            if i + 1 < int(options['begin_at']):
                continue
            url = self.format_url('http://api.opencongress.org/bills', congress=bill['congress_no'], type=bill['bill_type'], number=bill['bill_no'])
            print "{0}/{1}: {2}".format(i + 1, unique_bills_count, url)
            json = self.get_url_json(url)

            title = ''

            if json.get('total_pages', 0) > 0:
                title = self.get_right_title(json['bills'][0]['bill'])

            print '------> {0}'.format(title)

            BillTitle.objects.create(
                congress_no=bill['congress_no'],
                bill_type=bill['bill_type'],
                bill_no=bill['bill_no'],
                title=title[:255]
            )
            sleep(0.5)


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


    def get_right_title(self, bill):
        titles = bill.get('bill_titles')
        if titles:
            preferred_titles = [ x for x in titles if x['title_type'] == 'short' or x['is_default'] ]

            if not len(preferred_titles): return ''

            default_first = sorted(preferred_titles, lambda x,y: cmp(x['is_default'], y['is_default']), reverse=True)
            short_and_default_first = sorted(default_first, lambda x,y: cmp(x['title_type'], y['title_type']), reverse=True)

            return short_and_default_first[0]['title']
        else:
            return bill.get('title_common', bill.get('title_full_common'))


    def format_url(self, path, **params):
        params.update({'key': 'a34dd813faff9072ff2753ff56bd2a1e73300976'})
        params.update({'format': 'json'})

        return '?'.join([path, urllib.urlencode(params)])

