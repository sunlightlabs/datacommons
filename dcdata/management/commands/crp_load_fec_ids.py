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
    	FirstLastP varchar(40) NULL,
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


insert_fec_ids_stmt = """
insert into matchbox_entityattribute (entity_id, namespace, value)
    select a.entity_id, params.namespace, c.FECCandID
    from tmp_crp_candidates c
    inner join matchbox_entityattribute a on CID = value and namespace = 'urn:crp:recipient'
    cross join (values ('urn:fec_current_candidate:' || %s)) as params (namespace)
    where
        currcand = 'Y'
        and not exists 
            (select * 
            from matchbox_entityattribute x 
            where 
                x.entity_id = a.entity_id
                and x.namespace = params.namespace
                and x.value = c.FECCandID);
"""


def upload_crp_candidates(filename):
    c = connection.cursor()
    infile = open(filename, 'r')
    c.execute("DROP TABLE IF EXISTS tmp_crp_candidates")
    c.execute(create_tmp_crp_candidates_stmt)
    c.copy_expert("COPY tmp_crp_candidates FROM STDIN CSV QUOTE '|'", infile)


def insert_new_ids(cycle):
    c = connection.cursor()
    c.execute(insert_fec_ids_stmt, [cycle])
    print "inserted %d IDs" % c.rowcount
    
def cleanup_tmp_table():
    c = connection.cursor()
    c.execute("DROP TABLE tmp_crp_candidates")


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
                upload_crp_candidates(os.path.join(dataroot, 'cands%s.txt' % cycle ))
                insert_new_ids('19%s' % cycle if cycle > '80' else '20%s' % cycle)
                cleanup_tmp_table()
        
Command = CRPLoadFECIDs