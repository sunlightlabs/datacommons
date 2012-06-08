-- This is just for the new entities that were created.

insert into faca_matches (membersid, entity_id)
    select membersid, '1bf229f8-a764-44ac-9d1a-0f8dac493a8c'::uuid from faca_members where membersid not in (select membersid from faca_matches) and occupationoraffiliation ilike '%Colorado School of Mines%'
    union all
    select membersid, '5c67f458-31cc-453d-8c52-4936f774cd94'::uuid from faca_members where membersid not in (select membersid from faca_matches) and occupationoraffiliation ilike '%Texas Christian University%'
    union all
    select membersid, '0de2591e-116b-4b67-aa92-153c07a1954b'::uuid from faca_members where membersid not in (select membersid from faca_matches) and occupationoraffiliation ilike '%St. John Fisher College%'
    union all
    select membersid, 'c55617a0-296a-43b8-9f32-72287b211eba'::uuid from faca_members where membersid not in (select membersid from faca_matches) and occupationoraffiliation ilike '%South Carolina State University%'
    union all
    select membersid, '6a2e45d8-276e-4778-8f33-ee0b5649b1fb'::uuid from faca_members where membersid not in (select membersid from faca_matches) and occupationoraffiliation ilike '%University of La Verne%'
    union all
    select membersid, 'ef5f17a4-3662-40fc-b751-22f98f2d66d6'::uuid from faca_members where membersid not in (select membersid from faca_matches) and occupationoraffiliation ilike '%Biola University%'
    union all
    select membersid, '77f61790-d919-40d6-ab85-f13bce01a496'::uuid from faca_members where membersid not in (select membersid from faca_matches) and occupationoraffiliation ilike '%Edgewood College%'
    union all
    select membersid, '6f0624a4-181a-4fb6-9b03-80140900b60a'::uuid from faca_members where membersid not in (select membersid from faca_matches) and occupationoraffiliation ilike '%Louisiana Tech University%'
    union all
    select membersid, '2ec96e71-52ee-4305-a1b4-e84e44d7eb1e'::uuid from faca_members where membersid not in (select membersid from faca_matches) and occupationoraffiliation ilike '%Ashland University%'
;

