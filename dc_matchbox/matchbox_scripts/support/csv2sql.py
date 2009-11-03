from saucebrush import run_recipe, Recipe
from saucebrush.sources import CSVSource
from saucebrush.filters import FieldRemover, ConditionalFilter, FieldModifier, FieldRenamer, FieldCopier
from saucebrush.emitters import SqlDumpEmitter, DebugEmitter
import logging
import os
import sys


class FieldCountValidator(ConditionalFilter):
    """ A saucebrush filter to validate that the expected fields exist. """
    
    def __init__(self, expected_fields):
        super(FieldCountValidator, self).__init__()
        self.expected_fields = expected_fields

    def test_record(self, record):
        for field in self.expected_fields:
            if not (field in record and record[field] is not None):
                self.reject_record(record, "Record does not have required field '%s':" % (field,))
                return False
        return True
    
    # the base class reject_record holds the records in memory, which doesn't work well if all records are failing
    def reject_record(self, record, message):
        sys.stderr.write(message +  " " + record.__str__() + "\n")


def csv2sql(table_name, csv_columns, sql_fields, normalized_fields, normalizer, input_file=None, output_file=None, skiprows=0):
    """
    Reads in a CSV file and outputs SQL insert statements to recreate the data.
    
    Arguments:
        csv_columns -- a list of names of each CSV column
        sql_fields -- a map from sql column name to the source CSV column name. 
                    Columns can be renamed, and unmentioned CSV columns are dropped.
        normalized_fields -- a list of SQL columns that should be normalized.
        normalizer -- a normalizer function, from unicode to unicode, to be run on the normalized fields.
                    This could eventually be extended to allow different normalizers on different columns.
        input_file -- the input file to read from (default sys.stdin)
        output_file -- the output file to write to (default sys.stdout)
    """
    
    if not input_file:
        input_file = sys.stdin
    
    if not output_file:
        output_file = sys.stdout
        
    field_mapping = dict(zip(csv_columns, sql_fields))
    
    recipe = Recipe()
    #recipe.add_filter(DebugEmitter())
    recipe.add_filter(FieldCountValidator(csv_columns))
    #recipe.add_filter(FieldRemover([c for c in csv_columns if c not in sql_fields.values()]))
    recipe.add_filter(FieldRenamer(dict(((v, k) for k, v in field_mapping.iteritems())))) # flip mapping dict for rename
    if normalized_fields:
        #recipe.add_filter(FieldCopier(normalized_fields))
        recipe.add_filter(FieldModifier(normalized_fields.keys(), normalizer))
    #recipe.add_filter(DebugEmitter())
    #recipe.add_filter(SqlDumpEmitter(output_file, table_name, sql_fields.keys() + normalized_fields.keys()))
    recipe.add_filter(SqlDumpEmitter(output_file, table_name, sql_fields))
    
    recipe.run(CSVSource(input_file, fieldnames=csv_columns, skiprows=skiprows))


def main():

    from optparse import OptionParser
    
    usage = "usage: %prog [options]"
    
    parser = OptionParser(usage=usage)
    parser.add_option("-f", "--file", dest="file",
                      help="csv file to read", metavar="PATH")
    parser.add_option("-o", "--outfile", dest="outfile",
                      help="output file, or STDOUT if not specified", metavar="PATH")
    parser.add_option("-c", "--columns", dest="columns",
                      help="column names", metavar="\"COLUMN1,COLUMN2,...\"")
    parser.add_option("-t", "--table", dest="table", metavar="TABLENAME",
                      help="name of database table")
    parser.add_option("-s", "--sqlfields", dest="sqlfields", metavar="\"COLUMN1,COLUMN2,...\"",
                      help="names of sql columns, use columns if not set")
    parser.add_option("-n", "--normalize", dest="normalize", metavar="\"COLUMN1,COLUMN2,...\"",
                      help="names fields to normalize")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False,
                      help="noisy output")
    
    (options, args) = parser.parse_args()
    
    if not options.table:
        parser.error("-t table name is required")
    
    infile = open(os.path.abspath(options.file)) if options.file else sys.stdin
    outfile = open(os.path.abspath(options.outfile), 'w') if options.outfile else sys.stdout
    
    if options.columns:
        columns = options.columns.strip('"').split(',')
    else:
        columns = infile.readline().split(',')

    sqlfields = options.sqlfields.strip('"').split(',') if options.sqlfields else columns
    normalize = options.normalize.strip('"').split(',') if options.normalize else None
    
    csv2sql(options.table, columns, sqlfields, normalize, lambda s: s, infile, outfile, skiprows=0)
    

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()