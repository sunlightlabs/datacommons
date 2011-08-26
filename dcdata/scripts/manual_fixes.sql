-- Manual fix for 16 transactions where Disney is listed as parent of P&G
delete from
    parent_organization_associations p
using 
    organization_associations o
where 
    o.transaction_id = p.transaction_id
    and o.entity_id = '9070ecd132f44963a369479e91950283'
    and p.entity_id = '204b089d9d614fa6b77db666d76d9f3c'
;
