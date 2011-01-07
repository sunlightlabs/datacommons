from faads import FAADS_FIELDS
from fpds import FPDS_FIELDS
from django.db import connections

class Loader():
    def make_faads_sql(self, infile):
        grants_file = infile
        table = 'grants_grant'
        fields = [ x[0] for x in FAADS_FIELDS ]
        return self.sql_template_postgres(grants_file, table, fields)

    def make_fpds_sql(self, infile):
        file = infile
        table = 'contracts_contract'
        fields = [ x[0] for x in FPDS_FIELDS ]
        return self.sql_template_postgres(file, table, fields)

    def insert_faads(self, infile):
        table = 'grants_grant_new'
        fields = [ x[0] for x in FAADS_FIELDS ]

        cursor = connections['default'].cursor()
        cursor.copy_from(open(infile, 'r'), table, sep=',', columns = fields)

    def insert_fpds(self, infile):
        table = 'contracts_contract_new'
        fields = [ x[0] for x in FPDS_FIELDS ]

        cursor = connections['default'].cursor()
        cursor.copy_from(open(infile, 'r'), table, sep=',', columns = fields)

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
