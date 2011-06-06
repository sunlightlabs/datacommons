update pogo_contractor set contractor_ext_id = substring(url from 'ContractorID=([0-9]*)$')::smallint;
