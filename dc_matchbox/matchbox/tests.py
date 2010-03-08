

from datetime import datetime
from matchbox.management.commands.build_aggregates import build_aggregates
import unittest

from django.db import connection

from dcdata.contribution.models import Contribution,\
    UNITTEST_TRANSACTION_NAMESPACE, NIMSP_TRANSACTION_NAMESPACE,\
    CRP_TRANSACTION_NAMESPACE
from dcdata.models import Import
from models import Entity, EntityAlias, EntityAttribute, Normalization
from dcdata.management.commands.normalize_contributions import normalize_contributions
from matchbox.queries import search_entities_by_name, merge_entities, _prepend_pluses,\
    associate_transactions, _pairs_to_dict, disassociate_transactions
from matchbox.management.commands.build_big_hitters import build_big_hitters,\
    build_entity
from dcdata.utils.sql import dict_union



class BaseMatchboxTest(unittest.TestCase):
    
    def create_contribution(self, **kwargs):
        c = Contribution(**kwargs)
        if 'cycle' not in kwargs:
            c.cycle='09'
        if 'transaction_namespace' not in kwargs:
            c.transaction_namespace=UNITTEST_TRANSACTION_NAMESPACE
        c.import_reference=self.import_
        c.save()
    
    def assertFilter(self, model, primary, members):
        self.assertEqual(len(members), model.objects.filter(**primary).count())
        for member in members:
            self.assertEqual(1, model.objects.filter(**dict_union(primary, member)).count())
    
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
        
        

class TestQueries(BaseMatchboxTest):

    def setUp(self):
        """ 
        to do: set up some basic transactions, the run the build_entities and normalize scripts.
        
        Also add an entity with no corresponding transactions.
        """
        
        super(TestQueries, self).setUp()
        
        
        self.create_contribution(transaction_namespace=NIMSP_TRANSACTION_NAMESPACE, organization_name='Apple', organization_ext_id='1')
        self.create_contribution(transaction_namespace=NIMSP_TRANSACTION_NAMESPACE, organization_name='Apple Juice', organization_ext_id='1')
        self.create_contribution(transaction_namespace=NIMSP_TRANSACTION_NAMESPACE, organization_name='Apricot', organization_ext_id='2')
        
        build_big_hitters(["0, 1, Apple", "0, 2, Apricot"])
        
        orphan = Entity.objects.create(name=u'Avacado', type='organization')
        orphan.aliases.create(alias=u'Avacado')
        
        self.apple_id = Entity.objects.get(name="Apple").id
        self.apricot_id = Entity.objects.get(name="Apricot").id
        self.avacado_id = orphan.id
        
        normalize_contributions()
        Normalization.objects.create(original='Avacado', normalized='avacado')
        
        

    def test_search_entities_by_name(self):
        cursor = connection.cursor()
        for command in open( '../dc_data/scripts/contribution_name_indexes.sql', 'r'):
            if command.strip() and not command.startswith('--'):
                cursor.execute(command)
  
        build_aggregates()
        
        results = list(search_entities_by_name(u'a', ['organization']))
        
        self.assertEqual(3, len(results))
        
        ((_, first_name, first_count, _, _), (_, second_name, second_count, _, _), (_, third_name, third_count, _, _)) = results
        
        self.assertTrue(first_name in ['Apple', 'Apple Juice'])
        self.assertEqual(2, first_count)
        
        self.assertEqual('Apricot', second_name)
        self.assertEqual(1, second_count)
        
        self.assertEqual('Avacado', third_name)
        self.assertEqual(0, third_count)


    def test_search_entities_by_name_multiple_aliases(self):
        build_aggregates()

        apple = Entity.objects.get(id=self.apple_id)
        apple.aliases.create(alias="Appetite")
        Normalization.objects.create(original="Appetite", normalized="appetite")
        
        result = search_entities_by_name(u'app', ['organization'])
        
        (id, name, count, _, _) = result.__iter__().next()
        
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
        self.assertEqual(1, applicot.attributes.filter(namespace='urn:nimsp:organization', value='1').count())
        self.assertEqual(1, applicot.attributes.filter(namespace='urn:nimsp:organization', value='2').count())
        self.assertEqual(1, applicot.attributes.filter(namespace='urn:crp:organization', value='0').count())
#        
    def test_merge_entities_and_with_entity(self):
        self.assertEqual(2, Contribution.objects.with_entity(Entity.objects.get(pk=self.apple_id)).count())
        self.assertEqual(1, Contribution.objects.with_entity(Entity.objects.get(pk=self.apricot_id)).count())
        
        apple_head = Contribution.objects.create(parent_organization_name="Apple Head",
                                    parent_organization_entity=self.apple_id,
                                    date=datetime.now(),
                                    cycle='09', 
                                    transaction_namespace=UNITTEST_TRANSACTION_NAMESPACE,
                                    import_reference=self.import_)
        apple_catcher = Contribution.objects.create(recipient_name="Apple Catcher",
                                    recipient_entity=self.apple_id,
                                    date=datetime.now(),
                                    cycle='09', 
                                    transaction_namespace=UNITTEST_TRANSACTION_NAMESPACE,
                                    import_reference=self.import_)
        apricot_council = Contribution.objects.create(committee_name="Apricot Council",
                                    committee_entity=self.apricot_id,
                                    date=datetime.now(),
                                    cycle='09', 
                                    transaction_namespace=UNITTEST_TRANSACTION_NAMESPACE,
                                    import_reference=self.import_)
        apricot_picker = Contribution.objects.create(organization_name="Apricot Picker",
                                    organization_entity=self.apricot_id,
                                    date=datetime.now(),
                                    cycle='09', 
                                    transaction_namespace=UNITTEST_TRANSACTION_NAMESPACE,
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
        

    
    

class TestEntityBuild(BaseMatchboxTest):        
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
        build_entity(u'Apple', 'organization', '999', '999')
        
        self.assertEqual(1, Entity.objects.count())
        self.assertEqual(1, Entity.objects.filter(name='Apple').count())
        self.assertEqual(1, Entity.objects.filter(type='organization').count())
        
        self.create_contribution(contributor_name='Banana Bar')

        normalize_contributions()
        build_entity(u'Banana Bar', 'organization', '999', '999')
        
        self.assertEqual(2, Entity.objects.count())
        c = Contribution.objects.get(contributor_name='Banana Bar')
        e = Entity.objects.get(name='Banana Bar')
        self.assertEqual(e.id, c.contributor_entity)
        
        self.create_contribution(organization_name='Coconut Lounge')
        self.create_contribution(transaction_namespace=NIMSP_TRANSACTION_NAMESPACE, organization_ext_id='1234')
        self.create_contribution(transaction_namespace=CRP_TRANSACTION_NAMESPACE, organization_ext_id='999')
        self.create_contribution(transaction_namespace=CRP_TRANSACTION_NAMESPACE, organization_ext_id='1234')

        normalize_contributions()
        build_entity(u'Coconut Lounge', 'organization', '999', '1234')
        
        e = Entity.objects.get(name='Coconut Lounge')
        self.assertEqual(2, Contribution.objects.filter(organization_entity=e.id).count())
        
    def test_big_hitters(self):
        self.create_contribution(transaction_namespace=NIMSP_TRANSACTION_NAMESPACE, contributor_ext_id='1')
        self.create_contribution(transaction_namespace=NIMSP_TRANSACTION_NAMESPACE, organization_ext_id='1')
        self.create_contribution(transaction_namespace=NIMSP_TRANSACTION_NAMESPACE, parent_organization_ext_id='1')
        self.create_contribution(transaction_namespace=CRP_TRANSACTION_NAMESPACE, contributor_ext_id='D000031229') # won't count toward total b/c we don't search on CRP IDs, since they don't occur in actual data
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
        self.create_contribution(transaction_id='1', contributor_name='FooBar', amount=100)
        self.create_contribution(organization_name='FooBar Corp')
        self.create_contribution(organization_name='ZapWow', amount=100)
        self.create_contribution(parent_organization_name='ZapWow', amount=200)
        self.create_contribution(transaction_id='2', committee_name='ZapWow', amount=400)
        self.create_contribution(recipient_name='ZapWow', amount=800)
        
        whitelist = ["0, 0, FooBar", "0, 0, ZapWow", "0, 0, WhimWham"]
        
        normalize_contributions()
        build_big_hitters(whitelist)
        
        foobar = Entity.objects.get(name="FooBar")
        self.assertEqual(2, foobar.contribution_count)
        self.assertEqual(100, foobar.contribution_total_given)
        
        zapwow = Entity.objects.get(name="ZapWow")
        self.assertEqual(4, zapwow.contribution_count)
        self.assertEqual(300, zapwow.contribution_total_given)
        self.assertEqual(1200, zapwow.contribution_total_received)
        
        merge_entities([foobar.id, zapwow.id], Entity(name=u'foowow'))
        
        foowow = Entity.objects.get(name='foowow')
        self.assertEqual(6, foowow.contribution_count)
        self.assertEqual(400, foowow.contribution_total_given)
        self.assertEqual(1200, foowow.contribution_total_received)
        
        whimwham = Entity.objects.get(name='WhimWham')
        self.assertEqual(0, whimwham.contribution_count)
        self.assertEqual(0, whimwham.contribution_total_given)
        self.assertEqual(0, whimwham.contribution_total_received)
        
        associate_transactions(whimwham.id, 'committee_entity', zip([UNITTEST_TRANSACTION_NAMESPACE] * 2, ('1', '2')))
        
        whimwham = Entity.objects.get(name='WhimWham')
        self.assertEqual(2, whimwham.contribution_count)
        self.assertEqual(0, whimwham.contribution_total_given)
        self.assertEqual(500, whimwham.contribution_total_received)
  
        foowow = Entity.objects.get(name='foowow')
        self.assertEqual(5, foowow.contribution_count)
        self.assertEqual(400, foowow.contribution_total_given)
        self.assertEqual(800, foowow.contribution_total_received)
        
       
        
        
    def test_entity_aliases(self):
        self.create_contribution(contributor_name='Bob',
                                 contributor_employer='Waz',
                                 organization_name='Waz Co')
        self.create_contribution(organization_name='Waz Co',
                                 parent_organization_name='Wazzo Intl')
        
        whitelist=["0, 0, Waz Corp", "0, 0, Bob", "0, 0, Wazzo Intl"]
        
        normalize_contributions()
        build_big_hitters(whitelist)
        
        self.assertEqual(3, Entity.objects.count())
        
        e = Entity.objects.get(name='Bob')
        self.assertEqual(1, EntityAlias.objects.filter(entity=e.id).count())
        self.assertEqual(1, EntityAlias.objects.filter(entity=e.id, alias='Bob').count())
        
        e = Entity.objects.get(name='Wazzo Intl')
        self.assertEqual(1, EntityAlias.objects.filter(entity=e.id).count())
        self.assertEqual(1, EntityAlias.objects.filter(entity=e.id, alias='Wazzo Intl').count())

        e = Entity.objects.get(name='Waz Corp')
        self.assertEqual(3, EntityAlias.objects.filter(entity=e.id).count())
        self.assertEqual(1, EntityAlias.objects.filter(entity=e.id, alias='Waz Corp').count())
        self.assertEqual(1, EntityAlias.objects.filter(entity=e.id, alias='Waz Co').count())
        self.assertEqual(1, EntityAlias.objects.filter(entity=e.id, alias='Waz').count())
        
    def test_entity_attributes(self):
        self.create_contribution(transaction_namespace=NIMSP_TRANSACTION_NAMESPACE,
                                 contributor_ext_id='2', contributor_name='FooBar',
                                 organization_ext_id='3', organization_name='FooBar',
                                 parent_organization_ext_id='4', parent_organization_name='FooBar')
        self.create_contribution(transaction_namespace=NIMSP_TRANSACTION_NAMESPACE,
                                 parent_organization_ext_id='4', parent_organization_name='FooBar',
                                 committee_ext_id='5', committee_name='FooBar',
                                 recipient_ext_id='6', recipient_name='FooBar')
        self.create_contribution(transaction_namespace=CRP_TRANSACTION_NAMESPACE,
                                 contributor_ext_id='7', contributor_name='FooBar')
        
        whitelist=["8, 1, FooBar"]
        
        normalize_contributions()
        build_big_hitters(whitelist)
        
        self.assertEqual(1, Entity.objects.count())
        
        e = Entity.objects.get(name='FooBar')
        self.assertEqual(3, e.contribution_count)
        self.assertEqual(9, EntityAttribute.objects.filter(entity=e.id).count())
        self.assertEqual(1, EntityAttribute.objects.filter(entity=e.id, namespace=EntityAttribute.ENTITY_ID_NAMESPACE, value=e.id).count())
        for (namespace, id) in zip(['urn:nimsp:organization', 'urn:nimsp:contributor', 'urn:nimsp:organization', \
                                    'urn:nimsp:parent_organization', 'urn:nimsp:committee', 'urn:nimsp:recipient', \
                                    'urn:crp:contributor', 'urn:crp:organization'], range(1, 9)):
            self.assertEqual(1, EntityAttribute.objects.filter(entity=e.id, namespace=namespace, value=str(id)).count())


    def test_verified_aggregates(self):
        self.create_contribution(transaction_namespace=NIMSP_TRANSACTION_NAMESPACE, contributor_ext_id = '1', contributor_name='FooBar Co')
        self.create_contribution(transaction_namespace=NIMSP_TRANSACTION_NAMESPACE, contributor_ext_id = '2', contributor_name='FooBar Corp')
        self.create_contribution(transaction_namespace=NIMSP_TRANSACTION_NAMESPACE, contributor_ext_id = '100', contributor_name='Spaz Ltd')
        self.create_contribution(transaction_namespace=NIMSP_TRANSACTION_NAMESPACE, contributor_ext_id = '101', contributor_name='Spaz Limited')
        self.create_contribution(transaction_namespace=NIMSP_TRANSACTION_NAMESPACE, contributor_ext_id = '102', contributor_name='Spaz')
        
        whitelist = ["0, 1, FooBar", "0, 100, Spaz"]
        normalize_contributions()
        build_big_hitters(whitelist)
        
        foobar_id = Entity.objects.get(name='FooBar').id
        self.assertFilter(EntityAlias, {'entity': foobar_id}, [{'alias': 'FooBar', 'verified': True},
                                                               {'alias': 'FooBar Co', 'verified': False},
                                                               {'alias': 'FooBar Corp', 'verified': False}])
        self.assertFilter(EntityAttribute, {'entity':foobar_id}, [{'namespace': 'urn:nimsp:organization', 'value': '1', 'verified': True},
                                                                  {'namespace': EntityAttribute.ENTITY_ID_NAMESPACE, 'value': foobar_id, 'verified': True},
                                                                  {'namespace': 'urn:crp:organization', 'value': '0', 'verified':True},
                                                                  {'namespace': 'urn:nimsp:contributor', 'value': '1', 'verified': False},
                                                                  {'namespace': 'urn:nimsp:contributor', 'value': '2', 'verified': False}])
        
        spaz_id = Entity.objects.get(name='Spaz').id
        self.assertFilter(EntityAlias, {'entity': spaz_id}, [{'alias': 'Spaz', 'verified': True},
                                                             {'alias': 'Spaz Ltd', 'verified': False},
                                                             {'alias': 'Spaz Limited', 'verified': False}])
        self.assertFilter(EntityAttribute, {'entity':spaz_id}, [{'namespace': EntityAttribute.ENTITY_ID_NAMESPACE, 'value': spaz_id, 'verified':True},
                                                                {'namespace': 'urn:crp:organization', 'value': '0', 'verified':True},
                                                                {'namespace': 'urn:nimsp:organization', 'value': '100', 'verified':True},
                                                                {'namespace': 'urn:nimsp:contributor', 'value': '100', 'verified': False},
                                                                {'namespace': 'urn:nimsp:contributor', 'value': '101', 'verified': False},
                                                                {'namespace': 'urn:nimsp:contributor', 'value': '102', 'verified': False}])
        
        self.create_contribution(transaction_namespace=NIMSP_TRANSACTION_NAMESPACE, transaction_id='Food Bar', contributor_ext_id = '4', contributor_name='Food Bar')
        self.create_contribution(transaction_namespace=NIMSP_TRANSACTION_NAMESPACE, transaction_id='FooBar', contributor_ext_id = '2', contributor_name='FooBar')
        self.create_contribution(transaction_namespace=NIMSP_TRANSACTION_NAMESPACE, transaction_id='FooBar Corp', contributor_ext_id = '1', contributor_name='FooBar Corp')
        
        # on association: gets new aliases/attributes, no duplicates formed, existing verified stay verified
        associate_transactions(foobar_id, 'contributor_entity', zip([NIMSP_TRANSACTION_NAMESPACE] * 3, ('Food Bar', 'FooBar', 'FooBar Corp')))
        
        self.assertFilter(EntityAlias, {'entity': foobar_id}, [{'alias': 'FooBar', 'verified': True},
                                                               {'alias': 'FooBar Co', 'verified': False},
                                                               {'alias': 'FooBar Corp', 'verified': False},
                                                               {'alias': 'Food Bar', 'verified': False}])
        self.assertFilter(EntityAttribute, {'entity':foobar_id}, [{'namespace': 'urn:nimsp:organization', 'value': '1', 'verified': True},
                                                                  {'namespace': EntityAttribute.ENTITY_ID_NAMESPACE, 'value': foobar_id, 'verified': True},
                                                                  {'namespace': 'urn:crp:organization', 'value': '0', 'verified':True},
                                                                  {'namespace': 'urn:nimsp:contributor', 'value': '1', 'verified': False},
                                                                  {'namespace': 'urn:nimsp:contributor', 'value': '2', 'verified': False},
                                                                  {'namespace': 'urn:nimsp:contributor', 'value': '4', 'verified': False}])
        
        # on disassociation: alias/attributes stay when verified, stay when still present, go when last one
        associate_transactions(spaz_id, 'contributor_entity', zip([NIMSP_TRANSACTION_NAMESPACE] * 3, ('Food Bar', 'FooBar', 'FooBar Corp')))
        
        self.assertFilter(EntityAlias, {'entity': foobar_id}, [{'alias': 'FooBar', 'verified': True},
                                                               {'alias': 'FooBar Co', 'verified': False},
                                                               {'alias': 'FooBar Corp', 'verified': False}])
        self.assertFilter(EntityAttribute, {'entity':foobar_id}, [{'namespace': 'urn:nimsp:organization', 'value': '1', 'verified': True},
                                                                  {'namespace': EntityAttribute.ENTITY_ID_NAMESPACE, 'value': foobar_id, 'verified': True},
                                                                  {'namespace': 'urn:crp:organization', 'value': '0', 'verified':True},
                                                                  {'namespace': 'urn:nimsp:contributor', 'value': '1', 'verified': False},
                                                                  {'namespace': 'urn:nimsp:contributor', 'value': '2', 'verified': False}])
                        
        self.assertFilter(EntityAlias, {'entity': spaz_id}, [{'alias': 'Spaz', 'verified': True},
                                                             {'alias': 'Spaz Ltd', 'verified': False},
                                                             {'alias': 'Spaz Limited', 'verified': False},
                                                             {'alias': 'FooBar', 'verified': False},
                                                             {'alias': 'FooBar Corp', 'verified': False},
                                                             {'alias': 'Food Bar', 'verified': False}])
       
        self.assertFilter(EntityAttribute, {'entity':spaz_id}, [{'namespace': EntityAttribute.ENTITY_ID_NAMESPACE, 'value': spaz_id, 'verified':True},
                                                                {'namespace': 'urn:crp:organization', 'value': '0', 'verified':True},
                                                                {'namespace': 'urn:nimsp:organization', 'value': '100', 'verified':True},
                                                                {'namespace': 'urn:nimsp:contributor', 'value': '100', 'verified': False},
                                                                {'namespace': 'urn:nimsp:contributor', 'value': '101', 'verified': False},
                                                                {'namespace': 'urn:nimsp:contributor', 'value': '102', 'verified': False},
                                                                {'namespace': 'urn:nimsp:contributor', 'value': '1', 'verified': False},
                                                                {'namespace': 'urn:nimsp:contributor', 'value': '2', 'verified': False},
                                                                {'namespace': 'urn:nimsp:contributor', 'value': '4', 'verified': False}])

        # on merge: verified from both show up, unverified from both show up, no duplicates
        merge_entities([spaz_id], Entity.objects.get(name='FooBar'))
        
        self.assertFilter(EntityAlias, {'entity': foobar_id}, [{'alias': 'Spaz', 'verified': True},
                                                               {'alias': 'Spaz Ltd', 'verified': False},
                                                               {'alias': 'Spaz Limited', 'verified': False},
                                                               {'alias': 'FooBar', 'verified': True},
                                                               {'alias': 'FooBar Co', 'verified': False},
                                                               {'alias': 'FooBar Corp', 'verified': False},
                                                               {'alias': 'Food Bar', 'verified': False}])        
        self.assertFilter(EntityAttribute, {'entity':foobar_id}, [{'namespace': EntityAttribute.ENTITY_ID_NAMESPACE, 'value': spaz_id, 'verified':True},
                                                                  {'namespace': EntityAttribute.ENTITY_ID_NAMESPACE, 'value': foobar_id, 'verified':True},
                                                                  {'namespace': 'urn:crp:organization', 'value': '0', 'verified':True},
                                                                  {'namespace': 'urn:nimsp:organization', 'value': '100', 'verified':True},
                                                                  {'namespace': 'urn:nimsp:organization', 'value': '1', 'verified':True},
                                                                  {'namespace': 'urn:nimsp:contributor', 'value': '100', 'verified': False},
                                                                  {'namespace': 'urn:nimsp:contributor', 'value': '101', 'verified': False},
                                                                  {'namespace': 'urn:nimsp:contributor', 'value': '102', 'verified': False},
                                                                  {'namespace': 'urn:nimsp:contributor', 'value': '1', 'verified': False},
                                                                  {'namespace': 'urn:nimsp:contributor', 'value': '2', 'verified': False},
                                                                  {'namespace': 'urn:nimsp:contributor', 'value': '4', 'verified': False}])
        
        self.assertFilter(EntityAlias, {'entity': spaz_id}, [])
        self.assertFilter(EntityAttribute, {'entity': spaz_id}, [])
        
            
class TestEntityAssociate(BaseMatchboxTest):
    
    def test_associate_transactions(self):
        self.create_contribution(transaction_id='a', contributor_name='Alice', amount=10)
        self.create_contribution(transaction_id='b', contributor_name='Alice', amount=20)
        self.create_contribution(transaction_id=1, amount=40)
        self.create_contribution(transaction_id=2, amount=80, contributor_name='Bob')
        self.create_contribution(transaction_id=3, amount=160, contributor_ext_id='BobID')
        self.create_contribution(transaction_id=4, contributor_employer="Carl")
        self.create_contribution(transaction_id=5, organization_name="Dave")
        self.create_contribution(transaction_id=6, parent_organization_name="Ethan")
        self.create_contribution(transaction_id=7, committee_name="Frank")
        self.create_contribution(transaction_id=8, recipient_name="Greg")
        
        self.create_contribution(transaction_id='m', transaction_namespace=NIMSP_TRANSACTION_NAMESPACE, contributor_name='Mary', contributor_ext_id='999')
        self.create_contribution(transaction_id='n', transaction_namespace=NIMSP_TRANSACTION_NAMESPACE, contributor_name='Nancy', contributor_ext_id='999')
        
        whitelist = ["0, 0, Alice", "0, 999, Mary J."]
        
        normalize_contributions()
        build_big_hitters(whitelist)
        
        e = Entity.objects.get(name="Alice")
        self.assertEqual(2, Contribution.objects.filter(contributor_entity=e.id).count())
        self.assertEqual(2, e.contribution_count)
        self.assertEqual(30, e.contribution_total_given)
        self.assertFilter(EntityAlias, {'entity': e.id}, [{'alias': 'Alice', 'verified': True}])
        self.assertEqual(3, EntityAttribute.objects.filter(entity=e.id).count())

        associate_transactions(e.id, 'contributor_entity', [(UNITTEST_TRANSACTION_NAMESPACE, '1')])
        
        e = Entity.objects.get(name="Alice")
        self.assertEqual(3, Contribution.objects.filter(contributor_entity=e.id).count())
        self.assertEqual(3, e.contribution_count)
        self.assertEqual(70, e.contribution_total_given)
        self.assertEqual(1, EntityAlias.objects.filter(entity=e.id).count())
        self.assertEqual('Alice', EntityAlias.objects.filter(entity=e.id)[0].alias)
 
        associate_transactions(e.id, 'contributor_entity', zip([UNITTEST_TRANSACTION_NAMESPACE] * 2, ('2', '3')))

        e = Entity.objects.get(name="Alice")
        self.assertEqual(5, Contribution.objects.filter(contributor_entity=e.id).count())
        self.assertEqual(5, e.contribution_count)
        self.assertEqual(310, e.contribution_total_given)
        self.assertEqual(2, EntityAlias.objects.filter(entity=e.id).count())
        self.assertEqual(1, EntityAlias.objects.filter(entity=e.id, alias='Alice').count())
        self.assertEqual(1, EntityAlias.objects.filter(entity=e.id, alias='Bob').count())
        self.assertEqual(4, EntityAttribute.objects.filter(entity=e.id).count())
        self.assertEqual(1, EntityAttribute.objects.filter(entity=e.id, namespace=EntityAttribute.ENTITY_ID_NAMESPACE, value=e.id).count())
        self.assertEqual(1, EntityAttribute.objects.filter(entity=e.id, namespace='urn:crp:organization', value='0').count())
        self.assertEqual(1, EntityAttribute.objects.filter(entity=e.id, namespace='urn:nimsp:organization', value='0').count())
        self.assertEqual(1, EntityAttribute.objects.filter(entity=e.id, namespace='urn:unittest:contributor', value='BobID').count())        
  
        associate_transactions(e.id, 'organization_entity', [(UNITTEST_TRANSACTION_NAMESPACE, '4'), (UNITTEST_TRANSACTION_NAMESPACE, '5')])
        associate_transactions(e.id, 'parent_organization_entity', [(UNITTEST_TRANSACTION_NAMESPACE, '6')])
        associate_transactions(e.id, 'committee_entity', [(UNITTEST_TRANSACTION_NAMESPACE, '7')])
        associate_transactions(e.id, 'recipient_entity', [(UNITTEST_TRANSACTION_NAMESPACE, '8')])

        e = Entity.objects.get(name="Alice")
        self.assertEqual(10, e.contribution_count)
        self.assertEqual(7, EntityAlias.objects.filter(entity=e.id).count())
        self.assertEqual(4, EntityAttribute.objects.filter(entity=e.id).count())        
        
        disassociate_transactions('contributor_entity', [(UNITTEST_TRANSACTION_NAMESPACE, 'b'), (UNITTEST_TRANSACTION_NAMESPACE, '2')])

        e = Entity.objects.get(name="Alice")
        self.assertEqual(3, Contribution.objects.filter(contributor_entity=e.id).count())
        self.assertEqual(8, e.contribution_count)
        self.assertEqual(210, e.contribution_total_given)
        self.assertEqual(6, EntityAlias.objects.filter(entity=e.id).count())
        self.assertEqual(1, EntityAlias.objects.filter(entity=e.id, alias='Alice').count())
        self.assertEqual(0, EntityAlias.objects.filter(entity=e.id, alias='Bob').count())
        self.assertEqual(4, EntityAttribute.objects.filter(entity=e.id).count())
        self.assertEqual(0, EntityAttribute.objects.filter(entity=e.id, namespace='urn:crp:contributor', value='BobID').count())

        e = Entity.objects.get(name="Mary J.")
        self.assertEqual(2, Contribution.objects.filter(contributor_entity=e.id).count())
        self.assertEqual(2, e.contribution_count)
        self.assertEqual(3, EntityAlias.objects.filter(entity=e.id).count())
        self.assertEqual(1, EntityAlias.objects.filter(entity=e.id, alias="Mary J.").count())
        self.assertEqual(1, EntityAlias.objects.filter(entity=e.id, alias="Mary").count())
        self.assertEqual(1, EntityAlias.objects.filter(entity=e.id, alias="Nancy").count())
        
        associate_transactions(e.id, 'contributor_entity', [(UNITTEST_TRANSACTION_NAMESPACE, 'a'), (UNITTEST_TRANSACTION_NAMESPACE, 'b')])
        
        e = Entity.objects.get(name="Mary J.")
        self.assertEqual(4, Contribution.objects.filter(contributor_entity=e.id).count())
        self.assertEqual(4, e.contribution_count)
        self.assertEqual(30, e.contribution_total_given)
        self.assertEqual(4, EntityAlias.objects.filter(entity=e.id).count())
        self.assertEqual(1, EntityAlias.objects.filter(entity=e.id, alias="Mary J.").count())
        self.assertEqual(1, EntityAlias.objects.filter(entity=e.id, alias="Mary").count())
        self.assertEqual(1, EntityAlias.objects.filter(entity=e.id, alias="Nancy").count())
        self.assertEqual(1, EntityAlias.objects.filter(entity=e.id, alias="Alice").count())
  
        e = Entity.objects.get(name="Alice")
        self.assertEqual(2, Contribution.objects.filter(contributor_entity=e.id).count())
        self.assertEqual(7, e.contribution_count)
        self.assertEqual(200, e.contribution_total_given)
        self.assertEqual(6, EntityAlias.objects.filter(entity=e.id).count())
        self.assertEqual(1, EntityAlias.objects.filter(entity=e.id, alias='Alice').count())
        
        
            
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
        
    
        