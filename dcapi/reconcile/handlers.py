from piston.handler import BaseHandler
from piston.utils import rc
from dcentity.matching.reconciler import ReconcilerService
import json
import re


class EntityReconciliationHandler(BaseHandler):

    service_metadata = {
                        "name": "Influence Explorer Reconciliation3",
                        "identifierSpace": "http://influenceexplorer.com/ns/entities",  # these are bogus values
                        "schemaspace": "http://influenceexplorer.com/ns/entity.object.id",  # to satisfy Refine
                        "view": {
                            "url": "http://influenceexplorer.com/entity/{{id}}"
                            },
                        "preview": {
                            "url": "http://influenceexplorer.com/entity/{{id}}",
                            "width": 430,
                            "height": 300
                            },
                        "defaultTypes": []
                    }

    def read(self, request, **kwargs):
        if request.REQUEST.get('callback'):
            return self.service_metadata
        else:
            return []

    def create(self, request, **kwargs):
        result = {}
        query = request.REQUEST.get('query')
        queries = request.REQUEST.get('queries')

        if query:
            q = json.loads(query)
            result['result'] = self.do_query(q)

        elif queries:
            q = json.loads(queries)
            if q is not None:

                for key, query in q.iteritems():
                    result[key] = {}
                    result[key]['result'] = self.do_query(query)
            else:
                print "We couldn't decode our queries JSON! D:"

        return result

    def do_query(self, query):
        # formatting according to the spec here:
        # http://code.google.com/p/google-refine/wiki/ReconciliationServiceApi
        properties = self.normalize_properties(query)
        type_ = query.get('type', self.determine_type_from_properties(properties, 'contributionType'))
        matches = ReconcilerService(query['query'], type_, properties=properties).start()

        return matches

    def normalize_properties(self, query):
        return { x['pid']: x['v'] for x in query.get('properties') }

    def determine_type_from_properties(self, properties, type_hint_column):
        type_hint = None
        type_ = None

        if properties:
            type_hint = properties.get(type_hint_column)

            if type_hint:
                if re.match(r'individual', type_hint.lower()):
                    type_ = 'individual'
                elif re.match(r'politician', type_hint.lower()):
                    type_ = 'politician'
                else:
                    type_ = 'organization'

        return type_
