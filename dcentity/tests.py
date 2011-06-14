from django.test import TestCase

from django.db import connection, transaction

from dcentity.entity import merge_entities
from dcentity.models import *
from dcentity.tools.management.commands.entity_wikipedia_scrape import find_wikipedia_url
from dcentity.tools.models import *
from dcentity.tools.names import *
from dcentity.tools.wpapi import *

class TestQueries(TestCase):
    
    def setUp(self):
        #set up latest cycle view for merge testing
        cursor = connection.cursor()
        cursor.execute(
            """create view politician_metadata_latest_cycle_view as 
            select distinct on (entity_id)
                    entity_id,
                    cycle,
                    state,
                    state_held,
                    district,
                    district_held,
                    party,
                    seat,
                    seat_held,
                    seat_status,
                    seat_result
                from matchbox_politicianmetadata
                order by entity_id, cycle desc"""
        )
        transaction.commit_unless_managed()
        
        apple = Entity.objects.create(name="Apple")
        #apple.aliases.create(alias="Apple")
        apple.aliases.create(alias="Apple Juice")
        apple.attributes.create(namespace='color', value='red')
        apple.attributes.create(namespace='color', value='yellow')
        apple.attributes.create(namespace='texture', value='crisp')
        apple.politician_metadata_by_cycle.create(party='Fruit', cycle=2010)
        self.apple_id = apple.id

        apricot = Entity.objects.create(name="Apricot")
        apricot.aliases.create(alias='Apricot')
        apricot.attributes.create(namespace='color', value='yellow')
        apricot.attributes.create(namespace='texture', value='soft')
        self.apricot_id = apricot.id

        applicot = Entity.objects.create(name=u"Applicot")
        applicot.aliases.create(alias='Applicot')
        self.applicot_id = applicot.id

        self.assertEqual(1, apple.aliases.filter(alias="Apple").count())
        self.assertEqual(3, Entity.objects.count())
        self.assertEqual(4, EntityAlias.objects.count())
        self.assertEqual(5, EntityAttribute.objects.count())

    def test_merge_entities(self):
        merge_entities([self.apple_id, self.apricot_id], self.applicot_id)

        self.assertEqual(1, Entity.objects.count())
        applicot = Entity.objects.get(name="Applicot")
        self.assertEqual(self.applicot_id, applicot.id.hex)

        self.assertEqual(4, EntityAlias.objects.count())
        self.assertEqual(4, applicot.aliases.count())
        self.assertEqual(1, applicot.aliases.filter(alias='Apple').count())
        self.assertEqual(1, applicot.aliases.filter(alias='Apple Juice').count())
        self.assertEqual(1, applicot.aliases.filter(alias='Apricot').count())
        self.assertEqual(1, applicot.aliases.filter(alias='Applicot').count())
    
    def test_delete_metadata(self):
        merge_entities([self.apple_id, self.apricot_id], self.applicot_id)    
        self.assertEqual(0, PoliticianMetadata.objects.filter(entity=self.apple_id).count())
        #self.assertEqual(0, SunlightInfo.objects.filter(entity=self.apple_id).count())

    def test_merge_entities_alias_duplication(self):
        apple = Entity.objects.get(id=self.apple_id)
        apple.aliases.create(alias="Delicious")

        apricot = Entity.objects.get(id=self.apricot_id)
        apricot.aliases.create(alias="Delicious")

        merge_entities([self.apple_id, self.apricot_id], self.applicot_id)

        applicot = Entity.objects.get(name="Applicot")

        self.assertEqual(5, EntityAlias.objects.count())
        self.assertEqual(5, applicot.aliases.count())
        self.assertEqual(1, applicot.aliases.filter(alias='Apple').count())
        self.assertEqual(1, applicot.aliases.filter(alias='Apple Juice').count())
        self.assertEqual(1, applicot.aliases.filter(alias='Apricot').count())
        self.assertEqual(1, applicot.aliases.filter(alias='Applicot').count())
        self.assertEqual(1, applicot.aliases.filter(alias='Delicious').count())

    def test_merge_entities_attribute_duplication(self):
        merge_entities([self.apple_id, self.apricot_id], self.applicot_id)

        applicot = Entity.objects.get(name="Applicot")

        self.assertEqual(6, EntityAttribute.objects.count())
        self.assertEqual(6, applicot.attributes.count())
        self.assertEqual(1, applicot.attributes.filter(namespace='color', value='red').count())
        self.assertEqual(1, applicot.attributes.filter(namespace='color', value='yellow').count())
        self.assertEqual(1, applicot.attributes.filter(namespace='texture', value='crisp').count())
        self.assertEqual(1, applicot.attributes.filter(namespace='texture', value='soft').count())
        self.assertEqual(1, applicot.attributes.filter(namespace=EntityAttribute.ENTITY_ID_NAMESPACE, value=self.apple_id).count())
        self.assertEqual(1, applicot.attributes.filter(namespace=EntityAttribute.ENTITY_ID_NAMESPACE, value=self.apricot_id).count())


class TestPoliticianManager(TestCase):
    def test_get_unique_politician(self):
        #Create some noise.
        e = EntityPlus.objects.create(type='politician', name='foo1')
        e.aliases.create(alias="Wayne P Deangelo")
        e = EntityPlus.objects.create(type='politician', name='foo2')
        e.aliases.create(alias="Robert Bennet")
        e = EntityPlus.objects.create(type='politician', name='foo3')
        e.aliases.create(alias='Caroline Bennet')

        #Create an leadership pac entity with an incomplete politician name.
        e = EntityPlus.objects.create(type='organization', name="foo4")
        e.aliases.create(alias="WAYNE DEANGELO FOR ASSEMBLY")
        self.assertEqual(e.names[0].pname.name, u'WAYNE DEANGELO')

        #Find the unique politician with full name.
        ename, entity = EntityPlus.politicians.get_unique_politician(e.names[0])
        self.assertEqual(ename.name, u'Wayne P Deangelo')

        #Non-unique non-match
        e = EntityPlus.objects.create(type='organization', name='foo5')
        e.aliases.create(alias="BENNET FOR ASSEMBLY")
        self.assertFalse(EntityPlus.politicians.get_unique_politician(e.names[0]))

class TestEntityPlus(TestCase):

    def test_first_matching_name(self):
        e1 = EntityPlus.objects.create(type="politician", name="name")
        a = e1.aliases.create(alias="WAYNE P GRETSKY")
        a = e1.aliases.create(alias="Mr D")
        e2 = EntityPlus.objects.create(type="politician", name="Fantastick")
        a = e2.aliases.create(alias="Yer Mom")
        a = e2.aliases.create(alias="W Gretsky")
        self.assertEqual(e1.first_matching_name(e2), PersonName("W Gretsky"))

        e3 = EntityPlus.objects.create(type="politician", name="yah")
        a = e3.aliases.create(alias="W P Fargo")
        self.assertFalse(e1.first_matching_name(e3))

class TestWikipediaScrape(TestCase):

    def test_find_wikipedia_url(self):
        e = EntityPlus.objects.create(type='politician', name="foo")
        a = e.aliases.create(alias='Barack Obama')

        e.politician_metadata_for_latest_cycle = PoliticianMetadataLatest(state='', party='D', seat='federal:president', cycle=2010, seat_status='open', seat_result='win')
        self.assertEqual(find_wikipedia_url(e)[0], 'http://en.wikipedia.org/wiki/Barack_Obama')

        e = EntityPlus.objects.create(type='organization', name="foo1")
        a = e.aliases.create(alias='Atlantic Richfield')
        self.assertEqual(find_wikipedia_url(e)[0], 'http://en.wikipedia.org/wiki/ARCO')

        e = EntityPlus.objects.create(type='organization', name="foo2")
        a = e.aliases.create(alias='No WP entry for this')
        self.assertEqual(find_wikipedia_url(e), ['', ''])

        e = EntityPlus.objects.create(type='organization', name="foo4")
        a = e.aliases.create(alias='159 Group')
        self.assertEqual(find_wikipedia_url(e), ['', ''])

        e = EntityPlus.objects.create(type='organization', name="foo5")
        a = e.aliases.create(alias='188 Claremont')
        self.assertEqual(find_wikipedia_url(e), ['', ''])


class TestWikipediaArticle(TestCase):

    def test_all(self):
        a = WikipediaArticle("Barack Obama")
        self.assertTrue(a.is_person())
        self.assertTrue(a.is_politician())
        self.assertTrue(a.name_matches("Barack Hussein Obama III"))
        self.assertTrue(a.is_american())

        a = WikipediaArticle("BP")
        self.assertFalse(a.is_person())
        self.assertFalse(a.is_politician())
        self.assertTrue(a.is_company())

        a = WikipediaArticle("User:SomeUser (disambiguation)")
        self.assertEqual(a.namespace, 'User')
        self.assertEqual(a.name, 'SomeUser')
        self.assertEqual(a.disambiguator, 'disambiguation')

        a = WikipediaArticle("Ralph E. Reed, Jr.")
        self.assertTrue(a.is_person())
        self.assertTrue(a.is_politician())
        self.assertTrue(a.is_american())

        a = WikipediaArticle("Brian Clay")
        self.assertFalse(a.is_politician())

        a = WikipediaArticle("Kevin Kolb")
        self.assertTrue(a.is_person())
        self.assertFalse(a.is_politician())

        a = WikipediaArticle("Linda Upmeyer")
        self.assertTrue(a.is_politician())
        self.assertTrue(a.is_american())

        a = WikipediaArticle("Donald Morrison (politician)")
        self.assertTrue(a.is_person())
        self.assertTrue(a.is_politician())
        self.assertFalse(a.is_american())

        self.assertTrue(WikipediaArticle("Robert Mendelsohn").is_disambiguation_page())

    def test_get_article_subject(self):
        self.assertEqual(get_article_subject("Barack Obama"), u'Barack Hussein Obama II')


class TestNames(TestCase):
    
    def test_fix_name(self):
        self.assertEqual(fix_name('Joe Blow (D)'), 'Joe Blow')
        self.assertEqual(fix_name('Blow, Joe (R)'), 'Joe Blow')
        self.assertEqual(fix_name('Schumer, Ted & George, Boy'), 'Ted Schumer & Boy George')
        self.assertEqual(fix_name('54th Natl Assn of US Cmte Dept Assoc Inc.'), '54th national association of united states committee department associates Inc.')
        self.assertEqual(fix_name('Johnson, Smith et al'), 'Johnson, Smith et al')
        self.assertEqual(fix_name('GORDNER, FRIENDS OF JOHN'), 'FRIENDS OF JOHN GORDNER')
        self.assertEqual(fix_name('HUFFMAN FOR ASSEMBLY 2008, JARED'), 'JARED HUFFMAN FOR ASSEMBLY 2008')
        self.assertEqual(fix_name('BEHNING, CMTE TO ELECT ROBERT W'), 'committee TO ELECT ROBERT W BEHNING')
        self.assertEqual(fix_name('HALL, DUANE R II'), 'DUANE R HALL II')
        self.assertEqual(fix_name('WALL, TROSSIE W JR'), 'TROSSIE W WALL JR')
        self.assertEqual(fix_name('CROOK, MRS JERRY W'), 'JERRY W CROOK')
        self.assertEqual(fix_name('HAMRIC, PEGGY (COMMITTEE 1)'), 'PEGGY HAMRIC')


class TestPersonName(TestCase):

    def test_middle_names_can_be_initialed(self):
        self.assertTrue(PersonName("Barack H Obama") == PersonName("Barack Hussein Obama"))

    def test_middle_names_if_present_must_match(self):
        self.assertFalse(PersonName("Barack B Obama") == PersonName("Barack H Obama"))

    def test_make_sure_not_equals_also_works(self):
        assert PersonName("Barack H Obama") != PersonName("Barack George Obama")

    def test_middle_names_and_suffixes_can_be_eliminated(self):
        self.assertTrue(PersonName("Barack H Obama, III") == PersonName("Barack Obama"))
        self.assertTrue(PersonName("Roger McAuliffe") == PersonName("ROGER P MCAULIFFE"))

    def test_first_names_can_be_initialed(self):
        self.assertTrue(PersonName("B H Obama") == PersonName("Barack Obama"))

    def test_but_they_must_match_if_they_arent_initials(self):
        self.assertFalse(PersonName("Beverly H Obama") == PersonName("Barack H Obama"))

    def test_last_names_must_always_match(self):
        self.assertFalse(PersonName("Barack H Hosana") == PersonName("Barack H Obama"))

    def test_nicknames_might_work(self):
        self.assertTrue(PersonName("Ted Haggart") == PersonName("Theodore Haggart"))
        self.assertTrue(PersonName("Mike Easley") == PersonName("Michael Easley"))

    def test_first_and_middle_names_can_be_ommitted(self):
        self.assertTrue(PersonName("George Washington") == PersonName("Washington"))

    def test_allow_middle_name_as_first_name_in_some_cases(self):
        self.assertTrue(PersonName("Ed McMahan") == PersonName("W. Edwin McMahan"))
        self.assertTrue(PersonName("J Edgar Hoover") == PersonName("Edgar Hoover"))
        self.assertTrue(PersonName("John Edgar Hoover") == PersonName("Edgar Hoover"))
        self.assertTrue(PersonName("J E Hoover") == PersonName("Edgar Hoover"))
        self.assertFalse(PersonName("J Edwin Hoover") == PersonName("J Edgar Hoover"))

    def test_ignore_anything_including_and_after_an_ampersand(self):
        p = PersonName("TED STRICKLAND & LEE FISCHER")
        self.assertEqual((p.first, p.middle, p.last, p.suffix), ('TED', None, 'STRICKLAND', None))
        self.assertTrue(p == PersonName("Ted Strickland"))

    def test_single_name_or_last_name_only_people(self):
        p = PersonName("Bono")
        self.assertEqual((p.first, p.middle, p.last, p.suffix), (None, None, 'BONO', None))

    def test_handle_inline_nicknames(self):
        p = PersonName('Robert Foster "Bob" Bennett')
        self.assertEqual((p.first, p.middle, p.last, p.suffix), ('ROBERT', 'FOSTER', 'BENNETT', None))
        self.assertTrue(p == PersonName('Bob Bennett'))

        p1 = PersonName('Joseph E. "Jeb" Bradley')
        self.assertEqual((p1.first, p1.middle, p1.last, p1.suffix), ('JOSEPH', 'E', 'BRADLEY', None))
        p2 = PersonName("JEB E BRADLEY")
        self.assertEqual((p2.first, p2.middle, p2.last, p2.suffix), ('JEB', 'E', 'BRADLEY', None))
        self.assertTrue(p1 == p2)
        self.assertTrue(p2 == p1)

    def test_match_middle_as_first(self):
        self.assertTrue(PersonName.match_middle_as_first(PersonName("J. Edgar Hoover"), PersonName("Edgar Hoover"), True))

    def test_check_reflexive(self):
        self.assertTrue(PersonName.match_middle_as_first(PersonName("Edgar Hoover"), PersonName("J. Edgar Hoover"), True))

    def test_with_initials_false_dont_resolve_initials(self):
        self.assertFalse(PersonName.match_middle_as_first(PersonName("J. E. Hoover"), PersonName("Edgar Hoover"), False))

    def test_with_a_nick_dict_resolve_nicknames(self):
        self.assertTrue(PersonName.match_middle_as_first( \
            PersonName("Ed McMahan"), PersonName("W. Edwin McMahan"), \
            False, \
            {'ED': set(('ED', 'EDWIN')), 'EDWIN': set(('ED', 'EDWIN'))}
        ))


    def test_without_a_nick_dict_dont_resolve_nicknames(self):
        self.assertFalse(PersonName.match_middle_as_first(
            PersonName("Ed McMahan"), PersonName("W. Edwin McMahan"), 
            False
        ))

    def test_non_matching_middle_names_should_fail(self):
        self.assertFalse(PersonName.match_middle_as_first(
            PersonName("J Edgar Hoover"), PersonName("Bob Edgar Hoover"),
            True
        ))

class TestOrganizationName(TestCase):

    def test(self):
        a = OrganizationName("Chronical Books LLC")
        self.assertEqual(a.base_name, 'CHRONICAL BOOKS')
        self.assertEqual(a.inc, 'LLC')
        self.assertTrue(a.is_company())
        self.assertFalse(a.is_politician())
        self.assertEqual(a.search_string(), 'CHRONICAL BOOKS')

        self.assertEqual(OrganizationName("Pizza Hut"), OrganizationName("Pizza Hut Inc"))

        self.assertEqual(OrganizationName("Sunkist Growers, Incorporated"), OrganizationName("Sunkist Growers"))

        o = OrganizationName("Raytheon Co.")
        self.assertEqual(o.base_name, 'RAYTHEON')
        self.assertEqual(o.inc, 'COMPANY')
        self.assertEqual(OrganizationName("Raytheon Company"), OrganizationName("Raytheon"))

        self.assertTrue(OrganizationName("RAYTHEON COmpany") == OrganizationName("RaYtHeOn company"))
        self.assertTrue(OrganizationName("THE ARC OF THE UNITED STATES") == OrganizationName("Arc of the United States"))

        self.assertTrue(OrganizationName("Firstline Transportation Security") == OrganizationName("FirstLine Transportation Security, Inc."))

        self.assertFalse(OrganizationName("united states department of State").is_politician())

        self.assertFalse(OrganizationName("1994 Group") == OrganizationName("Group"))

        self.assertFalse(OrganizationName("180 Solutions") == OrganizationName("Solutions"))

        self.assertTrue(OrganizationName("1-800 Contacts") == OrganizationName("1800 Contacts"))

        self.assertFalse(OrganizationName("166 Research") == OrganizationName("Research"))

        for name, base in (
                 ("HAGMAN FOR ASSEMBLY", "HAGMAN"),
                 ("Friends for Gregory Meeks", "Gregory Meeks"),
                 ("SWANSON FOR ASSEMBLY 2008", "SWANSON"),
                 ("Welch For Congress", "Welch"),
                 ("Cunningham Campaign Committee", "Cunningham"),
                 ("Cummings for Congress Campaign Committee", "Cummings"),
                 ("NEIGHBORS FOR EARL EHRHART", "EARL EHRHART"),
                 ("NEIGHBORS UNITED TO ELECT FRANK DICICO", "FRANK DICICO"),
                ):
            o = OrganizationName(name)
            self.assertTrue(o.is_politician())
            self.assertEqual(o.base_name, base)

        self.assertEqual(OrganizationName("JIM JONES FOR ASSEMBLY"), PersonName("Jim Jones"))
        self.assertEqual(PersonName("Jim Jones"), OrganizationName("JIM JONES FOR ASSEMBLY"))


    def test_eq_clean(self):
        self.assertEqual(OrganizationName.eq_clean("THE ARC OF THE UNITED STATES"), 'ARC UNITED STATES')

        self.assertEqual(OrganizationName.eq_clean("The official theater theof ofthe"), 'OFFICIAL THEATER THEOF OFTHE')

class TestWPAPI(TestCase):

    def test_title_search_redirects(self):
        self.assertEqual(title_search_redirects(u"Atlantic Richfield"), {u'ARCO': u'Atlantic Richfield'})

        self.assertEqual(title_search_redirects(u"PANERA"), {u'Panera Bread': u'PANERA'})

        self.assertEqual(title_search_redirects(u"Barack Obama"), {u'Barack Obama': u'Barack Obama'})
