from helpers import *

def correctionLateIndicator(value):
    
    if value == 'current entry':
        return ''
    elif value[0] == 'C':
        return 'C'
    elif value[0] == 'L':
        return 'L'

FAADS_FIELDS = [('unique_transaction_id', 'unique_transaction_id', None),
                ('transaction_status', 'transaction_status', None),
                ('fyq', 'fyq', None),
                ('cfda_program_num', 'cfda_program_num', None),
                ('sai_number', 'sai_number', None),
                ('recipient_name', 'recipient_name', None),
                ('recipient_city_code', 'recipient_city_code', None),
                ('recipient_city_name', 'recipient_city_name', None),
                ('recipient_county_code', 'recipient_county_code', None),
                ('recipient_zip', 'recipient_zip', None),
                ('recipient_type', 'recipient_type', splitCode),
                ('action_type', 'action_type', splitCode),
                ('agency_code', 'agency_code', splitCode),
                ('federal_award_id', 'federal_award_id', None),
                ('federal_award_mod', 'federal_award_mod', None),
                ('fed_funding_amount', 'fed_funding_amount', splitInt),
                ('non_fed_funding_amount', 'non_fed_funding_amount', splitInt),
                ('total_funding_amount', 'total_funding_amount', splitInt),
                ('obligation_action_date', 'obligation_action_date', None),
                ('starting_date', 'starting_date', None),
                ('ending_date', 'ending_date', None),
                ('assistance_type', 'assistance_type', splitCode),
                ('record_type', 'record_type', splitCode),
                ('correction_late_ind', 'correction_late_ind', correctionLateIndicator),
                ('fyq_correction', 'fyq_correction', None),
                ('principal_place_code', 'principal_place_code', None),
                ('principal_place_state', 'principal_place_state', None),
                ('principal_place_cc', 'principal_place_cc', None),
                ('principal_place_zip', 'principal_place_zip', None),
                ('principal_place_cd', 'principal_place_cd', None),
                ('cfda_program_title', 'cfda_program_title', None),
                ('agency_name', 'agency_name', None),
                ('project_description', 'project_description', None),
                ('duns_no', 'duns_no', None),
                ('duns_conf_code', 'duns_conf_code', None),
                ('progsrc_agen_code', 'progsrc_agen_code', None),
                ('progsrc_acnt_code', 'progsrc_acnt_code', None),
                ('progsrc_subacnt_code', 'progsrc_subacnt_code', None),
                ('receip_addr1', 'receip_addr1', None),
                ('receip_addr2', 'receip_addr2', None),
                ('receip_addr3', 'receip_addr3', None),
                ('face_loan_guran', 'face_loan_guran', splitInt),
                ('orig_sub_guran', 'orig_sub_guran', splitInt),
                ('fiscal_year', 'fiscal_year', splitInt),
                ('principal_place_state_code', 'principal_place_state_code', splitCode),
                ('recip_cat_type', 'recip_cat_type', splitCode),
                ('asst_cat_type', 'asst_cat_type', splitCode),
                ('recipient_cd', 'recipient_cd', splitCode),
                ('maj_agency_cat', 'maj_agency_cat', splitCode),
                ('rec_flag', 'rec_flag', splitCode),
                ('recipient_country_code', 'recipient_country_code', splitCode),
                ('uri', 'uri', None),
                ('recipient_state_code', 'recipient_state_code', splitCode)]

