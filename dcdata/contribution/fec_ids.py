from django.db import connection

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
