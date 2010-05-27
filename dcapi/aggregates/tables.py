from dcdata.utils.sql import augment, dict_union

# An ordered dictionary for name/value pairs
class ODict(dict):
    def __init__(self, assignments):
        super(ODict,self).__init__(assignments)
        self.ordered_keys = [name for (name, _) in assignments]
    
    def keys(self):
        return self.ordered_keys
    
    def items(self):
        return [(key, self[key]) for key in self.keys()]



  
########## Code for generating generic SQL Code -- assumes nothing about our particular schemas ##########  
    
def case_empty(preferred, fallback):
    return "case when %s != '' then %s else %s end" % (preferred, preferred, fallback)
      
    
def ranked_select(selected, from_, rank, rank_order, group_by=[]):
    aliases = ", ".join(selected.keys())    
    select_columns = ", ".join(["%s as %s" % (value, alias) for (alias, value) in selected.items()])
    group_values = ", ".join([selected[alias] for alias in group_by])
    rank_values = ", ".join([selected[alias] for alias in rank])
    rank_order_values = ", ".join(["%s desc" % selected[alias] for alias in rank_order])
    
    group_clause = "group by " + group_values if group_by else ""
    
    return \
        """
        select %(aliases)s
        from (select %(columns)s, 
                rank() over (partition by %(rank)s order by %(rank_order)s) as rank
            from %(from_tables)s   
            %(group_clause)s) top
        where
            rank <= 10
        """ % dict(aliases=aliases, columns=select_columns, from_tables=from_, rank=rank_values, rank_order=rank_order_values, group_clause=group_clause)    







def grouped_select(selected, from_, group_by, where=None):
    select_columns = ", ".join(["%s as %s" % (value, alias) for (alias, value) in selected.items()])
    group_values = ", ".join([selected[alias] for alias in group_by])

    where_clause = "where %s" % where if where else ""

    return \
        """
        select %(columns)s
        from %(from_tables)s
        %(where_clause)s
        group by %(group)s
        """ % dict(columns=select_columns, from_tables=from_, where_clause=where_clause, group=group_values)


def create_as_ranked_cycle_combination(table, selected, from_, rank, rank_order, group_by=None):
    with_cycle = ranked_select(ODict(selected.items() + [('cycle', 'cycle')]), from_, rank + ['cycle'], rank_order, group_by + ['cycle'])
    without_cycle = with_cycle.replace('cycle', '-1', 1).replace(', cycle as cycle', '').replace(', cycle', '').replace('cycle as cycle, ', '').replace('cycle, ', '')
    
    return \
        """
        create table %(table)s as
            %(with_cycle)s
        union
            %(without_cycle)s;
        """ % dict(table=table, with_cycle=with_cycle, without_cycle=without_cycle)


def create_as_cycle_combination(table, cycle_select):
    without_cycle = cycle_select.replace('cycle', '-1', 1).replace(', cycle as cycle', '').replace(', cycle', '').replace('cycle as cycle, ', '').replace('cycle, ', '')

    return \
        """
        create table %(table)s as
            %(with_cycle)s
        union
            %(without_cycle)s;
        """ % dict(table=table, with_cycle=cycle_select, without_cycle=without_cycle)




def create_as_grouped_cycle_combination(table, selected, from_, group_by):
    with_cycle = grouped_select(augment(selected, cycle='cycle'), from_, group_by + ['cycle'])
    without_cycle = grouped_select(augment(selected, cycle='-1'), from_, group_by)
    
    return \
        """
        create table %(table)s as
            %(with_cycle)s
        union
            %(without_cycle)s;
        """ % dict(table=table, with_cycle=with_cycle, without_cycle=without_cycle)
                 

def drop_table(table):
    return "drop table if exists %s;\n" % table

def create_index(table, columns):
    return "create index %(table)s_idx on %(table)s (%(columns)s);" % dict(table=table, columns=", ".join(columns))



def standard_association_join(source, primary, secondary):
    return \
        """
        %s source
        inner join %s %s using (transaction_id)
        left join %s %s using (transaction_id)
        """ % (source, ASSOCIATION_TABLES[primary], primary, ASSOCIATION_TABLES[secondary], secondary)



def build_ranked_table(table, from_, primary_terms, secondary_terms, measures, rank_order):
    
    selected = ODict(primary_terms.items() + secondary_terms.items() + measures.items())

    rank = primary_terms.keys()
    
    group_by = primary_terms.keys() + secondary_terms.keys()
    
    return "%s\n%s\n%s\n" % (
                             drop_table(table),
                             create_as_ranked_cycle_combination(table, selected, from_, rank, rank_order, group_by),
                             create_index(table, rank + ['cycle'])
                             )    

    
    pass



########## Code specific to the Data Commons tables ##########


ASSOCIATION_TABLES = dict(
    contributor="contributor_associations",
    recipient='recipient_associations',
    organization='organization_associations',
    client='assoc_lobbying_client',
    registrant='assoc_lobbying_registrant')


def build_standard_ranked_table(table, source, primary, secondary, measures):
    assert primary in ASSOCIATION_TABLES
    assert secondary in ASSOCIATION_TABLES
    
    primary_terms = {primary + '_entity': primary + ".entity_id"}
    secondary_terms = {secondary + '_entity': "coalesce(%s.entity_id, '')" % secondary,
                       secondary + '_name': secondary + '_name'}
    
    from_ = standard_association_join(source, primary, secondary)

    return build_ranked_table(table, from_, primary_terms, secondary_terms, measures, measures.keys())

def build_pie_table(table, source, primary, features, measures):
    assert primary in ASSOCIATION_TABLES
    
    primary_alias = primary + '_entity'
    primary_value = primary + ".entity_id"
    
    selected = dict_union(features, measures, {primary_alias: primary_value})

    from_ = \
        """
        %s source
        inner join %s %s using (transaction_id)
        """ % (source, ASSOCIATION_TABLES[primary], primary)

    group_by = [primary_alias] + features.keys()
    
    return "%s\n%s\n%s\n" % (
                             drop_table(table),
                             create_as_grouped_cycle_combination(table, selected, from_, group_by),
                             create_index(table, [primary_alias])
                             )


        

### Top List Tables ###
'agg_sectors_to_cand'
'agg_cat_orders_to_cand'
'agg_orgs_to_cand'
'agg_cands_from_indiv'
'agg_orgs_from_inidv'
'agg_cands_from_org'

'agg_lobbying_registrants_for_client'
'agg_lobbying_issues_for_client'
'agg_lobbying_lobbyists_for_client'
'agg_lobbying_registrants_for_lobbyist'
'agg_lobbying_issues_for_lobbyist'
'agg_lobbying_clients_for_lobbyist'
'agg_lobbying_clients_for_registrant'
'agg_lobbying_issues_for_registrant'
'agg_lobbying_lobbyists_for_registrant'


### Pie Chart Tables ###
'agg_party_from_indiv'
'agg_party_from_org'
'agg_namespace_from_org'
'agg_local_to_politician'
'agg_contributor_type_to_politician'


### also: associations, views, totals, sparklines... ###

COUNT = dict(count='count(*)')
AMOUNT = dict(amount='sum(amount)')
COUNT_AND_AMOUNT = ODict(AMOUNT.items() + COUNT.items())


pacs_to_cand = grouped_select(
                            selected=dict(
                                recipient_entity='recipient.entity_id',
                                organization_name='contributor_name',
                                organization_entity="coalesce(contributor.entity_id, '')",
                                cycle='cycle', 
                                count='count(*)', 
                                amount='sum(amount)'), 
                            from_=standard_association_join('contributions_organization', 'recipient', 'contributor'),
                            group_by=['recipient_entity', 'organization_name', 'organization_entity', 'cycle'])

employees_to_cand = grouped_select(
                            selected=dict(
                                recipient_entity='recipient.entity_id',
                                organization_name=case_empty('parent_organization_name', 'organization_name'),
                                organization_entity="coalesce(organization.entity_id, '')",
                                cycle='cycle', 
                                count='count(*)', 
                                amount='sum(amount)'), 
                            from_=standard_association_join('contributions_individual', 'recipient', 'organization'),
                            group_by=['recipient_entity', 'organization_name', 'organization_entity', 'cycle'])


agg_orgs_to_cand_base = ranked_select(
    selected=ODict([
        ('recipient_entity', 'recipient_entity'),
        ('cycle', 'cycle'),
        ('organization_name', 'organization_name'),
        ('organization_entity', 'organization_entity'),
        ('total_count', "coalesce(top_pacs.count, 0) + coalesce(top_indivs.count, 0)"),
        ('pacs_count', "coalesce(top_pacs.count, 0)"),
        ('indivs_count', "coalesce(top_indivs.count, 0)"),
        ('total_amount', "coalesce(top_pacs.amount, 0) + coalesce(top_indivs.amount, 0)"),
        ('pacs_amount', "coalesce(top_pacs.amount, 0)"),
        ('indivs_amount', "coalesce(top_indivs.amount, 0)")]),
    from_="""    (%s) top_pacs 
            full outer join
                (%s) top_indivs
            using (recipient_entity, organization_name, organization_entity, cycle)
        """ % (pacs_to_cand, employees_to_cand),
    rank=['recipient_entity', 'cycle'],
    rank_order=['total_amount'])

agg_orgs_to_cand_stmt = create_as_cycle_combination('agg_orgs_to_cand', agg_orgs_to_cand_base)

                               


agg_cands_from_indiv_stmt = build_standard_ranked_table(
    table='agg_cands_from_indiv',
    source='contributions_individual',
    primary='contributor',
    secondary='recipient',
    measures=COUNT_AND_AMOUNT)

agg_sectors_to_cand_stmt = build_ranked_table(
    table='agg_sectors_to_cand',
    from_='(select * from contributions_individual union select * from contributions_organization) source inner join recipient_associations recipient using (transaction_id)',
    primary_terms={'recipient_entity': 'recipient.entity_id'},
    secondary_terms={'sector': "substring(contributor_category_order for 1)"},
    measures=COUNT_AND_AMOUNT,
    rank_order=['amount'])

agg_cat_orders_to_cand_stmt = build_ranked_table(
    table='agg_cat_orders_to_cand',
    from_="(select * from contributions_individual union select * from contributions_organization) source inner join recipient_associations recipient using (transaction_id)",
    primary_terms=ODict([('recipient_entity', 'recipient.entity_id'), ('sector', "substring(contributor_category_order for 1)")]),
    secondary_terms={'category_order': 'contributor_category_order'},
    measures=COUNT_AND_AMOUNT,
    rank_order=['amount'])

agg_lobbying_registrants_for_client_stmt = build_standard_ranked_table(
    table='agg_lobbying_registrants_for_client', 
    source='lobbying_report',
    primary='client',
    secondary='registrant', 
    measures=COUNT_AND_AMOUNT)

agg_lobbying_issues_for_lobbyist_stmt = build_ranked_table(
    table='agg_lobbying_issues_for_lobbyist',
    from_= \
        """
        lobbying_report r
            inner join lobbying_issue i using (transaction_id)
            inner join lobbying_lobbyist l using (transaction_id)
            inner join assoc_lobbying_lobbyist la on la.id = l.id
        """,
    primary_terms={'lobbyist_entity': 'la.entity_id'}, 
    secondary_terms={'issue': 'i.general_issue'}, 
    measures=COUNT,
    rank_order=['count'])

agg_party_from_indiv_stmt = build_pie_table(
    table='agg_party_from_indiv',
    source='contributions_individual',
    primary='contributor',
    features=dict(recipient_party='recipient_party'),
    measures=COUNT_AND_AMOUNT)



