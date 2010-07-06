from dcdata.contracts import *
from dcdata.contracts.models import Contract
from django.contrib.localflavor.us.us_states import STATES_NORMALIZED
from django.core.management.base import CommandError, BaseCommand
from optparse import make_option
from saucebrush import run_recipe
from saucebrush.emitters import Emitter, DebugEmitter, CSVEmitter
from saucebrush.filters import (
    Filter, FieldAdder, FieldModifier, FieldRenamer, FieldRemover, UnicodeFilter
)
import csv
import os
import sys
import MySQLdb
import MySQLdb.cursors

UNMODIFIED_FIELDS = ['fiscal_year','version','piid','parent_id','award_id']

MODEL_FPDS_MAPPING = {
    'id': 'record_id',
    'transaction_number': 'transactionNumber',
    'last_modified_date': 'lastModifiedDate',
    'modification_number': 'modNumber',
    'modification_reason': 'reasonForModification',
    'agency_id': 'agencyID',
    'contracting_agency_id': 'contractingOfficeAgencyID',
    'contracting_office_id': 'contractingOfficeID',
    'requesting_agency_id': 'fundingRequestingAgencyID',
    'requesting_office_id': 'fundingRequestingOfficeID',
    'major_program_code': 'majorProgramCode',
    'idv_agency_fee': 'feePaidForUseOfService',
    'cotr_name': 'COTRName',
    'cotr_other_name': 'alternateCOTRName',
    'contract_action_type': 'contractActionType',
    'contract_bundling_type': 'contractBundling',
    'contract_competitiveness': 'extentCompeted',
    'contract_description': 'descriptionOfContractRequirement',
    'contract_financing': 'contractFinancing',
    'contract_nia_code': 'nationalInterestActionCode',
    'contract_nocompete_reason': 'reasonNotCompeted',
    'contract_offers_received': 'numberOfOffersReceived',
    'contract_pricing_type': 'typeOfContractPricing',
    'contract_set_aside': 'typeOfSetAside',
    'subcontract_plan': 'subcontractPlan',
    'number_of_actions': 'numberOfActions',
    'consolidated_contract': 'consolidatedContract',
    'multiyear_contract': 'multiYearContract',
    'performance_based_contract': 'performanceBasedServiceContract',
    'signed_date': 'signedDate',
    'effective_date': 'effectiveDate',
    'completion_date': 'currentCompletionDate',
    'maximum_date': 'ultimateCompletionDate',
    'renewal_date': 'renewalDate',
    'cancellation_date': 'cancellationDate',
    'obligated_amount': 'obligatedAmount',
    'current_amount': 'baseAndExercisedOptionsValue',
    'maximum_amount': 'baseAndAllOptionsValue',
    'price_difference': 'priceEvaluationPercentDifference',
    'cost_data_obtained': 'costOrPricingData',
    'purchase_card_as_payment': 'purchaseCardAsPaymentMethod',
    'vendor_name': 'vendorName',
    'vendor_business_name': 'vendorDoingAsBusinessName',
    'vendor_employees': 'numberOfEmployees',
    'vendor_annual_revenue': 'annualRevenue',
    'vendor_street_address': 'streetAddress',
    'vendor_street_address2': 'streetAddress2',
    'vendor_street_address3': 'streetAddress3',
    'vendor_city': 'city',
    'vendor_state': 'state',
    'vendor_zipcode': 'ZIPCode',
    'vendor_district': 'vendor_cd',
    'vendor_country_code': 'vendorCountryCode',
    'vendor_duns': 'DUNSNumber',
    'vendor_parent_duns': 'parentDUNSNumber',
    'vender_phone': 'phoneNo',
    'vendor_fax': 'faxNo',
    'vendor_ccr_exception': 'CCRException',
    'place_district': 'congressionalDistrict',
    'place_location_code': 'locationCode',
    'place_state_code': 'stateCode',
    'product_origin_country': 'countryOfOrigin',
    'product_origin': 'placeOfManufacture',
    'producer_type': 'manufacturingOrganizationType',
    'statutory_authority': 'otherStatutoryAuthority',
    'product_service_code': 'productOrServiceCode',
    'naics_code': 'principalNAICSCode',
    'solicitation_id': 'solicitationID',
    'supports_goodness': 'contingencyHumanitarianPeacekeepingOperation',
    'dod_system_code': 'systemEquipmentCode',
    'it_commercial_availability': 'informationTechnologyCommercialItemCategory',
    'cas_clause': 'costAccountingStandardsClause',
    'recovered_material_clause': 'recoveredMaterialClauses',
    'fed_biz_opps': 'fedBizOpps',
    'government_property': 'GFE_GFP',
}

def state_abbr(name):
    abbr = STATES_NORMALIZED.get(name.strip().lower(), None)
    return abbr or ''

class CountEmitter(Emitter):

    def __init__(self, every=1000):
        super(Emitter, self).__init__()
        self.every = every
        self.count = 0

    def emit_record(self, record):
        self.count += 1
        if self.count % self.every == 0:
            print "%s records" % self.count

class ChoiceFilter(Filter):
    def __init__(self, model):
        super(ChoiceFilter, self).__init__()
        self.choice_fields = {}
        for field in model._meta.fields:
            if field.choices:
                self.choice_fields[field.name] = [c[0] for c in field.choices]
    def process_record(self, record):
        for key in record.iterkeys():
            if key in self.choice_fields:
                if record[key] is not None and record[key] not in self.choice_fields[key]:
                    record[key] = None
        return record

class MySQLSource(object):

    def __init__(self, query, host, username, password, db):
        self.conn = MySQLdb.connect(
            host=host,
            user=username,
            passwd=password,
            db=db,
            cursorclass=MySQLdb.cursors.SSDictCursor)
        self.query = query

    def __iter__(self):
        cur = self.conn.cursor()
        cur.execute(self.query)
        for record in cur:
            yield record
        cur.close()
    
    def done(self):
        self.conn.close()

class AgencyFilter(Filter):
    def __init__(self, agencies):
        super(AgencyFilter, self).__init__()
        self.agencies = agencies
    def process_record(self, record):
        if record['agency_id'] in self.agencies:
            record['agency_name'] = self.agencies[record['agency_id']]
        if record['contracting_agency_id'] in self.agencies:
            record['contracting_agency_name'] = self.agencies[record['contracting_agency_id']]        
        if record['requesting_agency_id'] in self.agencies:
            record['requesting_agency_name'] = self.agencies[record['requesting_agency_id']]
        return record

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option("-c", "--host", dest="host", help="MySQL host", metavar="HOST"),
        make_option("-d", "--database", dest="database", help="MySQL database", metavar="DATABASE"),
        make_option("-o", "--outfile", dest="outfile", help="CSV output file", metavar="PATH"),
        make_option("-p", "--password", dest="password", help="MySQL password", metavar="PASSWORD"),
        make_option("-u", "--username", dest="username", help="MySQL username", metavar="USERNAME"),
        make_option("-y", "--year", dest="year", help="fiscal year to load", metavar="YEAR"),
        make_option("--agencies", dest="agencies_path", help="agencies CSV", metavar="PATH"),
    )
    
    def handle(self, *args, **options):

        for required in ('username','outfile','year'):
            if required not in options or options[required] is None:
                raise CommandError("%s argument is required" % required)
                
        if 'outfile' in options and options['outfile']:
            outfile = open(os.path.abspath(options['outfile']), 'w')
        else:
            outfile = sys.stdout
        outfields = [field.name for field in Contract._meta.fields]
        unused_fields = list(set(FPDS_FIELDS) - set(MODEL_FPDS_MAPPING.values() + UNMODIFIED_FIELDS))
        
        agency_mapping = {}
        if options['agencies_path']:
            for rec in csv.DictReader(open(os.path.abspath(options['agencies_path']))):
                agency_mapping[rec['id']] = rec['name']
        
        query = """SELECT * FROM fpds_award3_sunlight"""
        if options['year']:
            query = "%s WHERE fiscal_year = %s" % (query, int(options['year']))
        
        #query += " LIMIT 1000"
        
        mysql_params = {
            'query': query,
            'db': options['database'] or 'fpds',
            'username': options['username'],
            'password': options['password'] or '',
            'host': options['host'] or 'localhost',
        }
        
        run_recipe(
            MySQLSource(**mysql_params),
            FieldRemover(unused_fields),
            FieldAdder('agency_name', None),
            FieldAdder('requesting_agency_name', None),
            FieldAdder('contracting_agency_name', None),
            FieldRenamer(MODEL_FPDS_MAPPING),
            FieldModifier(('place_state_code', 'vendor_state'), state_abbr),
            AgencyFilter(agency_mapping),
            ChoiceFilter(Contract),
            UnicodeFilter(),
            #CountEmitter(every=1000),
            CSVEmitter(outfile, fieldnames=outfields),
        )