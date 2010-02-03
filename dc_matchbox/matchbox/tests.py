

from datetime import datetime
from uuid import uuid4
import unittest

from dcdata.contribution.models import Contribution, sql_names
from dcdata.models import Import
from models import Entity, EntityAlias, EntityAttribute, Normalization
from matchbox_scripts.contribution.build_contribution_entities import get_recipient_type
from matchbox_scripts.support.build_entities import populate_entities, build_entity
from matchbox_scripts.contribution.normalize_contributions import run as run_normalization_script
from matchbox_scripts.contribution.normalize import normalize_contributions
from matchbox_scripts.contribution.build_aggregates import build_aggregates
from matchbox.queries import search_entities_by_name, merge_entities, _prepend_pluses,\
    associate_transactions, _pairs_to_dict, disassociate_transactions
from matchbox_scripts.contribution.build_big_hitters import build_big_hitters




class TestQueries(unittest.TestCase):
    NAMESPACE = 'urn:unittest:transaction'

    def save_contribution(self, org_name, org_entity):
        c = Contribution(organization_name=org_name, 
                     organization_urn='urn:unittest:organization:' + org_name,
                     organization_entity=org_entity,
                     datestamp=datetime.now(),
                     cycle='09', 
                     transaction_namespace=self.NAMESPACE,
                     import_reference=self.import_)
        c.save()
        

    def setUp(self):
        """ 
        to do: set up some basic transactions, the run the build_entities and normalize scripts.
        
        Also add an entity with no corresponding transactions.
        """
        
        print("Setting up database...")
        Import.objects.all().delete()
        Contribution.objects.all().delete()
        Entity.objects.all().delete()
        EntityAlias.objects.all().delete()
        EntityAttribute.objects.all().delete()
        Normalization.objects.all().delete()
        
        self.import_ = Import()
        self.import_.save()
        
        self.apple_id = uuid4().hex
        self.apricot_id = uuid4().hex
        self.avacado_id = uuid4().hex
        
        for (org_name, org_entity) in [('Apple', self.apple_id), ('Apple Juice', self.apple_id), ('Apricot', self.apricot_id)]:
            self.save_contribution(org_name, org_entity)

        populate_entities(sql_names['contribution'], 
                          sql_names['contribution_organization_entity'], 
                          [sql_names['contribution_organization_name']],
                          sql_names['contribution_organization_urn'],
                          'organization')
        
        orphan = Entity(id=self.avacado_id, name=u'Avacado', type='organization')
        orphan.save()
        orphan.aliases.create(alias=u'Avacado')
        
        run_normalization_script()
        
        
        
        
    def test_populate_entities(self):
        self.assertEqual(3, Entity.objects.count())
        
        apple = Entity.objects.get(pk=self.apple_id)
        self.assertTrue(apple.name in ("Apple", "Apple Juice"))
        self.assertEqual(2, Contribution.objects.with_entity(apple, ['organization_entity']).count())
        
        apple_alias = EntityAlias.objects.get(alias="Apple")
        self.assertEqual(apple.id, apple_alias.entity.id)
        
        self.assertEqual(3, apple.attributes.count())
        self.assertEqual(1, apple.attributes.filter(namespace='urn:unittest:organization', value='Apple').count())
        self.assertEqual(1, apple.attributes.filter(namespace='urn:unittest:organization', value='Apple Juice').count())
        self.assertEqual(1, apple.attributes.filter(namespace=EntityAttribute.ENTITY_ID_NAMESPACE, value=apple.id).count())


        apricot = Entity.objects.get(name="Apricot")
        self.assertEqual(1, Contribution.objects.with_entity(apricot, ['organization_entity']).count())
        
        apricot_alias = EntityAlias.objects.get(alias="Apricot")
        self.assertEqual(apricot.id, apricot_alias.entity.id)
        
        self.assertEqual(2, apricot.attributes.count())
        self.assertEqual(1, apricot.attributes.filter(namespace='urn:unittest:organization', value='Apricot').count())
        self.assertEqual(1, apricot.attributes.filter(namespace=EntityAttribute.ENTITY_ID_NAMESPACE, value=apricot.id).count())

        
        avacado = Entity.objects.get(name='Avacado')
        self.assertEqual(0, Contribution.objects.with_entity(avacado, ['organization_entity']).count())
        
    def test_populate_entities_cross_column_duplication(self):
        Contribution.objects.create(recipient_name="Apple Sauce",
                                    recipient_entity=self.apple_id,
                                    recipient_urn="urn:unittest:recipient:" + "Apple Sauce",
                                    datestamp=datetime.now(),
                                    cycle='09', 
                                    transaction_namespace=self.NAMESPACE,
                                    import_reference=self.import_)
        
        Contribution.objects.create(recipient_name="Apple",
                                    recipient_entity=self.apple_id,
                                    recipient_urn="urn:unittest:recipient:" + "Apple",
                                    datestamp=datetime.now(),
                                    cycle='09', 
                                    transaction_namespace=self.NAMESPACE,
                                    import_reference=self.import_)
        
        populate_entities(sql_names['contribution'],
                  sql_names['contribution_recipient_entity'],
                  [sql_names['contribution_recipient_name']],
                  sql_names['contribution_recipient_urn'],
                  'fruits')
        
        self.assertEqual(3, Entity.objects.count())
        
        apple = Entity.objects.get(id=self.apple_id)
        self.assertEqual(2, Contribution.objects.with_entity(apple, ['organization_entity']).count())
        self.assertEqual(2, Contribution.objects.with_entity(apple, ['recipient_entity']).count())
        self.assertEqual(4, Contribution.objects.with_entity(apple).count())
        
        self.assertEqual(3, apple.aliases.count())
        self.assertEqual(1, apple.aliases.filter(alias='Apple').count())
        self.assertEqual(1, apple.aliases.filter(alias='Apple Juice').count())
        self.assertEqual(1, apple.aliases.filter(alias='Apple Sauce').count())
        
        self.assertEqual(5, apple.attributes.count())
        self.assertEqual(1, apple.attributes.filter(namespace='urn:unittest:organization', value='Apple').count())
        self.assertEqual(1, apple.attributes.filter(namespace='urn:unittest:organization', value='Apple Juice').count())
        self.assertEqual(1, apple.attributes.filter(namespace='urn:unittest:recipient', value='Apple Sauce').count())
        self.assertEqual(1, apple.attributes.filter(namespace='urn:unittest:recipient', value='Apple').count())
        self.assertEqual(1, apple.attributes.filter(namespace=EntityAttribute.ENTITY_ID_NAMESPACE, value=apple.id).count())
        
        
    def test_populate_entities_recipient_type(self):
        Contribution.objects.create(recipient_name="Apple Council",
                                    recipient_entity=uuid4().hex,
                                    recipient_type='C',
                                    datestamp=datetime.now(),
                                    cycle='09', 
                                    transaction_namespace=self.NAMESPACE,
                                    import_reference=self.import_)
        
        Contribution.objects.create(recipient_name="Apple Smith",
                                    recipient_entity=uuid4().hex,
                                    recipient_type='P',
                                    datestamp=datetime.now(),
                                    cycle='09', 
                                    transaction_namespace=self.NAMESPACE,
                                    import_reference=self.import_)
        
        populate_entities(sql_names['contribution'],
                          sql_names['contribution_recipient_entity'],
                          [sql_names['contribution_recipient_name']],
                          sql_names['contribution_recipient_urn'],
                          get_recipient_type,
                          sql_names['contribution_recipient_type'])
        
        self.assertEqual(1, Entity.objects.filter(type='committee').count())
        self.assertEqual(1, Entity.objects.filter(type='committee', name='Apple Council').count())
        
        self.assertEqual(1, Entity.objects.filter(type='politician').count())
        self.assertEqual(1, Entity.objects.filter(type='politician', name='Apple Smith').count())

    def test_search_entities_by_name(self):
        build_aggregates()
        
        results = list(search_entities_by_name(u'a', ['organization']))
        
        self.assertEqual(3, len(results))
        
        ((_, first_name, first_count, _), (_, second_name, second_count, _), (_, third_name, third_count, _)) = results
        
        self.assertTrue(first_name in ['Apple', 'Apple Juice'])
        self.assertEqual(2, first_count)
        
        self.assertEqual('Apricot', second_name)
        self.assertEqual(1, second_count)
        
        self.assertEqual('Avacado', third_name)
        self.assertEqual(0, third_count)


    def test_search_entities_by_name_multiple_aliases(self):
        apple = Entity.objects.get(id=self.apple_id)
        apple.aliases.create(alias="Appetite")
        Normalization.objects.create(original="Appetite", normalized="appetite")
        build_aggregates()
        
        result = search_entities_by_name(u'app', ['organization'])
        
        (id, name, count, dollar_total) = result.__iter__().next()
        
        self.assertTrue(name in ['Apple', 'Apple Juice'])
        self.assertEqual(2, count)

            
    def test_merge_entities(self):
        new_id = merge_entities((self.apple_id, self.apricot_id), Entity(name=u"Applicot"))
        
        self.assertEqual(2, Entity.objects.count())
        applicot = Entity.objects.get(name="Applicot")
        self.assertEqual(new_id, applicot.id)
        
        self.assertEqual(u'applicot', Normalization.objects.get(original="Applicot").normalized)
        
        self.assertEqual(3, Contribution.objects.with_entity(applicot, ['organization_entity']).count())
        
        self.assertEqual(4, applicot.aliases.count())
        self.assertEqual(1, applicot.aliases.filter(alias='Apple').count())
        self.assertEqual(1, applicot.aliases.filter(alias='Apple Juice').count())
        self.assertEqual(1, applicot.aliases.filter(alias='Apricot').count())
        self.assertEqual(1, applicot.aliases.filter(alias='Applicot').count())
        
    def test_merge_entities_alias_duplication(self):
        apple = Entity.objects.get(id=self.apple_id)
        apple.aliases.create(alias="Delicious")
        
        apricot = Entity.objects.get(id=self.apricot_id)
        apricot.aliases.create(alias="Delicious")
        
        merge_entities((apple.id, apricot.id), Entity(name=u'Applicot'))
        
        applicot = Entity.objects.get(name="Applicot")

        self.assertEqual(5, applicot.aliases.count())
        self.assertEqual(1, applicot.aliases.filter(alias='Apple').count())
        self.assertEqual(1, applicot.aliases.filter(alias='Apple Juice').count())
        self.assertEqual(1, applicot.aliases.filter(alias='Apricot').count())
        self.assertEqual(1, applicot.aliases.filter(alias='Applicot').count())
        self.assertEqual(1, applicot.aliases.filter(alias='Delicious').count())
        
    def test_merge_entities_attribute_duplication(self):
        apple = Entity.objects.get(id=self.apple_id)
        apple.attributes.all().delete()
        apple.attributes.create(namespace='color', value='red')
        apple.attributes.create(namespace='color', value='yellow')
        apple.attributes.create(namespace='texture', value='crisp')
        
        apricot = Entity.objects.get(id=self.apricot_id)
        apricot.attributes.all().delete()
        apricot.attributes.create(namespace='color', value='yellow')
        apricot.attributes.create(namespace='texture', value='soft')
        
        merge_entities((apple.id, apricot.id), Entity(name=u'Applicot'))
        
        applicot = Entity.objects.get(name="Applicot")
        
        self.assertEqual(5, applicot.attributes.count())
        self.assertEqual(1, applicot.attributes.filter(namespace='color', value='red').count())
        self.assertEqual(1, applicot.attributes.filter(namespace='color', value='yellow').count())
        self.assertEqual(1, applicot.attributes.filter(namespace='texture', value='crisp').count())
        self.assertEqual(1, applicot.attributes.filter(namespace='texture', value='soft').count())
        
    def test_merge_entities_previous_ids(self):
        merge_entities((self.apple_id, self.apricot_id), Entity(name=u'Applicot'))
        applicot = Entity.objects.get(name="Applicot")

        self.assertEqual(6, applicot.attributes.count())
        self.assertEqual(1, applicot.attributes.filter(namespace=EntityAttribute.ENTITY_ID_NAMESPACE, value=self.apple_id).count())
        self.assertEqual(1, applicot.attributes.filter(namespace=EntityAttribute.ENTITY_ID_NAMESPACE, value=self.apricot_id).count())
        self.assertEqual(1, applicot.attributes.filter(namespace=EntityAttribute.ENTITY_ID_NAMESPACE, value=applicot.id).count())
        self.assertEqual(1, applicot.attributes.filter(namespace='urn:unittest:organization', value='Apricot').count())
        self.assertEqual(1, applicot.attributes.filter(namespace='urn:unittest:organization', value='Apple Juice').count())
        self.assertEqual(1, applicot.attributes.filter(namespace='urn:unittest:organization', value='Apple').count())
#        
    def test_merge_entities_and_with_entity(self):
        self.assertEqual(2, Contribution.objects.with_entity(Entity.objects.get(pk=self.apple_id)).count())
        self.assertEqual(1, Contribution.objects.with_entity(Entity.objects.get(pk=self.apricot_id)).count())
        
        apple_head = Contribution.objects.create(parent_organization_name="Apple Head",
                                    parent_organization_entity=self.apple_id,
                                    datestamp=datetime.now(),
                                    cycle='09', 
                                    transaction_namespace=self.NAMESPACE,
                                    import_reference=self.import_)
        apple_catcher = Contribution.objects.create(recipient_name="Apple Catcher",
                                    recipient_entity=self.apple_id,
                                    datestamp=datetime.now(),
                                    cycle='09', 
                                    transaction_namespace=self.NAMESPACE,
                                    import_reference=self.import_)
        apricot_council = Contribution.objects.create(committee_name="Apricot Council",
                                    committee_entity=self.apricot_id,
                                    datestamp=datetime.now(),
                                    cycle='09', 
                                    transaction_namespace=self.NAMESPACE,
                                    import_reference=self.import_)
        apricot_picker = Contribution.objects.create(organization_name="Apricot Picker",
                                    organization_entity=self.apricot_id,
                                    datestamp=datetime.now(),
                                    cycle='09', 
                                    transaction_namespace=self.NAMESPACE,
                                    import_reference=self.import_)
        
        apple = Entity.objects.get(pk=self.apple_id)
        
        self.assertEqual(4, Contribution.objects.with_entity(apple).count())
        self.assertEqual(2, Contribution.objects.with_entity(apple, ['organization_entity']).count())
        self.assertEqual(1, Contribution.objects.with_entity(apple, ['parent_organization_entity']).count())
        self.assertEqual(1, Contribution.objects.with_entity(apple, ['recipient_entity']).count())
        self.assertEqual(0, Contribution.objects.with_entity(apple, ['committee_entity']).count())
        
        merge_entities([self.apple_id, self.apricot_id], Entity(name=u'Applicot'))
        applicot = Entity.objects.get(name='Applicot')
        
        self.assertEqual(7, Contribution.objects.with_entity(applicot).count())
        self.assertEqual(apple_head, Contribution.objects.with_entity(applicot, ['parent_organization_entity'])[0])
        self.assertEqual(apple_catcher, Contribution.objects.with_entity(applicot, ['recipient_entity'])[0])
        self.assertEqual(apricot_council, Contribution.objects.with_entity(applicot, ['committee_entity'])[0])
        self.assertTrue(apricot_picker in Contribution.objects.with_entity(applicot, ['organization_entity']))
        
    def test_multiple_name_columns(self):
        id = uuid4().hex
        Contribution.objects.create(organization_name="one",
                                                     contributor_employer="two",
                                                    organization_entity=id,
                                                    datestamp=datetime.now(),
                                                    cycle='09', 
                                                    transaction_namespace=self.NAMESPACE,
                                                    import_reference=self.import_)
        Contribution.objects.create(organization_name="three",
                                                    organization_entity=id,
                                                    datestamp=datetime.now(),
                                                    cycle='09', 
                                                    transaction_namespace=self.NAMESPACE,
                                                    import_reference=self.import_)
        Contribution.objects.create(contributor_employer="four",
                                                    organization_entity=id,
                                                    datestamp=datetime.now(),
                                                    cycle='09', 
                                                    transaction_namespace=self.NAMESPACE,
                                                    import_reference=self.import_)
        Contribution.objects.create(organization_entity=id,
                                                    datestamp=datetime.now(),
                                                    cycle='09', 
                                                    transaction_namespace=self.NAMESPACE,
                                                    import_reference=self.import_)
        
        populate_entities(sql_names['contribution'], 
                          sql_names['contribution_organization_entity'], 
                          [sql_names['contribution_organization_name'], sql_names['contribution_contributor_employer']],
                          sql_names['contribution_organization_urn'],
                          'organization')
        
        aliases = [entity_alias.alias for entity_alias in EntityAlias.objects.filter(entity=id)]
        
        self.assertEqual(4, len(aliases))
        self.assertTrue('one' in aliases)
        self.assertTrue('two' in aliases)
        self.assertTrue('three' in aliases)
        self.assertTrue('four' in aliases)
    
    


class BaseEntityBuildTests(unittest.TestCase):
    NAMESPACE = 'urn:unittest:transaction'
    
    def create_contribution(self, **kwargs):
        c = Contribution(**kwargs)
        if 'cycle' not in kwargs:
            c.cycle='09'
        c.transaction_namespace=self.NAMESPACE
        c.import_reference=self.import_
        c.save()
    
    
    def setUp(self):
        print("Setting up database...")
        Import.objects.all().delete()
        Contribution.objects.all().delete()
        Entity.objects.all().delete()
        EntityAlias.objects.all().delete()
        EntityAttribute.objects.all().delete()
        Normalization.objects.all().delete()
        
        self.import_ = Import()
        self.import_.save()
        
        
        
class TestEntityBuild(BaseEntityBuildTests):        
    def test_normalize(self):
        self.create_contribution(contributor_name='contributor duplicate')
        self.create_contribution(contributor_name='contributor duplicate')
        self.create_contribution(organization_name='MULTIPLE ORIGINALS')
        self.create_contribution(organization_name='multiple-originals')
        self.create_contribution(parent_organization_name='multiple...originals')
        self.create_contribution(committee_name='cross-column duplicate')
        self.create_contribution(recipient_name='cross-column duplicate')
        self.create_contribution(contributor_name='trailing whitespace ')
        self.create_contribution(contributor_name='trailing whitespace')
        
        normalize_contributions()
        
        self.assertEqual(1, Normalization.objects.filter(normalized='contributorduplicate').count())
        self.assertEqual(3, Normalization.objects.filter(normalized='multipleoriginals').count())
        self.assertEqual(1, Normalization.objects.filter(normalized='crosscolumnduplicate').count())
        self.assertEqual(2, Normalization.objects.filter(normalized='trailingwhitespace').count())
            
        
    def test_build_entity(self):
        build_entity('Apple', 'organization', [('contributor_name', u'Apple Co', 'contributor_entity')])
        
        self.assertEqual(1, Entity.objects.count())
        self.assertEqual(1, Entity.objects.filter(name='Apple').count())
        self.assertEqual(1, Entity.objects.filter(type='organization').count())
        
        self.create_contribution(contributor_name='Banana Bar')

        normalize_contributions()
        build_entity('Banana Bar', 'organization', [('contributor_name', u'Banana Bar', 'contributor_entity')])
        
        self.assertEqual(2, Entity.objects.count())
        c = Contribution.objects.get(contributor_name='Banana Bar')
        e = Entity.objects.get(name='Banana Bar')
        self.assertEqual(e.id, c.contributor_entity)
        
        self.create_contribution(organization_name='Coconut Lounge')
        self.create_contribution(organization_urn='1234')
        
        normalize_contributions()
        build_entity('Coconut Camp', 'organization', [('organization_name', u'Coconut Lounge', 'organization_entity'),
                                                      ('organization_urn', u'1234', 'organization_entity')])
        
        e = Entity.objects.get(name='Coconut Camp')
        self.assertEqual(2, Contribution.objects.filter(organization_entity=e.id).count())
        
    def test_big_hitters(self):
        self.create_contribution(contributor_urn='urn:nimsp:contributor:1')
        self.create_contribution(organization_urn='urn:nimsp:contributor:1')
        self.create_contribution(parent_organization_urn='urn:nimsp:contributor:1')
        self.create_contribution(contributor_urn='urn:crp:contributor:D000031229') # won't count toward total b/c we don't search on CRP IDs, since they don't occur in actual data
        self.create_contribution(contributor_name='1-800 Contacts')
        self.create_contribution(organization_name='1-800 Contacts')
        self.create_contribution(parent_organization_name='1-800 Contacts')
        
        whitelist_csv = ["D000031229, 1, 1-800 Contacts"]
        
        normalize_contributions()
        build_big_hitters(whitelist_csv)
        
        e = Entity.objects.get(name="1-800 Contacts")
        
        self.assertEqual(2, Contribution.objects.filter(contributor_entity=e.id).count())
        self.assertEqual(2, Contribution.objects.filter(organization_entity=e.id).count())
        self.assertEqual(2, Contribution.objects.filter(parent_organization_entity=e.id).count())
        
    def test_entity_aggregates(self):
        self.create_contribution(contributor_name='FooBar', amount=100)
        self.create_contribution(contributor_employer='FooBar Corp')
        self.create_contribution(organization_name='ZapWow', amount=100)
        self.create_contribution(parent_organization_name='ZapWow', amount=200)
        self.create_contribution(committee_name='ZapWow', amount=400)
        self.create_contribution(recipient_name='ZapWow', amount=800)
        
        whitelist = ["0, 0, FooBar", "0, 0, ZapWow"]
        
        normalize_contributions()
        build_big_hitters(whitelist)
        build_aggregates()
        
        foobar = Entity.objects.get(name="FooBar")
        self.assertEqual(2, foobar.contribution_count)
        self.assertEqual(100, foobar.contribution_amount)
        
        zapwow = Entity.objects.get(name="ZapWow")
        self.assertEqual(4, zapwow.contribution_count)
        self.assertEqual(1500, zapwow.contribution_amount)
        
    def test_entity_aliases(self):
        self.create_contribution(contributor_name='Bob',
                                 contributor_employer='Waz')
        self.create_contribution(organization_name='Waz Co',
                                 parent_organization_name='Wazzo Intl')
        
        whitelist=["0, 0, Waz Corp", "0, 0, Bob", "0, 0, Wazzo Intl"]
        
        normalize_contributions()
        build_big_hitters(whitelist)
        build_aggregates()
        
        self.assertEqual(3, Entity.objects.count())
        
        e = Entity.objects.get(name='Bob')
        self.assertEqual(1, EntityAlias.objects.filter(entity=e.id).count())
        self.assertEqual(1, EntityAlias.objects.filter(entity=e.id, alias='Bob').count())
        
        e = Entity.objects.get(name='Wazzo Intl')
        self.assertEqual(1, EntityAlias.objects.filter(entity=e.id).count())
        self.assertEqual(1, EntityAlias.objects.filter(entity=e.id, alias='Wazzo Intl').count())

        e = Entity.objects.get(name='Waz Corp')
        self.assertEqual(2, EntityAlias.objects.filter(entity=e.id).count())
        self.assertEqual(1, EntityAlias.objects.filter(entity=e.id, alias='Waz Co').count())
        self.assertEqual(1, EntityAlias.objects.filter(entity=e.id, alias='Waz').count())
        
            
class TestEntityAssociate(BaseEntityBuildTests):
    
    def test_associate_transactions(self):
        self.create_contribution(transaction_id='a', contributor_name='Alice', amount=10)
        self.create_contribution(transaction_id='b', contributor_name='Alice', amount=20)
        self.create_contribution(transaction_id=1, amount=40)
        self.create_contribution(transaction_id=2, amount=80, contributor_name='Bob')
        self.create_contribution(transaction_id=3, amount=160, contributor_urn='urn:unittest:Bob')
        self.create_contribution(transaction_id=4, contributor_employer="Carl")
        self.create_contribution(transaction_id=5, organization_name="Dave")
        self.create_contribution(transaction_id=6, parent_organization_name="Ethan")
        self.create_contribution(transaction_id=7, committee_name="Frank")
        self.create_contribution(transaction_id=8, recipient_name="Greg")
        
        self.create_contribution(transaction_id='m', contributor_name='Mary', contributor_urn='urn:nimsp:contributor:999')
        self.create_contribution(transaction_id='n', contributor_name='Nancy', contributor_urn='urn:nimsp:contributor:999')
        
        whitelist = ["0, 0, Alice", "0, 999, Mary J."]
        
        normalize_contributions()
        build_big_hitters(whitelist)
        build_aggregates()
        
        e = Entity.objects.get(name="Alice")
        self.assertEqual(2, Contribution.objects.filter(contributor_entity=e.id).count())
        self.assertEqual(2, e.contribution_count)
        self.assertEqual(30, e.contribution_amount)
        self.assertEqual(1, EntityAlias.objects.filter(entity=e.id).count())
        self.assertEqual('Alice', EntityAlias.objects.filter(entity=e.id)[0].alias)

        associate_transactions(e.id, 'contributor_entity', [(self.NAMESPACE, '1')])
        
        e = Entity.objects.get(name="Alice")
        self.assertEqual(3, Contribution.objects.filter(contributor_entity=e.id).count())
        self.assertEqual(3, e.contribution_count)
        self.assertEqual(70, e.contribution_amount)
        self.assertEqual(1, EntityAlias.objects.filter(entity=e.id).count())
        self.assertEqual('Alice', EntityAlias.objects.filter(entity=e.id)[0].alias)
        
        associate_transactions(e.id, 'contributor_entity', zip([self.NAMESPACE] * 2, ('2', '3')))

        e = Entity.objects.get(name="Alice")
        self.assertEqual(5, Contribution.objects.filter(contributor_entity=e.id).count())
        self.assertEqual(5, e.contribution_count)
        self.assertEqual(310, e.contribution_amount)
        self.assertEqual(2, EntityAlias.objects.filter(entity=e.id).count())
        self.assertEqual(1, EntityAlias.objects.filter(entity=e.id, alias='Alice').count())
        self.assertEqual(1, EntityAlias.objects.filter(entity=e.id, alias='Bob').count())
# todo: enable when attribute aggregation is working        
#        self.assertEqual(1, EntityAttribute.objects.filter(entity=e.id).count())
#       self.assertEqual(1, EntityAttribute.objects.filter(entity=e.id, namespace='urn:unittest', attribute='Bob').count())

        associate_transactions(e.id, 'organization_entity', [(self.NAMESPACE, '4'), (self.NAMESPACE, '5')])
        associate_transactions(e.id, 'parent_organization_entity', [(self.NAMESPACE, '6')])
        associate_transactions(e.id, 'committee_entity', [(self.NAMESPACE, '7')])
        associate_transactions(e.id, 'recipient_entity', [(self.NAMESPACE, '8')])

        e = Entity.objects.get(name="Alice")
        self.assertEqual(10, e.contribution_count)
        self.assertEqual(7, EntityAlias.objects.filter(entity=e.id).count())
        
        disassociate_transactions('contributor_entity', [(self.NAMESPACE, 'b'), (self.NAMESPACE, '2')])

        e = Entity.objects.get(name="Alice")
        self.assertEqual(3, Contribution.objects.filter(contributor_entity=e.id).count())
        self.assertEqual(8, e.contribution_count)
        self.assertEqual(210, e.contribution_amount)
        self.assertEqual(6, EntityAlias.objects.filter(entity=e.id).count())
        self.assertEqual(1, EntityAlias.objects.filter(entity=e.id, alias='Alice').count())
        self.assertEqual(0, EntityAlias.objects.filter(entity=e.id, alias='Bob').count())

        e = Entity.objects.get(name="Mary J.")
        self.assertEqual(2, Contribution.objects.filter(contributor_entity=e.id).count())
        self.assertEqual(2, e.contribution_count)
        self.assertEqual(2, EntityAlias.objects.filter(entity=e.id).count())
        self.assertEqual(1, EntityAlias.objects.filter(entity=e.id, alias="Mary").count())
        self.assertEqual(1, EntityAlias.objects.filter(entity=e.id, alias="Nancy").count())
        
        associate_transactions(e.id, 'contributor_entity', [(self.NAMESPACE, 'a'), (self.NAMESPACE, 'b')])
        
        e = Entity.objects.get(name="Mary J.")
        self.assertEqual(4, Contribution.objects.filter(contributor_entity=e.id).count())
        self.assertEqual(4, e.contribution_count)
        self.assertEqual(30, e.contribution_amount)
        self.assertEqual(3, EntityAlias.objects.filter(entity=e.id).count())
        self.assertEqual(1, EntityAlias.objects.filter(entity=e.id, alias="Mary").count())
        self.assertEqual(1, EntityAlias.objects.filter(entity=e.id, alias="Nancy").count())
        self.assertEqual(1, EntityAlias.objects.filter(entity=e.id, alias="Alice").count())
  
        e = Entity.objects.get(name="Alice")
        self.assertEqual(2, Contribution.objects.filter(contributor_entity=e.id).count())
        self.assertEqual(7, e.contribution_count)
        self.assertEqual(200, e.contribution_amount)
        self.assertEqual(5, EntityAlias.objects.filter(entity=e.id).count())
        self.assertEqual(0, EntityAlias.objects.filter(entity=e.id, alias='Alice').count())
        
            
class TestUtils(unittest.TestCase):
    def test_pairs_to_dict(self):
        self.assertEqual({}, _pairs_to_dict([]))
        
        self.assertEqual({'a': set([1])}, _pairs_to_dict([('a',1)]))
        
        self.assertEqual({'a': set([1,2])}, _pairs_to_dict([('a',1),('a',2)]))
        self.assertEqual({'a': set([1]), 'b': set([2])}, _pairs_to_dict([('a', 1), ('b', 2)]))
                         
    
    def test_prepend_pluses(self):
        self.assertEqual("", _prepend_pluses(""))
        self.assertEqual("", _prepend_pluses("   "))
        
        self.assertEqual("+a", _prepend_pluses("a"))
        self.assertEqual("+apple +computer", _prepend_pluses("apple computer"))
        self.assertEqual("+apple +computer, +inc.", _prepend_pluses("apple computer, inc."))
        self.assertEqual("+Procter +& +Gamble", _prepend_pluses("Procter & Gamble"))
        self.assertEqual("+Emily's +List", _prepend_pluses("Emily's List"))
        
    
        