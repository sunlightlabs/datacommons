create table contributions_nimsp_90 (
    check ( transaction_namespace = 'urn:nimsp:transaction' and cycle = 1990 )
) inherits (contribution_contribution);
create table contributions_nimsp_92 (
    check ( transaction_namespace = 'urn:nimsp:transaction' and cycle = 1992 )
) inherits (contribution_contribution);
create table contributions_nimsp_94 (
    check ( transaction_namespace = 'urn:nimsp:transaction' and cycle = 1994 )
) inherits (contribution_contribution);
create table contributions_nimsp_96 (
    check ( transaction_namespace = 'urn:nimsp:transaction' and cycle = 1996 )
) inherits (contribution_contribution);
create table contributions_nimsp_98 (
    check ( transaction_namespace = 'urn:nimsp:transaction' and cycle = 1998 )
) inherits (contribution_contribution);
create table contributions_nimsp_00 (
    check ( transaction_namespace = 'urn:nimsp:transaction' and cycle = 2000 )
) inherits (contribution_contribution);
create table contributions_nimsp_02 (
    check ( transaction_namespace = 'urn:nimsp:transaction' and cycle = 2002 )
) inherits (contribution_contribution);
create table contributions_nimsp_04 (
    check ( transaction_namespace = 'urn:nimsp:transaction' and cycle = 2004 )
) inherits (contribution_contribution);
create table contributions_nimsp_06 (
    check ( transaction_namespace = 'urn:nimsp:transaction' and cycle = 2006 )
) inherits (contribution_contribution);
create table contributions_nimsp_08 (
    check ( transaction_namespace = 'urn:nimsp:transaction' and cycle = 2008 )
) inherits (contribution_contribution);
create table contributions_nimsp_10 (
    check ( transaction_namespace = 'urn:nimsp:transaction' and cycle = 2010)
) inherits (contribution_contribution);
create table contributions_nimsp_12 (
    check ( transaction_namespace = 'urn:nimsp:transaction' and cycle = 2012)
) inherits (contribution_contribution);

create table contributions_crp_90 (
    check ( transaction_namespace = 'urn:crp:transaction' and cycle = 1990 )
) inherits (contribution_contribution);
create table contributions_crp_92 (
    check ( transaction_namespace = 'urn:crp:transaction' and cycle = 1992 )
) inherits (contribution_contribution);
create table contributions_crp_94 (
    check ( transaction_namespace = 'urn:crp:transaction' and cycle = 1994 )
) inherits (contribution_contribution);
create table contributions_crp_96 (
    check ( transaction_namespace = 'urn:crp:transaction' and cycle = 1996 )
) inherits (contribution_contribution);
create table contributions_crp_98 (
    check ( transaction_namespace = 'urn:crp:transaction' and cycle = 1998 )
) inherits (contribution_contribution);
create table contributions_crp_00 (
    check ( transaction_namespace = 'urn:crp:transaction' and cycle = 2000 )
) inherits (contribution_contribution);
create table contributions_crp_02 (
    check ( transaction_namespace = 'urn:crp:transaction' and cycle = 2002 )
) inherits (contribution_contribution);
create table contributions_crp_04 (
    check ( transaction_namespace = 'urn:crp:transaction' and cycle = 2004 )
) inherits (contribution_contribution);
create table contributions_crp_06 (
    check ( transaction_namespace = 'urn:crp:transaction' and cycle = 2006 )
) inherits (contribution_contribution);
create table contributions_crp_08 (
    check ( transaction_namespace = 'urn:crp:transaction' and cycle = 2008 )
) inherits (contribution_contribution);
create table contributions_crp_10 (
    check ( transaction_namespace = 'urn:crp:transaction' and cycle = 2010 )
) inherits (contribution_contribution);
create table contributions_crp_12 (
    check ( transaction_namespace = 'urn:crp:transaction' and cycle = 2012 )
) inherits (contribution_contribution);

create index contributions_nimsp_90__transaction_namepsace on contributions_nimsp_90 (transaction_namespace);
create index contributions_nimsp_90__transaction_namepsace on contributions_nimsp_90 (cycle);
create index contributions_nimsp_92__transaction_namepsace on contributions_nimsp_92 (transaction_namespace);
create index contributions_nimsp_92__transaction_namepsace on contributions_nimsp_92 (cycle);
create index contributions_nimsp_94__transaction_namepsace on contributions_nimsp_94 (transaction_namespace);
create index contributions_nimsp_94__transaction_namepsace on contributions_nimsp_94 (cycle);
create index contributions_nimsp_96__transaction_namepsace on contributions_nimsp_96 (transaction_namespace);
create index contributions_nimsp_96__transaction_namepsace on contributions_nimsp_96 (cycle);
create index contributions_nimsp_98__transaction_namepsace on contributions_nimsp_98 (transaction_namespace);
create index contributions_nimsp_98__transaction_namepsace on contributions_nimsp_98 (cycle);
create index contributions_nimsp_00__transaction_namepsace on contributions_nimsp_00 (transaction_namespace);
create index contributions_nimsp_00__transaction_namepsace on contributions_nimsp_00 (cycle);
create index contributions_nimsp_02__transaction_namepsace on contributions_nimsp_02 (transaction_namespace);
create index contributions_nimsp_02__transaction_namepsace on contributions_nimsp_02 (cycle);
create index contributions_nimsp_04__transaction_namepsace on contributions_nimsp_04 (transaction_namespace);
create index contributions_nimsp_04__transaction_namepsace on contributions_nimsp_04 (cycle);
create index contributions_nimsp_06__transaction_namepsace on contributions_nimsp_06 (transaction_namespace);
create index contributions_nimsp_06__transaction_namepsace on contributions_nimsp_06 (cycle);
create index contributions_nimsp_08__transaction_namepsace on contributions_nimsp_08 (transaction_namespace);
create index contributions_nimsp_08__transaction_namepsace on contributions_nimsp_08 (cycle);
create index contributions_nimsp_10__transaction_namepsace on contributions_nimsp_10 (transaction_namespace);
create index contributions_nimsp_10__transaction_namepsace on contributions_nimsp_10 (cycle);
create index contributions_nimsp_12__transaction_namepsace on contributions_nimsp_12 (transaction_namespace);
create index contributions_nimsp_12__transaction_namepsace on contributions_nimsp_12 (cycle);
