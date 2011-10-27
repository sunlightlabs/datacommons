drop view if exists lobbyist_bundling_denormalized_view;
create view lobbyist_bundling_denormalized_view as
    select
        file_num,
        cb.committee_name,
        committee_fec_id,
        re.name as recipient_name,
        le.name as lobbyist_name,
        fe.name as firm_name,
        contributor_fec_id,
        lb.street_addr1,
        lb.street_addr2,
        lb.city,
        lb.state,
        lb.zip_code,
        lb.occupation,
        cb.start_date,
        cb.end_date,
        report_year,
        report_type,
        amount,
        lb.semi_annual_amount,
        pdf_url
    from contribution_bundle cb
        inner join contribution_lobbyistbundle lb on file_num = file_num_id
        left join assoc_bundle_recipients abr using (file_num)
        left join matchbox_entity re on abr.entity_id = re.id
        left join assoc_bundler_lobbyists abl on abl.bundle_id = lb.id
        left join matchbox_entity le on abl.entity_id = le.id
        left join assoc_bundler_firms abf on abf.bundle_id = lb.id
        left join matchbox_entity fe on abf.entity_id = fe.id
    where not should_ignore
;
