#!/usr/bin/env python

from dcdata.contracts.models import Contract
from dcdata.grants.models import Grant
from django.db.models.fields import CharField
import csv
import faads
import fpds
import os
import os.path
import re
import sys


CONTRACT_STRINGS = dict([(f.name, f.max_length) for f in Contract._meta.fields if isinstance(f, CharField)])
GRANT_STRINGS = dict([(f.name, f.max_length) for f in Grant._meta.fields if isinstance(f, CharField)])
                     

class USASpendingDenormalizer:
    re_contracts = re.compile('.*[cC]ontracts.*')

    def parse_file(self, input, output, fields, string_lengths, calculated_fields=None):
        reader = csv.DictReader(input)
        writer = csv.writer(output, delimiter='|')

        def null_transform(value):
            return value

        for line in reader:
            insert_fields = []

            for field in fields:
                fieldname = field[0]
                db_fieldname = field[1] # todo: delete this data, it isn't used
                transform = field[2] or null_transform

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
        

    def parse_directory(self, in_path, out_path, out_grants_path, out_contracts_path):
        if not out_path:
            out_path = os.path.join(in_path, 'out')

        if not os.path.exists(out_path):
            os.mkdir(out_path)

        out_grants = open(out_grants_path, 'w')
        out_contracts = open(out_contracts_path, 'w')

        for file in os.listdir(in_path):
            file_path = os.path.join(in_path, file)

            if os.path.isfile(file_path):
                input = open(file_path, 'rb')

                if self.re_contracts.match(file):
                    self.parse_file(input, out_contracts, fpds.FPDS_FIELDS, CONTRACT_STRINGS, fpds.CALCULATED_FPDS_FIELDS)
                else:
                    self.parse_file(input, out_grants, faads.FAADS_FIELDS, GRANT_STRINGS, faads.CALCULATED_FAADS_FIELDS)

                input.close()

        out_grants.close()
        out_contracts.close()
