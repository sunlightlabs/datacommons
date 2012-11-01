from piston.handler import BaseHandler
from dcentity.matching.reconciler import ReconcilerService
import json
import re


class EntityReconciliationHandler(BaseHandler):

    service_metadata = {
                        "name": "Influence Explorer Reconciliation3",
                        "identifierSpace": "http://staging.influenceexplorer.com/ns/entities",  # these are bogus values
                        "schemaspace": "http://staging.influenceexplorer.com/ns/entity.object.id",  # to satisfy Refine
                        "view": {
                            "url": "http://staging.influenceexplorer.com/entity/{{id}}"
                            },
                        "preview": {
                            "url": "http://staging.influenceexplorer.com/entity/{{id}}",
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
            for key, query in q.items():
                result[key] = {}
                result[key]['result'] = self.do_query(query)
        else:
            import pdb; pdb.set_trace()
            q = json.loads(request.POST)
            for key, query in q.items():
                if not re.match(r'q\d', key):
                    continue

                result[key] = {}
                result[key]['result'] = self.do_query(query)

        return result

    def do_query(self, query):
        # formatting according to the spec here:
        # http://code.google.com/p/google-refine/wiki/ReconciliationServiceApi
        type_ = query.get('type', self.determine_type_from_properties(query.get('properties'), 'contributionType'))
        matches = ReconcilerService(query['query'], type_).start()

        return matches

    def determine_type_from_properties(self, properties, type_hint_column):
        type_hint = None
        type_ = None

        for p in properties:
            if p.get('pid') == type_hint_column:
                type_hint = p.get('v')

        if type_hint:
            if re.match(r'individual', type_hint.lower()):
                type_ = 'individual'
            elif re.match(r'politician', type_hint.lower()):
                type_ = 'politician'
            else:
                type_ = 'organization'

        return type_
