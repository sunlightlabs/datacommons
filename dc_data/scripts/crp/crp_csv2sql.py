from csv2sql import csv2sql


"""
Convert the CRP individual_contributions table into SQL insert statements. 

The SQL table includes all of the original columns.
"""


table_name = 'individual_contributions'
csv_columns = ['Cycle','FECTransID','ContribID','Contrib','RecipID',\
                'Orgname','UltOrg','RealCode','Date','Amount',\
                'Street','City','State','Zip','RecipCode','Type',\
                'CmteID','OtherID','Gender','FecOccEmp','Microfilm',\
                'Occ_EF','Emp_EF','Source']
sql_fields = dict([(c,c) for c in csv_columns])
normalized_fields = {}
normalizer = None


if __name__ == '__main__':
    csv2sql(table_name, csv_columns, sql_fields, normalized_fields, normalizer)

