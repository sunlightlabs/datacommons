import os

from optparse import make_option
from django.core.management.base import CommandError, BaseCommand
from django.db import connection, transaction

from dcdata.contribution.sources.crp import CYCLES


create_tmp_crp_candidates_stmt = """
    CREATE TABLE tmp_crp_candidates (
    	Cycle char(4) NOT NULL,
    	FECCandID char(9) NOT NULL,
    	CID char(9) NULL,
    	FirstLastP varchar NULL,
    	Party char(1) NULL,
    	DistIDRunFor char(4) NULL,
    	DistIDCurr char(4) NULL,
    	CurrCand char(1) NULL,
    	CycleCand char(1) NULL,
    	CRPICO char(1) NULL,
    	RecipCode char(2) NULL,
    	NoPacs char(1) NULL
    )
"""

create_tmp_crp_committees_stmt = """
    CREATE TABLE tmp_crp_committees (
        Cycle char(4) NOT NULL,
    	CmteID char(9) NOT NULL,
    	PACShort varchar(50) NULL,
    	Affiliate varchar(50) NULL,
    	UltOrg varchar(50) NULL,
    	RecipID char(9) NULL,
    	RecipCode char(2) NULL,
    	FECCandID char(9) NULL,
    	Party char(1) NULL,
    	PrimCode char(5) NULL,
    	Source char(10) NULL,
        Sensitive char(1) NULL,
    	IsForeign char(1) NOT NULL,
    	Active int NULL
    )
"""


insert_cand_ids_stmt = """
insert into matchbox_entityattribute (entity_id, namespace, value)
    select a.entity_id, 'urn:fec:candidate', c.FECCandID
    from tmp_crp_candidates c
    inner join matchbox_entityattribute a on CID = value and namespace = 'urn:crp:recipient'
    where
        not exists 
            (select * 
            from matchbox_entityattribute x 
            where 
                x.entity_id = a.entity_id
                and x.namespace = 'urn:fec:candidate'
                and x.value = c.FECCandID);
"""


insert_cmte_ids_stmt = """
    insert into matchbox_entityattribute (entity_id, namespace, value)
    select distinct entity_id, 'urn:fec:committee', c.CmteID
    from tmp_crp_committees c
    inner join matchbox_entityalias a on a.namespace in ('', 'urn:crp:organization') and lower(a.alias) = lower(c.ultorg)
    where
        not exists
            (select *
            from matchbox_entityattribute x
            where
                x.entity_id = a.entity_id
                and x.namespace = 'urn:fec:committee'
                and x.value = c.CmteID)
"""


def upload_crp_candidates(filename):
    c = connection.cursor()
    infile = open(filename, 'r')
    c.execute("DROP TABLE IF EXISTS tmp_crp_candidates")
    c.execute(create_tmp_crp_candidates_stmt)
    c.copy_expert("COPY tmp_crp_candidates FROM STDIN CSV QUOTE '|'", infile)

def upload_crp_committees(filename):
    c = connection.cursor()
    infile = open(filename, 'r')    
    c.execute("DROP TABLE IF EXISTS tmp_crp_committees")
    c.execute(create_tmp_crp_committees_stmt)
    c.copy_expert("COPY tmp_crp_committees FROM STDIN CSV QUOTE '|'", infile)
    

def insert_cand_ids():
    c = connection.cursor()
    c.execute(insert_cand_ids_stmt)
    print "inserted %d candidate IDs" % c.rowcount

def insert_cmte_ids():
    c = connection.cursor()
    c.execute(insert_cmte_ids_stmt)
    print "inserted %d committee IDs" % c.rowcount
    
def cleanup_tmp_tables():
    c = connection.cursor()
    c.execute("DROP TABLE tmp_crp_candidates")
    c.execute("DROP TABLE tmp_crp_committees")


def clean_unicode(source, dest):
    infile = open(source, 'r')
    outfile = open(dest, 'w')
    
    for line in infile:
        fixed_line = line.decode('utf8', 'replace').encode('utf8', 'replace')
        outfile.write(fixed_line)


class CRPLoadFECIDs(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("-c", "--cycles", dest="cycles", help="cycles to load ex: 90,92,08", metavar="CYCLES"),
        make_option("-d", "--dataroot", dest="dataroot", help="path to data directory", metavar="PATH"))
    
    def handle(self, *args, **options):
        if 'dataroot' not in options:
            raise CommandError("path to dataroot is required")

        cycles = []
        if 'cycles' in options and options['cycles']:
            for cycle in options['cycles'].split(','):
                if len(cycle) == 4:
                    cycle = cycle[2:4]
                if cycle in CYCLES:
                    cycles.append(cycle)
        else:
            cycles = CYCLES

        dataroot = os.path.abspath(options['dataroot'])
        
        with transaction.commit_on_success():
            for cycle in cycles:
                clean_unicode(os.path.join(dataroot, 'cmtes%s.txt' % cycle), os.path.join(dataroot, 'cmtes%s.utf8' % cycle))
                upload_crp_committees(os.path.join(dataroot, 'cmtes%s.utf8' % cycle ))
                upload_crp_candidates(os.path.join(dataroot, 'cands%s.txt' % cycle ))
                insert_cand_ids()
                insert_cmte_ids()
                cleanup_tmp_tables()
        
Command = CRPLoadFECIDs
