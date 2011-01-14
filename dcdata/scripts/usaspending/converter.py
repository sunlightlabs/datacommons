#!/usr/bin/env python

import csv, sys, os, os.path, re, fpds, faads

class USASpendingDenormalizer:
    re_contracts = re.compile('.*[cC]ontracts.*')

    def parse_file(self, input, output, fields, calculated_fields=None):
        reader = csv.DictReader(input)
        writer = csv.writer(output, delimiter='|')

        def null_transform(value):
            return value

        for line in reader:
            insert_fields = []

            for field in fields:
                csv_fieldname = field[0]
                db_fieldname = field[1] # todo: delete this data, it isn't used
                transform = field[2] or null_transform

                try:
                    value = transform(line[csv_fieldname])
                except Exception, e:
                    value = None
                    print >> sys.stderr, '|'.join([csv_fieldname, line[csv_fieldname],e.message])

                insert_fields.append(self.filter_non_values(value))

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

                    insert_fields.append(self.filter_non_values(value))

            writer.writerow(insert_fields)

    def filter_non_values(self, value):
        if value == None:
            return "NULL"
        
        if isinstance(value, str):
            if value in ('(none)'):
                return ''
            else:
                return value.strip()
        
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
                    self.parse_file(input, out_contracts, fpds.FPDS_FIELDS, fpds.CALCULATED_FPDS_FIELDS)
                else:
                    self.parse_file(input, out_grants, faads.FAADS_FIELDS, faads.CALCULATED_FAADS_FIELDS)

                input.close()

        out_grants.close()
        out_contracts.close()


if __name__ == '__main__':
    out_path = sys.argv[-1]
    in_path = sys.argv[-2]
    out_grants_path = os.path.join(os.path.abspath(out_path), 'grants.out')
    out_contracts_path = os.path.join(os.path.abspath(out_path), 'contracts.out')

    USASpendingDenormalizer().parse_directory(os.path.abspath(in_path), None, out_grants_path, out_contracts_path)
