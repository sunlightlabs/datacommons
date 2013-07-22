
-- manual fixes...not sure how to best package these if there are more in the future
update fec_indexp_import
set candidate_id = 'P60003654'
where
    candidate_id = 'P80003353'
    and spender_id = 'C00507525'
    and support_oppose = 'Support';


update fec_indexp_import
set candidate_id = manual_fixes.id
from (values
    ('barack obama, ', 'P80003338'),
    ('barak obama, ', 'P80003338'), 
    ('bonamici, suzanne', 'H2OR01133'),
    ('boucher, rick', 'H2VA09010'),
    ('buerkle, ann marie', 'H0NY25078'),
    ('canseco, francisco raul quico', 'H4TX28046'),
    ('cornilles, robert', 'H0OR01095'),
    ('corwin, jane', 'H2NY00044'),
    ('davis, jack', 'H4NY26045'),
    ('gingrich, newt', 'P60003654'),
    ('hahn, janice', 'H8CA36097'),
    ('hatch, orrin', 'S6UT00063'),
    ('hochul, kathleen', 'H2NY00036'),
    ('hochul, kathy', 'H2NY00036'),
    ('huntsman, jon', 'P20003067'),
    ('marshall, kate', 'H2NV02247'),
    ('newt, gingrich', 'P60003654'),
    ('obama, barack', 'P80003338'),
    ('paul, ron', 'P80000748'),
    ('perry, rick', 'P20003281'),
    ('rahall, nick', 'H6WV04057'),
    ('romne, mitt', 'P80003353'),
    ('romney, mitt', 'P80003353'),
    ('ron, p', 'P80000748'),
    ('ron, paul', 'P80000748'),
    ('santorum, richard', 'P20002721'),
    ('santorum, rick', 'P20002721'),
    ('thompson, tommy', 'S2WI00235'),
    ('turner, bob', 'H0NY09072'),
    ('kaine, timothy', 'S2VA00142'),
    ('krishnamoorthi, raja', 'H2IL08096'),
    ('tester, jon', 'S6MT00162'),
    ('allen, george', 'S8VA00214'),
    ('bachus, spencer', 'H2AL06035'),
    ('Aguilar, Pete', 'H2CA31125'),
    ('Aubuchon, Gary', 'H2FL14145'),
    ('Berman, Howard', 'H2CA26026'),
    ('Bilbray, Brian', 'H4CA49032'),
    ('Bono Mack, Mary', 'H8CA44034'),
    ('Brownley, Julia', 'H2CA00120'),
    ('Cartwright, Matt', 'H2PA17079'),
    ('Cook, Paul', 'H2CA08164'),
    ('CRIMMINS, MICHAEL', 'H8CA53019'),
    ('Critz, Mark', 'H0PA12132'),
    ('Denham, Jeff', 'H0CA19173'),
    ('Griffin, John', 'H0AR02107'),
    ('Hoogendyk, Jack', 'H0MI06103'),
    ('Kang, Sukhee', 'H2CA48087'),
    ('Keadle, Scott', 'H0NC10151'),
    ('kelly, jesse', 'H0AZ08015'),
    ('Liljenquist, Dan', 'S2UT00195'),
    ('Lugar, Richard', 'S4IN00014'),
    ('Lungren, Dan', 'H6CA34112'),
    ('Miller, Gary', 'H8CA41063'),
    ('Mourdock, Richard', 'S2IN00083'),
    ('Mourdock, Richard E.', 'S2IN00083'),
    ('Rangel, Charles', 'H6NY19029'),
    ('VANN, KIM', 'H2CA03090'),
    ('Warren, Elizabeth', 'S2MA00170'),
    ('Wilson, Heather', 'S8NM00168'),
    ('CRAMER, KEVIN J', 'H0ND01026'),
    ('D''Amboise, Scott', 'S2ME00042'),
    ('Dutton, Bob', 'H2CA31133'),
    ('Obama, Barak', 'P80003338'),
    ('Simpson, Mike', 'H8ID02064'),
    ('Taj, Clayton', 'H2TX30087')
) manual_fixes (name, id)
where
    lower(candidate_name) = lower(manual_fixes.name);


-- some names are shared by multiple people. For these we need to restrict by state as well.
update fec_indexp_import
set candidate_id = manual_fixes.id
from (values
    ('John, Sullivan', 'OK', 'H2OK01093')
) manual_fixes (name, state, id)
where
    lower(candidate_name) = lower(manual_fixes.name)
    and candidate_state = state;

-- some candidates aren't running for federal office and shouldn't be reported here to begin with
-- removing here just so I don't see them when I run the test for unidentified politicians
delete from fec_indexp_import
where 
    candidate_name in (
        'Ballasteros, Adan',
        'Cargill, Mike',
        'WALKER, SCOTT'
    );


drop view if exists agg_fec_indexp_candidates;
drop view if exists agg_fec_indexp_committees;

delete from fec_indexp where cycle in (select cycle from fec_indexp_out_of_date_cycles);
insert into fec_indexp 
    (cycle, candidate_id, candidate_name, spender_id, spender_name, election_type, candidate_state,
    candidate_district, candidate_office, candidate_party, amount, aggregate_amount,
    support_oppose, date, purpose, payee, filing_number, amendment, transaction_id, image_number, received_date)
select 
    cycle,
    candidate_id, 
    candidate_name, 
    spender_id, 
    spender_name, 
    election_type, 
    candidate_state,
    case when candidate_office = 'House' then candidate_district else '' end as candidate_district,
    candidate_office,
    candidate_party, 
    regexp_replace(amount, ',|\$', '', 'g')::numeric as amount,
    regexp_replace(aggregate_amount, ',|\$', '', 'g')::numeric as aggregate_amount,
    support_oppose, 
    date, 
    purpose, 
    payee, 
    filing_number, 
    amendment, 
    transaction_id, 
    image_number, 
    received_date
from fec_indexp_import i
where
    not exists (select * from fec_indexp_import a where i.spender_id = a.spender_id and i.filing_number = a.prev_file_num);


create or replace view agg_fec_indexp_candidates as
select distinct entity_id, cycle, spender_id, filing_number, transaction_id
from fec_indexp
inner join matchbox_entityattribute on candidate_id = value and namespace = 'urn:fec:candidate';

create or replace view agg_fec_indexp_committees as
select distinct entity_id, cycle, spender_id
from fec_indexp
inner join matchbox_entityattribute on spender_id = value and namespace = 'urn:fec:committee';


delete from agg_fec_indexp where cycle in (select cycle from fec_indexp_out_of_date_cycles);
insert into agg_fec_indexp (cycle, candidate_entity, candidate_name, committee_entity, committee_name, support_oppose, amount)
select i.cycle, cand.id as candidate_entity, coalesce(cand.name, candidate_name) as candidate_name,
    committee.id as committee_entity, coalesce(committee.name, spender_name) as committee_name,
    support_oppose, sum(amount) as amount
from fec_indexp i
inner join fec_indexp_out_of_date_cycles using (cycle)
left join agg_fec_indexp_candidates cand_assoc using (spender_id, filing_number, transaction_id)
left join matchbox_entity cand on cand_assoc.entity_id = cand.id
left join agg_fec_indexp_committees committee_assoc on committee_assoc.spender_id = i.spender_id and committee_assoc.cycle = i.cycle
left join matchbox_entity committee on committee_assoc.entity_id = committee.id
group by i.cycle, candidate_entity, coalesce(cand.name, candidate_name), committee_entity, coalesce(committee.name, spender_name), support_oppose
;


delete from agg_fec_indexp_totals where cycle in (select cycle from fec_indexp_out_of_date_cycles);
insert into agg_fec_indexp_totals (cycle, entity_id, spending_amount)
select cycle, committee_entity as entity_id, sum(amount) as spending_amount
from agg_fec_indexp
inner join fec_indexp_out_of_date_cycles using (cycle)
where committee_entity is not null
group by entity_id, cycle
;



