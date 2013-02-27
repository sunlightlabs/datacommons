from django.test import TestCase
#from django.test.client import Client
from dcentity.models import Entity
from fuzzywuzzy import fuzz
import json

class EntityReconciliationHandlerTest(TestCase):
    def test_service_metadata(self):
        self.maxDiff = None
        response = self.client.get('/api/1.0/refine/reconcile', {'callback': 'jsonp123'})

        self.assertEqual(200, response.status_code)
        self.assertEqual(100,
            fuzz.token_sort_ratio(
                'jsonp123({"name": "Influence Explorer Reconciliation3", "identifierSpace": "http://staging.influenceexplorer.com/ns/entities", "schemaspace": "http://staging.influenceexplorer.com/ns/entity.object.id", "view": { "url": "http://staging.influenceexplorer.com/entity/{{id}}" }, "preview": { "url": "http://staging.influenceexplorer.com/entity/{{id}}", "width": 430, "height": 300 }, "defaultTypes": []})',
                response.content
            )
        )

    def test_reconcile_multiple_query_format(self):
        Entity(name='Honeywell International', type='organization').save()
        Entity(name='Honeywell Foundation', type='organization').save()
        Entity(name='Honeywell Technology Solutions', type='organization').save()

        Entity(name='Podesta, Tony', type='individual').save()
        Entity(name='The Podesta Group', type='organization').save()
        Entity(name='Podesta, Thomas', type='organization').save()

        # entity PKs by name
        pks = { x.name: x.pk.get_hex() for x in Entity.objects.all() }

        response = self.client.post('/api/1.0/refine/reconcile',
            '{"queries": {"q0": {"query":"Honeywell", "properties": [{"pid": "contributionType", "v": "business"}]}, "q1": {"query": "Podesta, Anthony", "properties": [{"pid": "contributionType", "v": "individual"}]}}}')

        self.assertEqual(200, response.status_code)
        print response
        print response.content
        self.assertEqual(
            {"q1": {"result": [{"score": 1.6, "type": ["individual"], "id": pks['Podesta, Tony'], "match": False, "name": "Podesta, Tony"}]}, "q0": {"result": [{"score": 3, "type": ["organization"], "id": pks['Honeywell International'], "match": False, "name": "Honeywell International"}, {"score": 2, "type": ["organization"], "id": pks['Honeywell Foundation'], "match": False, "name": "Honeywell Foundation"}, {"score": 2, "type": ["organization"], "id": pks['Honeywell Technology Solutions'], "match": False, "name": "Honeywell Technology Solutions"}]}},
            json.loads(response.content)
        )

    def test_reconcile_single_query_format(self):
        Entity(name='Honeywell International', type='organization').save()
        Entity(name='Honeywell Foundation', type='organization').save()
        Entity(name='Honeywell Technology Solutions', type='organization').save()

        # entity PKs by name
        pks = { x.name: x.pk.get_hex() for x in Entity.objects.all() }

        response = self.client.post('/api/1.0/refine/reconcile',
            {"query": '{"query":"Honeywell", "properties": [{"pid": "contributionType", "v": "business"}]}'}
        )

        #print json.dumps(json.loads(response.content), sort_keys=True, indent=4)
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            {"result": [{"score": 3, "type": ["organization"], "id": pks['Honeywell International'], "match": False, "name": "Honeywell International"}, {"score": 2, "type": ["organization"], "id": pks['Honeywell Foundation'], "match": False, "name": "Honeywell Foundation"}, {"score": 2, "type": ["organization"], "id": pks['Honeywell Technology Solutions'], "match": False, "name": "Honeywell Technology Solutions"}]},
            json.loads(response.content)
        )

    def test_reconcile_real_multi_query(self):
        Entity(name='Honeywell International', type='organization').save()
        Entity(name='Honeywell Foundation', type='organization').save()
        Entity(name='Honeywell Technology Solutions', type='organization').save()

        Entity(name='Podesta, Tony', type='individual').save()
        Entity(name='The Podesta Group', type='organization').save()
        Entity(name='Podesta, Thomas', type='organization').save()

        # entity PKs by name
        pks = { x.name: x.pk.get_hex() for x in Entity.objects.all() }

        response = self.client.post('/api/1.0/refine/reconcile',
            {'queries': '{"q0": {"query":"Honeywell", "properties": [{"pid": "contributionType", "v": "business"}]}, "q1": {"query": "Podesta, Anthony", "properties": [{"pid": "contributionType", "v": "individual"}]}}'}
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            {"q1": {"result": [{"score": 1.6, "type": ["individual"], "id": pks['Podesta, Tony'], "match": False, "name": "Podesta, Tony"}]}, "q0": {"result": [{"score": 3, "type": ["organization"], "id": pks['Honeywell International'], "match": False, "name": "Honeywell International"}, {"score": 2, "type": ["organization"], "id": pks['Honeywell Foundation'], "match": False, "name": "Honeywell Foundation"}, {"score": 2, "type": ["organization"], "id": pks['Honeywell Technology Solutions'], "match": False, "name": "Honeywell Technology Solutions"}]}},
            json.loads(response.content)
        )

    def test_reconcile_real_multi_query_with_types(self):
        Entity(name='Honeywell International', type='organization').save()
        Entity(name='Honeywell Foundation', type='organization').save()
        Entity(name='Honeywell Technology Solutions', type='organization').save()

        Entity(name='Podesta, Tony', type='individual').save()
        Entity(name='The Podesta Group', type='organization').save()
        Entity(name='Podesta, Thomas', type='organization').save()

        # entity PKs by name
        pks = { x.name: x.pk.get_hex() for x in Entity.objects.all() }

        response = self.client.post('/api/1.0/refine/reconcile',
            {'queries': '{"q0": {"query":"Honeywell", "type":"organization"}, "q1": {"query": "Podesta, Anthony", "type": "individual"}}'}
        )

        print response
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            {"q1": {"result": [{"score": 1.6, "type": ["individual"], "id": pks['Podesta, Tony'], "match": False, "name": "Podesta, Tony"}]}, "q0": {"result": [{"score": 3, "type": ["organization"], "id": pks['Honeywell International'], "match": False, "name": "Honeywell International"}, {"score": 2, "type": ["organization"], "id": pks['Honeywell Foundation'], "match": False, "name": "Honeywell Foundation"}, {"score": 2, "type": ["organization"], "id": pks['Honeywell Technology Solutions'], "match": False, "name": "Honeywell Technology Solutions"}]}},
            json.loads(response.content)
        )

