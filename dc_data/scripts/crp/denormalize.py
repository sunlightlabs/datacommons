#!/usr/bin/env python
from saucebrush.filters import Filter, UnicodeFilter
#from datacommons.sources.crp import CatCodeLookup
import datetime
import logging

FIELDNAMES = ['id', 'import_reference', 'cycle', 'transaction_namespace', 'transaction_id', 'transaction_type',
              'filing_id', 'is_amendment', 'amount', 'datestamp', 'contributor_name', 'contributor_urn',
              'contributor_entity', 'contributor_type', 'contributor_occupation', 'contributor_employer',
              'contributor_gender', 'contributor_address', 'contributor_city', 'contributor_state',
              'contributor_zipcode', 'contributor_category', 'contributor_category_order',
              'organization_name', 'organization_entity', 'parent_organization_name',
              'parent_organization_entity', 'recipient_name', 'recipient_urn', 'recipient_entity',
              'recipient_party', 'recipient_type', 'recipient_category', 'recipient_category_order',
              'committee_name', 'committee_urn', 'committee_entity',
              'committee_party', 'election_type', 'district', 'seat', 'seat_status',
              'seat_result',]

def parse_date_iso(datestamp):
    pd = parse_date(datestamp)
    if pd:
        return pd.isoformat()

def parse_date(datestamp):
    if datestamp:
        try:
            (m, d, y) = datestamp.split('/')
            return datetime.date(int(y), int(m), int(d))
        except ValueError, ve:
            logging.warn("error parsing datestamp: %s" % datestamp)

class SpecFilter(UnicodeFilter):
    def __init__(self, spec):
        super(SpecFilter, self).__init__()
        self._spec = spec
    def process_record(self, record):
        record = super(SpecFilter, self).process_record(record)
        spec = self._spec.copy()
        for key, value in record.iteritems():
            if key in spec:
                spec[key] = value
        return spec

class FECTransactionFilter(Filter):

    def __init__(self, id_field, type_field, cycle_field='cycle'):
        self._id_field = id_field
        self._type_field = type_field
        self._cycle_field = cycle_field

    def process_record(self, record):
        record['transaction_id'] = "FEC:%s:%s" % (record[self._cycle_field], record[self._id_field])
        record['transaction_type'] = "urn:ogdc:transaction:%s" % record[self._type_field].lower().strip()
        return record

class FECOccupationFilter(Filter):

    def process_record(self, record):

        if record['occ_ef'] and record['emp_ef']:
            record['contributor_occupation'] = record['occ_ef']
            record['contributor_employer'] = record['emp_ef']
        elif '/' in record['fec_occ_emp']:
            record['contributor_occupation'] = record['fec_occ_emp']
            #(emp, occ) = record['fec_occ_emp'].split('/', 1)
            #record['contributor_occupation'] = occ
            #record['contributor_employer'] = emp

        return record

class RealCodeFilter(Filter):

    def __init__(self, fieldname='real_code'):
        self._cache = CatCodeLookup('data/sqlite/crp/catcodes.db')
        self._fieldname = fieldname

    def process_record(self, record):

        if record[self._fieldname]:

            val = record[self._fieldname].upper()

            catcode = self._cache.get(val, None)

            if catcode:

                #record['industry'] = catcode['catcode'][0]
                #record['sector'] = catcode['catcode'][:2]
                record['category'] = catcode['catcode']
                record['category_order'] = catcode['catorder']

            return record