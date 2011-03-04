insert into matchbox_sunlightinfo (entity_id, photo_url, notes)
    select entity_id, photo_url, '3/3/2011: Copying Bioguide photo_url here to override newly scraped politician photos from Wikipedia.'
from matchbox_bioguideinfo bioguide
where bioguide.photo_url is not null;
