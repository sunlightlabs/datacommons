
import sys

from saucebrush import run_recipe
from saucebrush.sources import CSVSource
from saucebrush.filters import FieldRemover, ConditionalFilter, FieldModifier, FieldRenamer, FieldCopier
from saucebrush.emitters import SqlDumpEmitter, DebugEmitter


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


def csv2sql(table_name, csv_columns, sql_fields, normalized_fields, normalizer, input_file = sys.stdin, output_file = sys.stdout):
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
        outpu_file -- the output file to write to (default sys.stdout)
    """

    run_recipe(CSVSource(input_file, csv_columns),
                                   #DebugEmitter(),
                                   FieldCountValidator(csv_columns),
                                   FieldRemover([c for c in csv_columns if c not in sql_fields.values()]),
                                   FieldRenamer(sql_fields),
                                   FieldCopier(normalized_fields),
                                   FieldModifier(normalized_fields.keys(), normalizer),
                                   #DebugEmitter(),)
                                   SqlDumpEmitter(output_file,table_name,sql_fields.keys() + normalized_fields.keys())) 

                                   




