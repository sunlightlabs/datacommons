from dcdata.fec.importer import *

cycles = '96 98 00 02 04 06 08 10 12'.split()

def cycle_configs(cycles):
	return reduce(lambda x, y: x + y, [cycle_config(c) for c in cycles])

def cycle_config(cycle):
	if len(cycle) == 4:
		cycle4 = cycle
		cycle2 = cycle[2:]
	elif len(cycle) == 2:
		cycle2 = cycle
		cycle4 = '20%s' % cycle if int(cycle) < 50 else '19%s' % cycle
	else:
		raise Exception("Unknown cycle %s" % cycle)

	return [
	    F('ftp://ftp.fec.gov/FEC/%s/indiv%s.zip' % (cycle4, cycle2), 'itcont.txt', 'fec_indiv_%s' % cycle2),
	    F('ftp://ftp.fec.gov/FEC/%s/pas2%s.zip' % (cycle4, cycle2), 'itpas2.txt', 'fec_pac2cand_%s' % cycle2),
	    F('ftp://ftp.fec.gov/FEC/%s/oth%s.zip' % (cycle4, cycle2), 'itoth.txt', 'fec_pac2pac_%s' % cycle2),
	    F('ftp://ftp.fec.gov/FEC/%s/cm%s.zip' % (cycle4, cycle2), 'cm.txt', 'fec_committees_%s' % cycle2),
	    F('ftp://ftp.fec.gov/FEC/%s/cn%s.zip' % (cycle4, cycle2), 'cn.txt', 'fec_candidates_%s' % cycle2),
	    F('ftp://ftp.fec.gov/FEC/%s/weball%s.zip' % (cycle4, cycle2), 'weball%s.txt' % cycle2, 'fec_candidate_summaries_%s' % cycle2),
	    F('ftp://ftp.fec.gov/FEC/%s/webk%s.zip' % (cycle4, cycle2), 'webk%s.txt' % cycle2, 'fec_committee_summaries_%s' % cycle2)
    ]
