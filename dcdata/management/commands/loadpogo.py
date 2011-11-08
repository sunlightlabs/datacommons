from dcdata.pogo.models import Contractor, Misconduct
from django.core.management.base import BaseCommand
from django.db import transaction

import os.path
import csv
import re
from datetime import datetime

CONTRACTORS_FIELDS = 'contractor url'.split()
INSTANCES_FIELDS = 'contractor instance penalty_amount contracting_party court_type date year date_significance disposition enforcement_agency misconduct_type synopsis url'.split()


class Command(BaseCommand):

    @transaction.commit_on_success
    def handle(self, contractors_file, misconduct_file, **options):
        contractors_reader = csv.DictReader(open(os.path.abspath(contractors_file), 'r'))

        for row in contractors_reader:
            # TODO: This can take over the regex processing to get contractor_ext_id from the URL
            # (currently being done in a one-off SQL script)
            contractor_ext_id = re.search(r'ContractorID=(\d+)', row['URL']).groups()[0]
            Contractor.objects.create(
                name = row['Contractor'],
                url = row['URL'],
                contractor_ext_id = contractor_ext_id,
            )


        instances_reader = csv.DictReader(open(os.path.abspath(misconduct_file), 'r'))

        for row in instances_reader:
            print row
            contractor = Contractor.objects.get(name=row['Contractor'])
            penalty_amount = row['Misconduct Penalty Amount'] or 0
            Misconduct.objects.create(
                contractor=contractor,
                instance=row['Instance'],
                penalty_amount=penalty_amount,
                contracting_party=row['Contracting Party'],
                court_type=row['Court Type'],
                date=datetime.strptime(row['Date'],'%m/%d/%Y'),
                date_year=row['Year'],
                date_significance=row['Significance of Date'],
                disposition=row['Disposition'],
                enforcement_agency=row['Enforcement Agency'],
                misconduct_type=row['Misconduct Type'],
                synopsis=row['Synopsis'],
                url=row['URL']
            )

        print 'Contractors created: {0}'.format(Contractor.objects.count())
        print 'Incidents created: {0}'.format(Misconduct.objects.count())

