
create_tops_stmt = """
    create table tmp_tops as
        select case when contributor_entity = '' then contributor_name
                    else contributor_entity
               end as contributor,
               case when recipient_entity = '' then recipient_name
                    else recipient_entity
               end as recipient,
               cycle,
               count(*) as count,
               sum(amount) as amount
        from contribution_contribution
        where 
            cycle = '2006'
            and contributor_state = 'WA'
        group by case when contributor_entity = '' then contributor_name
                        else contributor_entity end,
                 case when recipient_entity = '' then recipient_name
                         else recipient_entity end,
                 cycle;
"""
             
top_contributors_stmt = """             
    select coalesce(e.name, t.contributor), e.id, count, amount
    from tmp_tops t
    left outer join matchbox_entity e on e.id = t.contributor
    where
        recipient = 'GREGOIRE, CHRISTINE O'
    order by amount desc
    limit 20;
"""








