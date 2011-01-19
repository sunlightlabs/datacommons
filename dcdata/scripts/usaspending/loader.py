from django.db import connections
from faads import FAADS_FIELDS, CALCULATED_FAADS_FIELDS
from fpds import FPDS_FIELDS, CALCULATED_FPDS_FIELDS
import os.path

class Loader():
    def faads_fields(self):
        return [ x[0] for x in FAADS_FIELDS ] + [ x[0] for x in CALCULATED_FAADS_FIELDS ]

    def fpds_fields(self):
        return [ x[0] for x in FPDS_FIELDS ] + [ x[0] for x in CALCULATED_FPDS_FIELDS ]

    def make_faads_sql(self, infile):
        table = 'grants_grant'
        return self.sql_template_postgres(infile, table, self.faads_fields())

    def make_fpds_sql(self, infile):
        table = 'contracts_contract'
        return self.sql_template_postgres(infile, table, self.fpds_fields())

    def insert_faads(self, infile):
        table = 'grants_grant'

        cursor = connections['default'].cursor()
        
        #cursor.execute(self.sql_template_postgres(infile, table, self.faads_fields()))
        cursor.copy_from(open(infile, 'r'), table, sep='|', null='NULL', columns=self.faads_fields())
        

    def insert_fpds(self, infile):
        table = 'contracts_contract'

        cursor = connections['default'].cursor()
        
        # neither verion seems to handle quoted values correctly.
        # in particular, a pipe in a string value is treated as a delimiter, even though the value is quoted.
        # works fine using the \copy command in psql, indicating it's probably a psycopg2 bug.
        #cursor.copy_expert(self.sql_template_postgres(infile, table, self.fpds_fields()))
        cursor.copy_from(open(infile, 'r'), table, sep='|', null='NULL', columns=self.fpds_fields())


    def sql_template_postgres(self, file, table, fields):
        return """
            COPY {1} \
            ({2}) \
            FROM '{0}' \
            DELIMITER '|' \
            CSV QUOTE '"' \
            NULL 'NULL' \
        """.format(os.path.relpath(file), table, ', '.join(fields)) # relpath is for the sake of tests passing in different environments

    def sql_template_mysql(self, file, table, fields):
        return """
            LOAD DATA INFILE '{0}'
            INTO TABLE {1} 
            FIELDS TERMINATED BY ',' ENCLOSED BY '\"' 
            ({2})
        """.format(os.path.relpath(file), table, ', '.join(fields)) # relpath is for the sake of tests passing in different environments

