from dcdata.utils.sql import augment, dict_union




def case_empty(preferred, fallback):
    return "case %s != '' then %s else %s end" % (preferred, preferred, fallback)
  
    
def ranked_select(selected, from_, rank, rank_order, group_by):
    aliases = ", ".join(selected.keys())    
    select_columns = ", ".join(["%s as %s" % (value, alias) for (alias, value) in selected.iteritems()])
    group_values = ", ".join([selected[alias] for alias in group_by])
    rank_values = ", ".join([selected[alias] for alias in rank])
    
    return \
        """
        select %(aliases)s
        from (select %(columns)s, 
                rank() over (partition by %(rank)s order by %(rank_order)s) as rank
            from %(from_tables)s   
            group by %(group)s) top
        where
            rank <= :agg_top_n
        """ % dict(aliases=aliases, columns=select_columns, from_tables=from_, rank=rank_values, rank_order=rank_order, group=group_values)    


def grouped_select(selected, from_, group_by):
    select_columns = ", ".join(["%s as %s" % (value, alias) for (alias, value) in selected.iteritems()])
    group_values = ", ".join([selected[alias] for alias in group_by])

    return \
        """
        select %(columns)s
        from %(from_tables)s
        group by %(group)s
        """ % dict(columns=select_columns, from_tables=from_, group=group_values)


def create_as_ranked_cycle_combination(table, selected, from_, rank, rank_order, group_by):
    with_cycle = ranked_select(augment(selected, cycle='cycle'), from_, rank + ['cycle'], rank_order, group_by + ['cycle'])
    without_cycle = ranked_select(augment(selected, cycle='-1'), from_, rank, rank_order, group_by)
    
    return \
        """
        create table %(table)s as
            %(with_cycle)s
        union
            %(without_cycle)s;
        """ % dict(table=table, with_cycle=with_cycle, without_cycle=without_cycle)


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

def build_standard_ranked_table(table, source, primary, secondary, measures):
    assert primary in ASSOCIATION_TABLES
    assert secondary in ASSOCIATION_TABLES
    
    primary_terms = {primary + '_entity': primary + ".entity_id"}
    secondary_terms = {secondary + '_entity': "coalesce(%s.entity_id, '')" % secondary,
                       secondary + '_name': secondary + '_name'}
    
    from_ = \
        """
        %s source
        inner join %s %s using (transaction_id)
        left join %s %s using (transaction_id)
        """ % (source, ASSOCIATION_TABLES[primary], primary, ASSOCIATION_TABLES[secondary], secondary)

    return build_ranked_table(table, from_, primary_terms, secondary_terms, measures)

def build_ranked_table(table, from_, primary_terms, secondary_terms, measures):
    
    selected = dict_union(primary_terms, secondary_terms, measures)

    rank = primary_terms.keys()
    rank_order = 'sum(amount) desc'
    
    group_by = dict_union(primary_terms, secondary_terms).keys()
    
    return "%s\n%s\n%s\n" % (
                             drop_table(table),
                             create_as_ranked_cycle_combination(table, selected, from_, rank, rank_order, group_by),
                             create_index(table, rank + ['cycle'])
                             )    

    
    pass

ASSOCIATION_TABLES = dict(
    contributor="contributor_associations",
    recipient='recipient_associations')



        

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

COUNT = dict(count='count(source)')
AMOUNT = dict(amount='sum(amount)')
COUNT_AND_AMOUNT = dict_union(COUNT, AMOUNT)


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
    measures=COUNT_AND_AMOUNT)

agg_cat_orders_to_cand_stmt = build_ranked_table(
    table='agg_cat_orders_to_cand',
    from_="(select * from contributions_individual union select * from contributions_organization) source inner join recipient_associations recipient using (transaction_id)",
    primary_terms={'recipient_entity': 'recipient.entity_id', 'sector': "substring(contributor_category_order for 1)"},
    secondary_terms={'category_order': 'contributor_category_order'},
    measures=COUNT_AND_AMOUNT)

agg_party_from_indiv_stmt = build_pie_table(
    table='agg_party_from_indiv',
    source='contributions_individual',
    primary='contributor',
    features=dict(recipient_party='recipient_party'),
    measures=COUNT_AND_AMOUNT)



