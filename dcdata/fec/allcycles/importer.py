from dcdata.fec.importer import *

cycles = '00 02 04 06 08 10 12'.split()

def cycle_config(cycle):
    return [
        F('ftp://ftp.fec.gov/FEC/20%s/indiv%s.zip' % (cycle, cycle), 'itcont.dta', None, 'fec_indiv_%s' % cycle),
        F('ftp://ftp.fec.gov/FEC/20%s/pas2%s.zip' % (cycle, cycle), 'itpas2.dta', None, 'fec_pac2cand_%s' % cycle),
        F('ftp://ftp.fec.gov/FEC/20%s/oth%s.zip' % (cycle, cycle), 'itoth.dta', None, 'fec_pac2pac_%s' % cycle),
        F('ftp://ftp.fec.gov/FEC/cm%s.zip' % cycle, 'foiacm.dta', 'fec_committee_master_schema.csv', 'fec_committees_%s' % cycle),
        F('ftp://ftp.fec.gov/FEC/cn%s.zip' % cycle, 'foiacn.dta', 'fec_candidate_master_schema.csv', 'fec_candidates_%s' % cycle),
        F('ftp://ftp.fec.gov/FEC/webl%s.zip' % cycle, 'FECWEB/webl%s.dat' % cycle, 'fec_candidate_summary.csv', 'fec_candidate_summaries_%s' % cycle),
        F('ftp://ftp.fec.gov/FEC/webk%s.zip' % cycle, 'FECWEB/webk%s.dat' % cycle, 'fec_pac_summary.csv', 'fec_committee_summaries_%s' % cycle)
    ]
