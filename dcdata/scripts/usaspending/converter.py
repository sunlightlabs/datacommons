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

class USASpendingDenormalizer:
    re_contracts = re.compile('.*[cC]ontracts.*')

    def parse_file(self, input, output, fields, model, calculated_fields=None):
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

                insert_fields.append(self.filter_non_values(value, model._meta.get_field(fieldname)))

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

                    insert_fields.append(self.filter_non_values(value,  model._meta.get_field(fieldname)))

            writer.writerow(insert_fields)


    def filter_non_values(self, value, django_field):
        if isinstance(django_field, CharField):
            if not value or value in ('(none)'):
                return ''

            if not isinstance(value, str):
                print >> sys.stderr, "Warning: value '%s' for field '%s' is not a string." % (value, django_field.name)
                value = str(value)
            
            value = value.strip()
            
            if len(value) > django_field.max_length:
                print >> sys.stderr, "Warning: value '%s' for field '%s' is too long." % (value, django_field.name)

            return value[:django_field.max_length]
        
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
                    self.parse_file(input, out_contracts, fpds.FPDS_FIELDS, Contract, fpds.CALCULATED_FPDS_FIELDS)
                else:
                    self.parse_file(input, out_grants, faads.FAADS_FIELDS, Grant, faads.CALCULATED_FAADS_FIELDS)

                input.close()

        out_grants.close()
        out_contracts.close()
