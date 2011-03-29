alter table lobbying_bill add column bill_type_raw varchar(12);
alter table lobbying_bill add column bill_type varchar(2);

update lobbying_bill set bill_type_raw = regexp_replace(bill_name, E'[0-9. ]*', '', 'g');
update
    lobbying_bill 
set
    bill_type = case
        when bill_type_raw in ('H', 'HR') then 'h'
        when bill_type_raw in ('HCON', 'HCONRES') then 'hc'
        when bill_type_raw in ('HJ', 'HJRES') then 'hj'
        when bill_type_raw in ('HRES', 'HRRES') then 'hr'
        when bill_type_raw in ('S', 'SR') then 's'
        when bill_type_raw in ('SCON', 'SCONRES') then 'sc'
        when bill_type_raw in ('SJ', 'SJES', 'SJRES') then 'sj'
        when bill_type_raw in ('SRES') then 'sr'
        else null end
;

alter table lobbying_bill drop column chamber;
