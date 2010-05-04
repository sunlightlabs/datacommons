
from piston.handler import BaseHandler
from dcapi.aggregates.lobbying.queries import get_top_registrants_for_client,\
    get_top_issues_for_client, get_top_lobbyists_for_client
from dcapi.aggregates.handlers import AggTopHandler



class OrgRegistrantsHandler(AggTopHandler):
    fields = ['registrant_name', 'registrant_entity', 'amount']

    def query(self, entity_id, cycle, limit):
        return get_top_registrants_for_client(entity_id, cycle, limit)


class OrgIssuesHandler(AggTopHandler):
    fields = ['issue', 'count']

    def query(self, entity_id, cycle, limit):
        return get_top_issues_for_client(entity_id, cycle, limit)


class OrgLobbyistsHandler(AggTopHandler):
    fields = ['lobbyist_name', 'lobbyist_entity', 'count']

    def query(self, entity_id, cycle, limit):
        return get_top_lobbyists_for_client(entity_id, cycle, limit)

