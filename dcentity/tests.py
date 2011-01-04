from django.test import TestCase

from dcentity.models import *
from dcentity.entity import merge_entities

class TestQueries(TestCase):

    def setUp(self):
        super(TestQueries, self).setUp()

        apple = Entity.objects.create(name="Apple")
        apple.aliases.create(alias="Apple")
        apple.aliases.create(alias="Apple Juice")
        apple.attributes.create(namespace='color', value='red')
        apple.attributes.create(namespace='color', value='yellow')
        apple.attributes.create(namespace='texture', value='crisp')
        self.apple_id = apple.id

        apricot = Entity.objects.create(name="Apricot")
        apricot.aliases.create(alias='Apricot')
        apricot.attributes.create(namespace='color', value='yellow')
        apricot.attributes.create(namespace='texture', value='soft')
        self.apricot_id = apricot.id

        applicot = Entity.objects.create(name=u"Applicot")
        applicot.aliases.create(alias='Applicot')
        self.applicot_id = applicot.id

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


