from dcdata.fec.importer import *

cycles = '00 02 04 06 08 10 12'.split()

ALL_CYCLE_CONFIG = reduce(lambda x, y: x+y,
        [(
            F('ftp://ftp.fec.gov/FEC/indiv%s.zip' % cycle, 'itcont.dta', 'fec_individual_contributions.csv', 'fec_indiv_%s' % cycle),
            F('ftp://ftp.fec.gov/FEC/pas2%s.zip' % cycle, 'itpas2.dta', 'fec_contributions_to_candidates.csv', 'fec_pac2cand_%s' % cycle),
            F('ftp://ftp.fec.gov/FEC/oth%s.zip' % cycle, 'itoth.dta', 'fec_committee_transactions.csv', 'fec_pac2pac_%s' % cycle),
            F('ftp://ftp.fec.gov/FEC/cm%s.zip' % cycle, 'foiacm.dta', 'fec_committee_master_schema.csv', 'fec_committees_%s' % cycle),
            F('ftp://ftp.fec.gov/FEC/cn%s.zip' % cycle, 'foiacn.dta', 'fec_candidate_master_schema.csv', 'fec_candidates_%s' % cycle),
            F('ftp://ftp.fec.gov/FEC/webk%s.zip' % cycle, 'FECWEB/webk%s.dat' % cycle, 'fec_pac_summary.csv', 'fec_pac_summaries_%s' % cycle),    
        ) for cycle in cycles], ())



# + [
#     F('ftp://ftp.fec.gov/FEC/1992/pacsum92.zip', 'NP921.TAP', 'pacsum.csv', 'fec_early_pac_summaries_%s' % year[2:4]),
#     F('ftp://ftp.fec.gov/FEC/1994/pacsum94.zip', 'PACSUM94.DAT', 'pacsum.csv', 'fec_early_pac_summaries_%s' % year[2:4]),
#     F('ftp://ftp.fec.gov/FEC/1996/pacsum96.zip', 'PACSUM96.DAT', 'pacsum.csv', 'fec_early_pac_summaries_%s' % year[2:4]),
#     F('ftp://ftp.fec.gov/FEC/1998/pacsum98.zip', 'R98/RDATA/NPTAP1.TAP', 'pacsum.csv', 'fec_early_pac_summaries_%s' % year[2:4]),
#     F('ftp://ftp.fec.gov/FEC/2000/pacsum00.zip', 'pacsum%s.txt', 'pacsum.csv', 'fec_early_pac_summaries_%s' % year[2:4]),
#     F('ftp://ftp.fec.gov/FEC/2002/pacsum02.zip', 'pacsum%s.txt', 'pacsum.csv', 'fec_early_pac_summaries_%s' % year[2:4]),
#     F('ftp://ftp.fec.gov/FEC/2004/pacsum04.zip', 'pacsum%s.txt', 'pacsum.csv', 'fec_early_pac_summaries_%s' % year[2:4]),
# ]