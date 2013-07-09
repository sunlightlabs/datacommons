from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from dcapi.aggregates.handlers import EntityTopListHandler, TopListHandler
from dcapi.aggregates.handlers import TopListHandler
from dcapi.aggregates.handlers import SummaryHandler, SummaryRollupHandler, \
                                      SummaryBreakoutHandler

from dcdata.lobbying.models import Bill, BillTitle, Issue

import requests

def obtain_bill_title(bill):
    try:
        bt = BillTitle.objects.get(bill_no=bill.bill_no, bill_type=bill.bill_type, congress_no=bill.congress_no)
        print bt.title
        return bt.title
    except:
        return '(Title Unknown)'

def gather_bill_metadata(bill):
    metadata = bill.__dict__.copy()
    del metadata['_state']

    metadata['bill_title'] = obtain_bill_title(bill)
    metadata['bill_issue'] = bill.issue.general_issue if bill.issue else None

    if metadata['congress_no'] >= 111:
        type_map = { 'h'     : 'hr'     ,
                     'hr'    : 'hres'   ,
                     'hj'    : 'hjres'  ,
                     'hc'    : 'hconres',
                     's'     : 's'      ,
                     'sr'    : 'sres'   ,
                     'sj'    : 'sjres'  ,
                     'sc'    : 'sconres',
                     'hamdt' : 'hamdt'  ,
                     'samdt' : 'samdt'  }

        bill_type = type_map.get(metadata['bill_type'] if metadata['bill_type'] else
                              metadata['bill_type_raw'].lower(), None)

        if bill_type:
            params = {  'bill_type' : bill_type,
                        'congress'  : bill.congress_no,
                        'number'    : bill.bill_no,
                        'apikey'    : settings.SYSTEM_API_KEY}

            params.update({ 'fields'  : ','.join([  'official_title',
                                                    'short_title',
                                                    'title',
                                                    'popular_title',
                                                    'nicknames',
                                                    'last_action',
                                                    'summary',
                                                    'summary_short',
                                                    'urls.govtrack'])})

            congress_url = 'http://congress.api.sunlightfoundation.com/bills'

            r = requests.get(congress_url, params=params)
            res = r.json
            if r.ok and res['count'] == 1:
                #tmp = metadata.pop('bill_title',None)
                cm = res['results'][0]
                metadata['display_title'] = cm.get('popular_title', None)       or \
                                            cm.get('short_title', None)         or \
                                            cm.get('official_title', None)      or \
                                            metadata.get('bill_title', None)    or \
                                            metadata['bill_name']
                nicknames = cm.get('nicknames', None) 
                metadata['display_subtitle'] = metadata['bill_name']
                metadata['display_nicknames'] = ', '.join(['"'+n+'"' for n in nicknames]) if nicknames else None
                metadata['url'] = cm['urls'].get('govtrack', None) if cm.get('urls', None) else None
                metadata['last_action'] = cm.get('last_action', None)
                metadata['display_summary'] = cm.get('summary_short', None)     or \
                                              cm.get('summary', None)           or \
                                              "Sorry, no summary is available."
            else:
                print "something went wrong"
                print r.url
                print "status was {code} {reason}".format(code=r.status_code, reason=r.reason)
                print "json was \n {j}".format(j=r.json)

    return metadata

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
        (select bill_id as category, bill_name, sum(count) as count, sum(amount) as amount
        from summary_lobbying_bills_for_biggest_org
        where cycle = %s
        group by bill_id, bill_name, congress_no
        order by sum(amount) desc
        limit 10) x;
    """

class OrgBillsBiggestOrgsByAmountHandler(SummaryBreakoutHandler):

    args = ['cycle', 'limit']

    fields = ['name', 'id', 'bill_id', 'amount']

    type_list = [str,str,int,float]

    stmt = """
       with top_bills as
        (
        select
            bill_id,
            bill_name,
            congress_no,
            cycle,
            sum(count) as count,
            sum(amount) as amount
        from summary_lobbying_bills_for_biggest_org
        where cycle = %s
        group by bill_id, bill_name, congress_no, cycle
        order by sum(amount) desc
        limit 10
        )

       select
            name,
            id,
            bill_id,
            amount
        from
        (select client_name as name, client_entity as id, s.bill_id, s.bill_name, s.congress_no, s.amount,
        rank() over(partition by s.bill_id order by rank_by_amount) as rank
        from summary_lobbying_bills_for_biggest_org s
        join top_bills t on s.bill_id = t.bill_id and s.congress_no = t.congress_no and s.cycle = t.cycle) sub
        where rank <= %s;
    """

class OrgBillsSummaryHandler(SummaryHandler):
    rollup = OrgBillsTotalsHandler()
    breakout = OrgBillsBiggestOrgsByAmountHandler()

    def key_function(self,x):
        return x['bill_id']
        # issue = x['issue']
        # if direct_or_indiv in self.rollup.category_map:
        #     return self.rollup.category_map
        # else:
        #     return self.rollup.default_key

    def read(self, request, **kwargs):
        labeled_results = super(OrgBillsSummaryHandler, self).read(request)
        for lr in labeled_results:
            try:
                bill = Bill.objects.filter(bill_id=lr['name'])[0]
            except ObjectDoesNotExist:
                import json
                print 'bill_id {bid} does not exist?!'.format(bid=lr['name'])
                print 'labeled_result:\n{d}'.format(d=json.dumps(lr,indent=2))
            bill_metadata = gather_bill_metadata(bill)
            lr['metadata'] = bill_metadata
            lr['name'] = bill.bill_name + ' (' + str(bill.congress_no) +')'

        return labeled_results
