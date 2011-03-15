
from dcapi.aggregates.handlers import EntityTopListHandler


class OrgRegistrantsHandler(EntityTopListHandler):
    fields = ['registrant_name', 'registrant_entity', 'count', 'amount']

    stmt = """
        select registrant_name, registrant_entity, count, amount
        from agg_lobbying_registrants_for_client
        where
            client_entity = %s
            and cycle = %s
        order by amount desc, count desc
        limit %s
    """


class OrgIssuesHandler(EntityTopListHandler):
    fields = ['issue', 'count']

    stmt = """
        select issue, count
        from agg_lobbying_issues_for_client
        where
            client_entity = %s
            and cycle = %s
        order by count desc
        limit %s
    """


class OrgBillsHandler(EntityTopListHandler):
    fields = 'congress_no bill_type bill_no bill_name cycle count'.split()

    stmt = """
        select {0}
        from agg_lobbying_bills_for_client
        where
            client_entity = %s
            and cycle = %s
        order by count desc
        limit %s
    """.format(', '.join(fields))


class OrgLobbyistsHandler(EntityTopListHandler):

    fields = ['lobbyist_name', 'lobbyist_entity', 'count']

    stmt = """
        select lobbyist_name, lobbyist_entity, count
        from agg_lobbying_lobbyists_for_client
        where
            client_entity = %s
            and cycle = %s
        order by count desc
        limit %s
    """

class IndivRegistrantsHandler(EntityTopListHandler):

    fields = ['registrant_name', 'registrant_entity', 'count']

    stmt = """
        select registrant_name, registrant_entity, count
        from agg_lobbying_registrants_for_lobbyist
        where
            lobbyist_entity = %s
            and cycle = %s
        order by count desc
        limit %s
    """

class IndivIssuesHandler(EntityTopListHandler):

    fields = ['issue', 'count']

    stmt = """
        select issue, count
        from agg_lobbying_issues_for_lobbyist
        where
            lobbyist_entity = %s
            and cycle = %s
        order by count desc
        limit %s
    """

class IndivClientsHandler(EntityTopListHandler):

    fields = ['client_name', 'client_entity', 'count']

    stmt = """
        select client_name, client_entity, count
        from agg_lobbying_clients_for_lobbyist
        where
            lobbyist_entity = %s
            and cycle = %s
        order by count desc
        limit %s
    """

class RegistrantIssuesHandler(EntityTopListHandler):

    fields = ['issue', 'count']

    stmt = """
        select issue, count
        from agg_lobbying_issues_for_registrant
        where
            registrant_entity = %s
            and cycle = %s
        order by count desc
        limit %s
    """

class RegistrantBillsHandler(EntityTopListHandler):

    fields = 'congress_no bill_type bill_no bill_name cycle count'.split()

    stmt = """
        select {0}
        from agg_lobbying_bills_for_registrant
        where
            registrant_entity = %s
            and cycle = %s
        order by count desc
        limit %s
    """.format(', '.join(fields))

class RegistrantClientsHandler(EntityTopListHandler):

    fields = ['client_name', 'client_entity', 'count', 'amount']

    stmt = """
        select client_name, client_entity, count, amount
        from agg_lobbying_clients_for_registrant
        where
            registrant_entity = %s
            and cycle = %s
        order by amount desc, count desc
        limit %s
    """


class RegistrantLobbyistsHandler(EntityTopListHandler):

    fields = ['lobbyist_name', 'lobbyist_entity', 'count']

    stmt = """
        select lobbyist_name, lobbyist_entity, count
        from agg_lobbying_lobbyists_for_registrant
        where
            registrant_entity = %s
            and cycle = %s
        order by count desc
        limit %s
    """




