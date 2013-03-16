
"""
The following is a list of the FEC tables and their columns to be indexed (beyond cycle,
which is taken care of by the partitioning.
"""
INDEX_COLS_BY_TABLE_FEC = {
    'fec_indiv':      ['filer_id'],
    'fec_candidates': [],
    'fec_pac2cand':   ['candidate_id', 'other_id'],
    'fec_pac2pac':    ['filer_id', 'other_id'],
    'fec_committees': [],
    'fec_candidates': [],
    'fec_candidate_summaries': [],
    'fec_committee_summaries': [],
}


