#!/usr/bin/env python
from dcdata.contribution.models import Contribution
from dcdata.contribution.sources.crp import CYCLES, FILE_TYPES
from django.core.management.base import CommandError, BaseCommand
from optparse import make_option
from saucebrush.filters import Filter, UnicodeFilter
import csv
import datetime
import logging
import os


FIELDNAMES = [field.name for field in Contribution._meta.fields]

SPEC = dict(((fn, '') for fn in FIELDNAMES))


class RecipientFilter(Filter):
    def __init__(self, candidates, committees):
        super(RecipientFilter, self).__init__()
        self._candidates = candidates
        self._committees = committees

    def add_recipient(self, record, committee):
        # cmte_id != recip_id indicates a candidate committee
        if committee['cmte_id'] != committee['recip_id']:
            candidate = self._candidates.get('%s:%s' % (record['cycle'], committee['fec_cand_id'].strip().upper()), None)
            if candidate:
                self.add_candidate_recipient(record, candidate, committee)
                return record
                
        self.add_committee_recipient(record, committee)    
        return record


    @staticmethod
    def get_recip_code_result(recip_code):
        recip_code = recip_code.strip().upper()
        return recip_code[1] if len(recip_code) > 1 and recip_code[1] in ('W','L') else ""

    @staticmethod
    def add_candidate_recipient(record, candidate, committee):
        record['recipient_name'] = candidate['first_last_p']
        record['recipient_party'] = candidate['party']
        record['recipient_type'] = 'P'
        record['recipient_category'] = committee['prim_code'] if committee else ''
        record['recipient_ext_id'] = candidate['cid']
        record['seat_status'] = candidate['crp_ico']
        record['seat_result'] = RecipientFilter.get_recip_code_result(candidate['recip_code']) if candidate['curr_cand'] and candidate['cycle_cand'] else ''

        (record['seat_held'], record['recipient_state_held'], record['district_held']) = RecipientFilter.parse_crp_seat(candidate['dist_id_curr'].strip()) if candidate['dist_id_curr'].strip() else ('', '', '')
        (record['seat'], record['recipient_state'], record['district']) = RecipientFilter.parse_fec_seat(candidate['fec_cand_id'])
        # FEC ID often has incorrect district, so fall back to CRP if CRP ID is also showing House
        if record['seat'] == 'federal:house':
            (crp_seat, crp_state, crp_district) = RecipientFilter.parse_crp_seat(candidate['dist_id_run_for'])
            if crp_seat == 'federal:house' and crp_state == record['recipient_state']:
                record['district'] = crp_district
                

    @staticmethod
    def parse_fec_seat(fec_id):
        if fec_id[0] == 'P':
            return ('federal:president', '', '')
        elif fec_id[0] == 'S':
            return ('federal:senate', fec_id[2:4], '')
        elif fec_id[0] == 'H':
            return ('federal:house', fec_id[2:4], fec_id[2:4] + '-' + fec_id[4:6])
        else:
            raise Exception('Unknown FEC ID: %s' % fec_id)

    @staticmethod
    def parse_crp_seat(seat):
        if len(seat.strip()) == 4:
            if seat == 'PRES':
                return ('federal:president', '', '')
            else:
                state = seat[0:2]
                if seat[2] == 'S':
                    return ('federal:senate', state, '')
                else:
                    # house seats are coded like ('MD04', 'NY10')
                    return ('federal:house', state, "%s-%s" % (seat[:2], seat[2:]))

    @staticmethod
    def add_committee_recipient(record, committee):
        record['recipient_name'] = committee['pac_short']
        record['recipient_party'] = committee['party']
        record['recipient_type'] = 'C'
        record['recipient_ext_id'] = committee['cmte_id']
        record['recipient_category'] = committee['prim_code']

        record['seat_status'] = ''
        record['seat_result'] = ''
        record['recipient_state'] = ''
        record['seat'] = ''
        record['district'] = ''
        record['recipient_state_held'] = ''
        record['seat_held'] = ''
        record['district_held'] = ''



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
    """return map of cycle:fecID -> record"""

    candidates = { }
    fields = FILE_TYPES['cands']

    for cycle in CYCLES:
        path = os.path.join(os.path.abspath(dataroot), 'raw', 'crp', 'cands%s.txt' % cycle)
        reader = csv.DictReader(open(path), fieldnames=fields, quotechar="|")

        for record in reader:
            key = "%s:%s" % (record.pop('cycle'), record['fec_cand_id'].upper())
            del record['no_pacs']

            if candidates.has_key(key) and not (record['curr_cand'] == 'Y' and record['cycle_cand'] == 'Y'):
                continue

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
        except ValueError:
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
            record['contributor_employer'] = ''

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
