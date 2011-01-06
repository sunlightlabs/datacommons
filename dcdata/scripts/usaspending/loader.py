from faads import FAADS_FIELDS
from fpds import FPDS_FIELDS

class Loader():
    def make_faads_sql(self):
        grants_file = '/home/kwebb/GIANT/usapsending/20101101_csv/datafeeds/out/grants.out'
        #table = 'faads'
        table = 'grants_grant'
        fields = [ x[0] for x in FAADS_FIELDS ]
        return self.sql_template_postgres(grants_file, table, fields)

    def make_fpds_sql(self):
        file = '/home/kwebb/GIANT/usapsending/20101101_csv/datafeeds/out/contracts.out'
        #table = 'fpds'
        table = 'contracts_contract'
        fields = [ x[0] for x in FPDS_FIELDS ]
        return self.sql_template_postgres(file, table, fields)

    def sql_template_postgres(self, file, table, fields):
        return """
            COPY {1} 
            ({2})
            FROM '{0}'
            CSV QUOTE '"'
        """.format(file, table, ', '.join(fields))

    def sql_template_mysql(self, file, table, fields):
        return """
            LOAD DATA INFILE '{0}'
            INTO TABLE {1} 
            FIELDS TERMINATED BY ',' ENCLOSED BY '\"' 
            ({2})
        """.format(file, table, ', '.join(fields))
