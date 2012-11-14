-- need to drop and recreate lobbying_report to make changes to lobbying_lobbying
drop view sponlob_lobbying_reports_quarterly;
drop view lobbying_report;

alter table lobbying_lobbying drop column client_ext_id;

create view lobbying_report as
    select *, case when year % 2 = 0 then year else year + 1 end as cycle
    from lobbying_lobbying l
    where
        use = 't';

create view sponlob_lobbying_reports_quarterly as
 SELECT lobbying_report.transaction_id, lobbying_report.transaction_type, lobbying_report.transaction_type_desc, lobbying_report.year, lobbying_report.filing_type, lobbying_report.filing_included_nsfs, lobbying_report.amount, lobbying_report.registrant_name, lobbying_report.registrant_is_firm, lobbying_report.client_name, lobbying_report.client_category, lobbying_report.client_parent_name, lobbying_report.include_in_industry_totals, lobbying_report.use, lobbying_report.affiliate, lobbying_report.cycle, (lobbying_report.year - 2008) * 4 + 
        CASE
            WHEN "substring"(lobbying_report.transaction_type::text, 1, 2) = 'q1'::text THEN 1
            WHEN "substring"(lobbying_report.transaction_type::text, 1, 2) = 'q2'::text THEN 2
            WHEN "substring"(lobbying_report.transaction_type::text, 1, 2) = 'q3'::text THEN 3
            WHEN "substring"(lobbying_report.transaction_type::text, 1, 2) = 'q4'::text THEN 4
            ELSE NULL::integer
        END AS quarters_from_2008
   FROM lobbying_report
  WHERE lobbying_report.year >= 2008;

