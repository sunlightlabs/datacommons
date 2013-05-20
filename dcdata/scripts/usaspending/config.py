INDEX_COLS_BY_TABLE = {
    'contracts_contract': [
        'using gin (to_tsvector(\'datacommons\'::regconfig, agency_name::text))',
        'statecode, congressionaldistrict',
        'using gin (to_tsvector(\'datacommons\'::regconfig, contracting_agency_name::text))',
        '(fiscal_year DESC, obligatedamount DESC)',
        'dunsnumber',
        'fiscal_year',
        'obligatedamount',
        'piid',
        'using gin (to_tsvector(\'datacommons\'::regconfig, requesting_agency_name::text))',
        'signeddate',
        'unique_transaction_id',
        'using gin (to_tsvector(\'datacommons\'::regconfig, city::text))',
        'using gin (to_tsvector(\'datacommons\'::regconfig, vendorname::text))',
    ],
    'grants_grant': [
        'using gin (to_tsvector(\'datacommons\'::regconfig, agency_name::text)) ',
        'using gin (to_tsvector(\'datacommons\'::regconfig, recipient_name::text))',
        'total_funding_amount',
    ],
}
