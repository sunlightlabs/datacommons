--datacommons=> select * from matchbox_wikipediainfo where entity_id = '494bba3863c84741bdd7eb3e97a296e8';
--   id   |              entity_id               |                                                                                  bio                                                                                   |             bio_url              |         scraped_on         | created_on | updated_on | photo_url 
----------+--------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------------------------------+----------------------------+------------+------------+-----------
-- 399077 | 494bba38-63c8-4741-bdd7-eb3e97a296e8 | <p>.ke is the Internet country code top-level domain (ccTLD) for Kenya.</p><p>Second-level domains, under which domains are registered at the third level, are:</p><p>+| http://en.wikipedia.org/wiki/.ke | 2011-03-01 00:06:28.483597 | 2011-03-01 |            | 
--        |                                      | Details of these, and of the unusual delegation mechanism used by the .ke zone, can be found in some ccTLD analysis </p>                                               |                                  |                            |            |            | 
--(1 row)
--
--Time: 19.058 ms
--datacommons=> select * from matchbox_sunlightinfo where entity_id = '494bba3863c84741bdd7eb3e97a296e8';
-- id | entity_id | bio | bio_url | photo_url | notes | created_on | updated_on 
------+-----------+-----+---------+-----------+-------+------------+------------
--(0 rows)

insert into matchbox_sunlightinfo (entity_id, bio, bio_url, notes) values ('494bba38-63c8-4741-bdd7-eb3e97a296e8', '', '', '');
