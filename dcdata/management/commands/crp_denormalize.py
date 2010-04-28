#!/usr/bin/env python
from saucebrush.filters import *
from dcdata.contribution.sources.crp import CYCLES, FILE_TYPES
import csv
import datetime
import logging
import os
from optparse import make_option
from django.core.management.base import CommandError, BaseCommand


FIELDNAMES = ['id', 'import_reference', 'cycle', 'transaction_namespace', 'transaction_id', 'transaction_type',
              'filing_id', 'is_amendment', 'amount', 'date', 'contributor_name', 'contributor_ext_id',
              'contributor_entity', 'contributor_type', 'contributor_occupation', 'contributor_employer',
              'contributor_gender', 'contributor_address', 'contributor_city', 'contributor_state',
              'contributor_zipcode', 'contributor_category', 'contributor_category_order',
              'organization_name', 'organization_ext_id', 'organization_entity', 'parent_organization_name', 'parent_organization_ext_id',
              'parent_organization_entity', 'recipient_name', 'recipient_ext_id', 'recipient_entity',
              'recipient_party', 'recipient_type', 'recipient_state', 'recipient_category', 'recipient_category_order',
              'committee_name', 'committee_ext_id', 'committee_entity', 'committee_party', 'election_type',
              'district', 'seat', 'seat_status', 'seat_result']

SPEC = dict(((fn, None) for fn in FIELDNAMES))


class RecipientFilter(Filter):
    def __init__(self, candidates, committees):
        super(RecipientFilter, self).__init__()
        self._candidates = candidates
        self._committees = committees
        
    def process_record(self, record):
        recip_id = record['recip_id'].strip().upper()
        if recip_id:
            if recip_id.startswith('N'):
                candidate = self._candidates.get('%s:%s' % (record['cycle'], recip_id), None)
                self.add_candidate_recipient(candidate, record)
            elif recip_id.startswith('C'):
                committee = self._committees.get('%s:%s' % (record['cycle'], recip_id), None)
                self.add_committee_recipient(committee, record)
        return record
        
    @staticmethod
    def get_recip_code_result(recip_code):
        recip_code = recip_code.strip().upper()
        return recip_code[1] if len(recip_code) >1 and recip_code[1] in ('W','L') else None
    
    @staticmethod
    def add_candidate_recipient(candidate, record):
        if candidate:
            record['recipient_name'] = candidate['first_last_p']
            record['recipient_party'] = candidate['party']
            record['recipient_type'] = 'politician'
            record['recipient_ext_id'] = candidate['cid']
            record['seat_status'] = candidate['crp_ico']
            record['seat_result'] = RecipientFilter.get_recip_code_result(candidate['recip_code'])
            seat = candidate['dist_id_run_for'].upper()
            if len(seat) == 4:
                if seat == 'PRES':
                    record['recipient_state'] = ''
                    record['seat'] = 'federal:president'
                else:
                    record['recipient_state'] = seat[0:2]
                    if seat[2] == 'S':
                        record['seat'] = 'federal:senate'
                    else:
                        record['seat'] = 'federal:house'
                        record['district'] = "%s-%s" % (seat[:2], seat[2:])
                        
    @staticmethod                    
    def add_committee_recipient(committee, record):
        if committee:
            record['recipient_name'] = committee['pac_short']
            record['recipient_party'] = committee['party']
            record['recipient_type'] = 'committee'
            record['seat_result'] = RecipientFilter.get_recip_code_result(committee['recip_code'])
            record['recipient_ext_id'] = committee['cmte_id']


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
        path = os.path.join(os.path.abspath(dataroot), 'raw', 'crp', 'cands%s.txt' % cycle)
        reader = csv.DictReader(open(path), fieldnames=fields, quotechar="|")
        for record in reader:
            key = "%s:%s" % (record.pop('cycle'), record['cid'].upper())
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
        path = os.path.join(os.path.abspath(dataroot), 'raw', 'crp', 'cmtes%s.txt' % cycle)
        reader = csv.DictReader(open(path), fieldnames=fields, quotechar="|")
        for record in reader:
            key = "%s:%s" % (record.pop('cycle'), record['cmte_id'].upper())
            del record['fec_cand_id']
            del record['source']
            del record['sensitive']
            del record['is_foreign']
            del record['active']
            committees[key] = record
    return committees


def parse_date_iso(date):
    pd = parse_date(date)
    if pd:
        return pd.isoformat()


def parse_date(date):
    if date:
        try:
            (m, d, y) = date.split('/')
            return datetime.date(int(y), int(m), int(d))
        except ValueError, ve:
            logging.warn("error parsing date: %s" % date)


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


class FECOccupationFilter(Filter):

    def process_record(self, record):

        if record['occ_ef'] and record['emp_ef']:
            record['contributor_occupation'] = record['occ_ef']
            record['contributor_employer'] = record['emp_ef']
        elif record['fec_occ_emp'].count('/') == 1:
            (emp, occ) = record['fec_occ_emp'].split('/')
            record['contributor_occupation'] = occ
            record['contributor_employer'] = emp
        else:
            record['contributor_occupation'] = record['fec_occ_emp']

        return record


class CatCodeFilter(Filter):
    def __init__(self, prefix, catcodes, field='real_code'):
        self._prefix = prefix
        self._catcodes = catcodes
        self._field = field
    def process_record(self, record):
        catcode = record.get(self._field, '').upper()
        if len(catcode) == 5:
            record['%s_category' % self._prefix] = catcode
            if catcode in self._catcodes:
                record['%s_category_order' % self._prefix] = self._catcodes[catcode]['catorder'].upper()
        return record



class CRPDenormalizeBase(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("-c", "--cycles", dest="cycles", help="cycles to load ex: 90,92,08", metavar="CYCLES"),
        make_option("-d", "--dataroot", dest="dataroot", help="path to data directory", metavar="PATH"),
        make_option("-b", "--verbose", action="store_true", dest="verbose", default=False, help="noisy output"))

    def handle(self, *args, **options):
        if 'dataroot' not in options:
            raise CommandError("path to dataroot is required")
    
        cycles = []
        if 'cycles' in options and options['cycles']:
            for cycle in options['cycles'].split(','):
                if len(cycle) == 4:
                    cycle = cycle[2:4]
                if cycle in CYCLES:
                    cycles.append(cycle)
        else:
            cycles = CYCLES
        
        dataroot = os.path.abspath(options['dataroot'])
    
        print "Loading catcodes..."
        catcodes = load_catcodes(dataroot)
        
        print "Loading candidates..."
        candidates = load_candidates(dataroot)
        
        print "Loading committees..."
        committees = load_committees(dataroot)
        
        self.denormalize(dataroot, cycles, catcodes, candidates, committees)
                 
    # to be implemented by subclasses
    def denormalize(self, root_path, cycles, catcodes, candidates, committees):
        raise NotImplementedError
    
    
class CRPDenormalizeAll(CRPDenormalizeBase):
    
    def denormalize(self, data_path, cycles, catcodes, candidates, committees):
        from dcdata.management.commands.crp_denormalize_individuals import CRPDenormalizeIndividual
        from dcdata.management.commands.crp_denormalize_pac2candidate import CRPDenormalizePac2Candidate
        from dcdata.management.commands.crp_denormalize_pac2pac import CRPDenormalizePac2Pac
                
        CRPDenormalizeIndividual().denormalize(data_path, cycles, catcodes, candidates, committees)
        CRPDenormalizePac2Candidate().denormalize(data_path, cycles, catcodes, candidates, committees)
        CRPDenormalizePac2Pac().denormalize(data_path, cycles, catcodes, candidates, committees)
        
Command = CRPDenormalizeAll