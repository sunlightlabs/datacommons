-- fix mistakenly overridden bios
update matchbox_sunlightinfo set bio = null where notes = '3/3/2011: Copying Bioguide photo_url here to override newly scraped politician photos from Wikipedia.';
-- there should never be a reason for wikipedia to override bioguide with empty entries
update matchbox_wikipediainfo set bio = null where bio = '';
