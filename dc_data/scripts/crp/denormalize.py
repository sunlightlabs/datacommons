#!/usr/bin/env python
from saucebrush.filters import Filter, UnicodeFilter
from dcdata.contribution.sources.crp import CYCLES, FILE_TYPES
import csv
import datetime
import logging
import os

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

def load_catcodes(dataroot):
    catcodes = { }
    fields = ('catcode','catname','catorder','industry','sector','sector_long')
    path = os.path.join(os.path.abspath(dataroot), 'raw', 'crp', 'CRP_Categories.txt')
    reader = csv.DictReader(open(path), fieldnames=fields, delimiter='\t')
    for _ in xrange(8):
        reader.next()
    for record in reader:
        catcodes[record.pop('catcode').upper()] = record
    return catcodes

def load_candidates(dataroot):
    candidates = { }
    fields = FILE_TYPES['cands']
    for cycle in CYCLES:
        path = os.path.join(os.path.abspath(dataroot), 'raw', 'crp', 'cands%s.csv' % cycle)
        reader = csv.DictReader(open(path), fieldnames=fields)
        for record in reader:
            key = "%s:%s" % (record.pop('cycle'), record.pop('cid').upper())
            del record['fec_cand_id']
            del record['dist_id_curr']
            del record['curr_cand']
            del record['cycle_cand']
            del record['no_pacs']
            candidates[key] = record
    return candidates

def load_committees(dataroot):
    committees = { }
    fields = FILE_TYPES['cmtes']
    for cycle in CYCLES:
        path = os.path.join(os.path.abspath(dataroot), 'raw', 'crp', 'cmtes%s.csv' % cycle)
        reader = csv.DictReader(open(path), fieldnames=fields)
        for record in reader:
            key = "%s:%s" % (record.pop('cycle'), record.pop('cmte_id').upper())
            del record['fec_cand_id']
            del record['source']
            del record['sensitive']
            del record['is_foreign']
            del record['active']
            committees[key] = record
    return committees

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