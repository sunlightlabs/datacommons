from dcapi.aggregates.handlers import EntityTopListHandler, TopListHandler
from dcapi.aggregates.handlers import TopListHandler
from dcapi.aggregates.handlers import SummaryHandler, SummaryRollupHandler, \
                                      SummaryBreakoutHandler

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
    fields = 'congress_no bill_type bill_no bill_name title cycle count'.split()

    stmt = """
        select {0}
        from agg_lobbying_bills_for_client
        inner join lobbying_billtitle using (bill_type, congress_no, bill_no)
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

    fields = 'congress_no bill_type bill_no bill_name title cycle count'.split()

    stmt = """
        select {0}
        from agg_lobbying_bills_for_registrant
        inner join lobbying_billtitle using (bill_type, congress_no, bill_no)
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


class TopOrgsLobbyingHandler(TopListHandler):
    args = ['entity_type', 'cycle', 'limit']

    fields = 'name entity_id amount cycle'.split()

    stmt = """
        select name, entity_id, non_firm_spending, cycle
        from agg_lobbying_by_cycle_rolled_up
        inner join matchbox_entity on matchbox_entity.id = entity_id
        where
            non_firm_spending > 0
            and case
                when %s = 'industries'
                then type = 'industry' and entity_id in (
                    select entity_id from matchbox_entityattribute where namespace = 'urn:crp:industry'
                )
                else type = 'organization' end
            and cycle = %s
        order by non_firm_spending desc
        limit %s
    """


class TopFirmsByIncomeHandler(TopListHandler):
    args = ['cycle', 'limit']

    fields = 'name entity_id amount cycle'.split()

    stmt = """
        select name, entity_id, firm_income, cycle
        from agg_lobbying_by_cycle_rolled_up
        inner join matchbox_entity on matchbox_entity.id = entity_id
        where cycle = %s and firm_income > 0
        order by firm_income desc
        limit %s
    """


class TopIndustriesLobbyingHandler(TopListHandler):
    args = ['cycle', 'limit']

    fields = 'name entity_id amount cycle'.split()

    stmt = """
        select name, entity_id, non_firm_spending, cycle
        from agg_lobbying_by_cycle_rolled_up
        inner join matchbox_entity on matchbox_entity.id = entity_id
        where
            non_firm_spending > 0
            and type = 'industry'
            and cycle = %s
        order by non_firm_spending desc
        limit %s
    """

class OrgIssuesTotalsHandler(SummaryRollupHandler):

    stmt = """
        select issue as category, sum(count) as count, sum(amount) as amount
        from summary_lobbying_issues_for_biggest_org
        where cycle = %s
        group by issue
        order by sum(amount) desc
        limit 10;
    """

class OrgIssuesBiggestOrgsByAmountHandler(SummaryBreakoutHandler):

    args = ['cycle', 'limit']

    fields = ['name', 'id', 'issue', 'amount']

    stmt = """
       with top_issues as
        (select issue as category, cycle, sum(count) as count, sum(amount) as amount
        from summary_lobbying_issues_for_biggest_org
        where cycle = %s
        group by issue, cycle
        order by sum(amount) desc
        limit 10)

       select name, id, issue, amount
        from
        (select client_name as name, client_entity as id, issue, s.amount,
        rank() over(partition by issue order by rank_by_amount) as rank
        from summary_lobbying_issues_for_biggest_org s
        join top_issues t on s.issue =  t.category and s.cycle = t.cycle) sub
        where rank <= %s;
    """

class OrgIssuesSummaryHandler(SummaryHandler):
    rollup = OrgIssuesTotalsHandler()
    breakout = OrgIssuesBiggestOrgsByAmountHandler()
    def key_function(self,x):
        return x['issue']
        # issue = x['issue']
        # if direct_or_indiv in self.rollup.category_map:
        #     return self.rollup.category_map
        # else:
        #     return self.rollup.default_key


class OrgBillsTotalsHandler(SummaryRollupHandler):

    default_key = None

    stmt = """
        select category, count, amount
        from
        (select bill_id, bill_name as category, cycle, sum(count) as count, sum(amount) as amount
        from summary_lobbying_bills_for_biggest_org
        where cycle = %s
        group by bill_id, bill_name, cycle
        order by sum(amount) desc
        limit 10) x;
    """

class OrgBillsBiggestOrgsByAmountHandler(SummaryBreakoutHandler):

    args = ['cycle', 'limit']

    fields = ['name', 'id', 'bill_name', 'amount']

    stmt = """
       with top_bills as
        (
        select bill_id, bill_name as category, cycle, sum(count) as count, sum(amount) as amount
        from summary_lobbying_bills_for_biggest_org
        where cycle = %s
        group by bill_id, bill_name, cycle
        order by sum(amount) desc
        limit 10
        )

       select name, id, bill_name, amount
        from
        (select client_name as name, client_entity as id, s.bill_id, s.bill_name, s.amount,
        rank() over(partition by s.bill_id order by rank_by_amount) as rank
        from summary_lobbying_bills_for_biggest_org s
        join top_bills t on s.bill_id = t.bill_id and s.cycle = t.cycle) sub
        where rank <= %s;
    """

class OrgBillsSummaryHandler(SummaryHandler):
    rollup = OrgBillsTotalsHandler()
    breakout = OrgBillsBiggestOrgsByAmountHandler()
    def key_function(self,x):
        return x['bill_name']
        # issue = x['issue']
        # if direct_or_indiv in self.rollup.category_map:
        #     return self.rollup.category_map
        # else:
        #     return self.rollup.default_key
