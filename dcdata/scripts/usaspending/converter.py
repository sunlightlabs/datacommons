#!/usr/bin/env python

from dcdata.contracts.models import Contract
from dcdata.grants.models import Grant
from dcdata.management.base.importer import BaseImporter
from django.db.models.fields import CharField
import csv
import faads
import fpds
import os
import os.path
import re
import sys
import logging


CONTRACT_STRINGS = dict([(f.name, f.max_length) for f in Contract._meta.fields if isinstance(f, CharField)])
GRANT_STRINGS = dict([(f.name, f.max_length) for f in Grant._meta.fields if isinstance(f, CharField)])


class USASpendingDenormalizer(BaseImporter):
    re_contracts = re.compile('.*[cC]ontracts.*.')

    def __init__(self, logger=None):
        self.log = logger or self.set_up_logger()


    def set_up_logger(self):
        # create logger
        self.log = logging.getLogger("command")
        self.log.setLevel(logging.DEBUG)
        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        # create formatter
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        ch.setFormatter(formatter)
        self.log.addHandler(ch)


    def parse_file(self, input, output, fields, string_lengths, calculated_fields=None):
        reader = csv.DictReader(input)
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
                    print >> sys.stderr, '|'.join([fieldname, line[fieldname],e.message])

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
                        print >> sys.stderr, '|'.join([fieldname, line.get(built_on_field, ''), e.message])

                    insert_fields.append(self.filter_non_values(fieldname, value, string_lengths))

            writer.writerow(insert_fields)


    def filter_non_values(self, field, value, string_lengths):
        # indicates that field should be treated as a CharField
        if field in string_lengths:
            if not value or value in ('(none)', 'NULL'):
                return ''

            if not isinstance(value, str):
                print >> sys.stderr, "Warning: value '%s' for field '%s' is not a string." % (value, field)
                value = str(value)

            # need value as unicode in order to compute proper length
            value = value.decode('utf8')

            value = value.strip()

            if len(value) > string_lengths[field]:
                print >> sys.stderr, "Warning: value '%s' for field '%s' is too long." % (value, field)

            value = value[:string_lengths[field]]

            # but need value back as string in order to write to file
            value = value.encode('utf8')

            return value

        else:

            if value == None:
                return "NULL"

            return value


    def parse_directory(self, in_path, out_path):
        if not out_path:
            out_path = os.path.join(os.path.abspath(in_path), 'out')
            self.log.info("Out path wasn't set. Setting it to {0}".format(out_path))

        if not os.path.exists(out_path):
            os.mkdir(out_path)
            self.log.info("Out path didn't exist. Creating {0}".format(out_path))

        out_grants = open(os.path.join(out_path, 'grants.out'), 'w')
        out_contracts = open(os.path.join(out_path, 'contracts.out'), 'w')

        self.log.info("Looking for input files...")
        for file in os.listdir(in_path):
            file_path = os.path.join(in_path, file)
            self.log.info("    Found {0}".format(file_path))

            if os.path.isfile(file_path):
                input = open(file_path, 'rb')

                self.log.info("    Converting {0}...".format(file_path))

                if self.re_contracts.match(file):
                    self.parse_file(input, out_contracts, fpds.FIELDS, CONTRACT_STRINGS, fpds.CALCULATED_FIELDS)
                else:
                    self.parse_file(input, out_grants, faads.FIELDS, GRANT_STRINGS, faads.CALCULATED_FIELDS)

                input.close()

        out_grants.close()
        out_contracts.close()

        self.log.info("Done with input files.")

