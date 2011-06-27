insert into matchbox_sunlightinfo (entity_id, photo_url, notes)
    select entity_id, photo_url, '6/27/2011: Copying Bioguide photo_url here for freshman senators who didn''t have them before, and to override scraped politician photos from Wikipedia.'
from matchbox_bioguideinfo bioguide
where bioguide.photo_url is not null
and not exists(select 1 from matchbox_sunlightinfo s where s.entity_id = bioguide.entity_id);
