CYCLES = [str(year)[2:] for year in range(1990, 2012, 2)]

FILE_TYPES = {
    'cands': ['cycle','fec_cand_id','cid','first_last_p','party','dist_id_run_for','dist_id_curr','curr_cand','cycle_cand','crp_ico','recip_code','no_pacs'],
    'cmtes': ['cycle','cmte_id','pac_short','affiliate','ult_org','recip_id','recip_code','fec_cand_id','party','prim_code','source','sensitive','is_foreign','active'],
    'indivs': ['cycle','fec_trans_id','contrib_id','contrib','recip_id','org_name','ult_org','real_code','datestamp','amount','street','city','state','zipcode','recip_code','type','cmte_id','other_id','gender','fec_occ_emp','microfilm','occ_ef','emp_ef','source'],
    'pac_other': ['cycle','fec_rec_no','filer_id','donor_cmte','contrib_lend_trans','city','state','zipcode','fec_occ_emp','prim_code','datestamp','amount','recip_id','party','other_id','recip_code','recip_prim_code','amend','report','pg','microfilm','type','real_code','source'],
    'pacs': ['cycle','fec_rec_no','pac_id','cid','amount','datestamp','real_code','type','di','fec_cand_id'],
}

TABLE_NAMES = {
    'cands': 'candidate',
    'cmtes': 'committee',
    'indivs': 'individual_contribution',
    'pac_other': 'pac2pac_contribution',
    'pacs': 'pac_contribution',
}