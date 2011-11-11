from dcdata.management.base.importer import BaseImporter
from django.db.models.fields import CharField
import csv
import os.path
import re


class BaseUSASpendingConverter(BaseImporter):
    """
        This performs the conversion from raw USASpending files to a format
        acceptable to COPY into PostgreSQL.

        Note: to use the specified data dirs (see below), the directory with the
        most current set of files should be symlinked to "latest".
    """

    IN_DIR =       '/home/usaspending/usaspending/latest/datafeeds'
    DONE_DIR =     '/home/usaspending/usaspending/latest/datafeeds/DONE'
    REJECTED_DIR = '/home/usaspending/usaspending/latest/datafeeds/REJECTED'
    OUT_DIR =      '/home/usaspending/usaspending/latest/datafeeds/OUT'
    FILE_PATTERN = '*_All_*.csv' # bash-style, ala '*.sql'

    email_subject = 'Unhappy USASpending App'

    def __init__(self):
        super(BaseUSASpendingConverter, self).__init__()
        if not self.FILE_PATTERN:
            raise NotImplementedError("Child classes must specify a FILE_PATTERN")


    def do_for_file(self, file_path):
        # Since all the files for both contracts and grants importers start out
        # in the same directory, we make the file pattern permissive and do an extra
        # check in each separate importer

        if not self.file_is_right_type(file_path):
            return

        self.log.info("Starting...")

        outfile_name = '{0}_{1}.csv'.format(self.outfile_basename, self.get_year_from_file_path(file_path))

        self.parse_file(file_path, outfile_name, self.module.FIELDS, self.get_string_fields(), self.module.CALCULATED_FIELDS)

        self.log.info("Done.")


    def outfile_path(self, infile):
        outfile = '{0}_{1}.csv'.format(self.outfile_basename, self.get_year_from_file_path(infile))
        return os.path.join([self.OUT_DIR, outfile])


    def file_is_right_type(self, file_):
        raise NotImplementedError("file_is_right_type() must be defined in the child class")


    def parse_file(self, input_, output, fields, string_lengths, calculated_fields=None):
        reader = csv.DictReader(input_)
        writer = csv.writer(output, delimiter='|')

        def null_transform(value):
            return value

        for line in reader:
            insert_fields = []

            for field in fields:
                fieldname = field[0]
                transform = field[1] or null_transform

                try:
                    value = transform(line[fieldname])
                except Exception, e:
                    value = None
                    self.log.error('|'.join([fieldname, line[fieldname],e.message]))

                insert_fields.append(self.filter_non_values(fieldname, value, string_lengths))

            if calculated_fields:
                for field in calculated_fields:
                    fieldname, built_on_field, transform = field

                    try:
                        if built_on_field:
                            value = transform(line[built_on_field])
                        else:
                            value = transform()
                    except Exception, e:
                        value = None
                        self.log.error('|'.join([fieldname, line.get(built_on_field, ''), e.message]))

                    insert_fields.append(self.filter_non_values(fieldname, value, string_lengths))

            writer.writerow(insert_fields)


    def filter_non_values(self, field, value, string_lengths):
        # indicates that field should be treated as a CharField
        if field in string_lengths:
            if not value or value in ('(none)', 'NULL'):
                return ''

            if not isinstance(value, str):
                self.log.warn("value '%s' for field '%s' is not a string.", value, field)
                value = str(value)

            # need value as unicode in order to compute proper length
            value = value.decode('utf8')

            value = value.strip()

            if len(value) > string_lengths[field]:
                self.log.warn("value '%s' for field '%s' is too long.", value, field)

            value = value[:string_lengths[field]]

            # but need value back as string in order to write to file
            value = value.encode('utf8')

            return value

        else:

            if value == None:
                return "NULL"

            return value


    def get_string_fields(self):
        return dict([(f.name, f.max_length) for f in self.modelclass._meta.fields if isinstance(f, CharField)])


    def get_year_from_file_path(self, file_path):
        return re.search(r'(?P<year>\d{4})_.*\.csv', file_path).group('year')
