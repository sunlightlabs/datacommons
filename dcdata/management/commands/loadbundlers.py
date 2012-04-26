from django.core.management.base import BaseCommand, CommandError
from django.core     import management
from optparse import make_option
from saucebrush import run_recipe
from saucebrush.sources import CSVSource
from saucebrush.filters import Filter, FieldRenamer, FieldModifier, \
    FieldRemover, UnicodeFilter, FieldCopier
from saucebrush.emitters import DjangoModelEmitter, DebugEmitter
from dcdata.contribution.models import Bundle, LobbyistBundle
from dcdata.management.commands.util import NoneFilter, CountEmitter, \
    TableHandler
from datetime import datetime


import os

class BundleFilter(Filter):
    def __init__(self):
        self._cache = {}
    def process_record(self, record):
        bundle_id = record['file_num']
        bundle = self._cache.get(bundle_id, None)
        if bundle is None:
            try:
                print "loading bundle %s from database" % bundle_id
                bundle = Bundle.objects.get(pk=bundle_id)
                self._cache[bundle_id] = bundle
                print "\t* loaded"
            except Bundle.DoesNotExist:
                #pass
                print "\t* does not exist"
        if bundle:
            record['file_num'] = bundle
            return record


class BundleHandler(TableHandler):
    field_map = dict(
        file_num = 'FILE_NUM',
        committee_fec_id = 'CMTE_ID',
        committee_name = 'CMTE_NM',
        first_image_num = 'BEGIN_IMAGE_NUM',
        report_year = 'RPT_YR',
        report_type = 'RPT_TP',
        is_amendment = 'AMNDT_IND',# still need to modify/add boolean is_amendment from this
        report_type_description = 'RPT_TP_DESC',
        start_date = 'CVG_START_DT',
        end_date = 'CVG_END_DT',
        reporting_period_amount = 'QTR_MON_BUNDLED_CONTB',
        semi_annual_amount = 'SEMI_AN_BUNDLED_CONTB',
        filing_date = 'RECEIPT_DT',
    )

    def __init__(self, inpath):
        super(BundleHandler, self).__init__(inpath)
        self.db_table = 'contribution_bundle'

    def run(self):
        run_recipe(
            CSVSource(open(self.inpath)),
            FieldRenamer(self.field_map),
            # Values are [N|A]. Convert to boolean.
            FieldModifier('is_amendment', \
                    lambda x: x == 'A'),
            # Convert any stray floats to integers
            FieldModifier('reporting_period_amount semi_annual_amount'.split(), \
                    lambda x: int(round(float(x))) if x else None),
            # Convert date formats
            FieldModifier('start_date end_date filing_date'.split(), \
                    lambda x: datetime.strptime(x, '%m/%d/%Y') if x else None),
            # TODO: These following two lines (and the field value) need to be thoroughly tested on the next bundling load
            FieldCopier({'pdf_url': 'first_image_num'}),
            FieldModifier('pdf_url', \
                    lambda x: 'http://query.nictusa.com/pdf/{0}/{1}/{1}.pdf'.format(x[-3:], x)),
            NoneFilter(),
            UnicodeFilter(),
            CountEmitter(every=200),
            #DebugEmitter(),
            DjangoModelEmitter('settings', Bundle)
        )



class LobbyistBundleHandler(TableHandler):
    field_map = dict(
        file_num = 'FILE_NUM',
        committee_fec_id = 'CMTE_ID',
        committee_name = 'CMTE_NM',
        image_num = 'IMAGE_NUM',
        report_year = 'RPT_YR',
        report_type = 'RPT_TP',
        is_amendment = 'AMNDT_IND',# still need to modify/add boolean is_amendment from this
        contributor_fec_id = 'CONTBR_ID',
        name = 'CONTBR_NM',
        street_addr1 = 'CONTBR_ST1',
        street_addr2 = 'CONTBR_ST2',
        city = 'CONTBR_CITY',
        state = 'CONTBR_ST',
        zip_code = 'CONTBR_ZIP',
        employer = 'CONTBR_EMPLOYER',
        occupation = 'CONTBR_OCCUPATION',
        amount = 'CONTB_RECEIPT_AMT',
        semi_annual_amount = 'CONTB_AGGREGATE_YTD',
        reporting_period_amount_all = 'QTR_MON_BUNDLED_CONTB',
        semi_annual_amount_all = 'SEMI_AN_BUNDLED_CONTB',
        receipt_type = 'RECEIPT_TP',
    )

    def __init__(self, inpath):
        super(LobbyistBundleHandler, self).__init__(inpath)
        self.db_table = 'contribution_lobbyistbundle'

    def run(self):
        run_recipe(
            CSVSource(open(self.inpath)),
            FieldRenamer(self.field_map),
            FieldRemover('committee_fec_id committee_name report_year report_type is_amendment start_date end_date reporting_period_amount_all semi_annual_amount_all'.split()),
            BundleFilter(),
            #FieldModifier('file_num', lambda x: Bundle.objects.get(pk=x)),
            # Convert any stray floats to integers
            FieldModifier('amount semi_annual_amount'.split(), \
                    lambda x: int(round(float(x))) if x else None),
            NoneFilter(),
            UnicodeFilter(),
            CountEmitter(every=500),
            #DebugEmitter(),
            DjangoModelEmitter('settings', LobbyistBundle)
        )


class Command(BaseCommand):

    HANDLERS = (BundleHandler, LobbyistBundleHandler)

    option_list = BaseCommand.option_list + (
        make_option("-b", "--bundles", dest="bundle_file", help="bundle source file", metavar="FILE"),
        make_option("-l", "--lobbyists", dest="lobbyists_file", help="lobbyists source file", metavar="FILE"),
    )

    def handle(self, *args, **options):

        bundle_file = os.path.abspath(options['bundle_file'])
        lobbyists_file = os.path.abspath(options['lobbyists_file'])

        if not (bundle_file and lobbyists_file):
            raise CommandError, "Both file paths must exist"

        if not (os.path.exists(bundle_file) and os.path.exists(lobbyists_file)):
            raise CommandError, "Both file paths must exist"

        l_handler = LobbyistBundleHandler(lobbyists_file)
        l_handler.drop()

        b_handler = BundleHandler(bundle_file)
        b_handler.drop()

        print "Syncing database to recreate dropped tables:"
        management.call_command('syncdb', interactive=False)

        b_handler.run()
        l_handler.run()

