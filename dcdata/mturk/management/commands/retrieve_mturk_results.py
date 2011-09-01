from django.core.management import BaseCommand, CommandError
import csv, os
from dcentity.models import Entity
from name_cleaver import *
from django.template import Template, Context
from django.db import connection
from optparse import make_option
from boto.mturk.question import QuestionForm
from boto.mturk.connection import MTurkConnection
from boto.mturk.qualification import Qualifications, PercentAssignmentsApprovedRequirement
import datetime, sys
from django.conf import settings

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-s', '--sandbox',
            action='store_true',
            dest='sandbox',
            default=False,
            help='Use the sandbox server instead of the production one.'),
        make_option('-F', '--filter',
            action='store',
            dest='filter',
            default=None,
            help='Specify one or more HIT properties to narrow the list of data you get back.')
    )
    
    def handle(self, *args, **options):
        # check args
        if len(args) != 1:
            raise CommandError("Please specify one argument.")
        
        # set up filters if there are any
        filters = {}
        if options['filter']:
            filter_list = options['filter'].split(',')
            for filter_item in filter_list:
                items = filter_item.strip().split('=')
                filters[items[0]] = items[1]
        
        # create a connection
        mturk = MTurkConnection(
            getattr(settings, 'MTURK_AWS_KEY', settings.MEDIASYNC['AWS_KEY']),
            getattr(settings, 'MTURK_AWS_SECRET', settings.MEDIASYNC['AWS_SECRET']),
            host = 'mechanicalturk.sandbox.amazonaws.com' if options['sandbox'] else 'mechanicalturk.amazonaws.com'
        )
        
        results = []
        workers = set()
        
        for hit in mturk.get_all_hits():
            # check filters
            if filters:
                if any ([getattr(hit, param, None) != filters[param] for param in filters.keys()]):
                    print 'Skipping hit %s for failure to match filters' % hit.HITId
                    continue
                
            
            row = {'td_id': hit.RequesterAnnotation, 'hit_id': hit.HITId}
            
            assignments = mturk.get_assignments(hit.HITId)
            
            answer_dict = {}
            for a in assignments:
                try:
                    answer_dict['worker_%s' % a.WorkerId] = dict(a.answers[0][0].fields)['is_match']
                    workers.add(a.WorkerId)
                except:
                    print 'Something weird happened with hit %s and worker %s' % (hit.HITId, a.WorkerId)
            
            row.update(answer_dict)
            
            row['num_assignments'] = len(answer_dict.keys())
            row['disagreement'] = len(answer_dict.keys()) > 1 and len(set(answer_dict.values())) > 1
            non_yes = [answer for answer in answer_dict.values() if answer != 'yes']
            row['any_non_yes'] = len(non_yes) > 0
            row['majority_non_yes'] = len(non_yes) >= row['num_assignments'] / 2.0
            
            if row['num_assignments'] < 3 or row['num_assignments'] != len(assignments):
                print 'Hit %s had %s successful assignments of %s attempted.' % (row['hit_id'], row['num_assignments'], len(assignments))
            
            results.append(row)
        
        writer_file = open(args[0], 'wb')
        
        fields = ['td_id', 'hit_id', 'num_assignments', 'disagreement', 'any_non_yes', 'majority_non_yes'] + ['worker_%s' % worker_id for worker_id in workers]
        writer = csv.DictWriter(writer_file, fields, restval='', extrasaction='ignore')
        writer.writeheader()
        
        for row in results:
            writer.writerow(row)