import csv, sys, os, re, fpds, faads

class USASpendingDenormalizer:
    re_contracts = re.compile('.*[cC]ontracts.*')

    def parse_file(self, input, output, fields):
        reader = csv.DictReader(input)

        def null_transform(value):
            return value

        for line in reader:
            insert_fields = []

            for field in fields:
                csv_fieldname = field[0]
                db_fieldname = field[1]
                transform = field[2] or null_transform

                try:
                    value = transform(line[csv_fieldname])
                except Exception, e:
                    value = None
                    print >> sys.stderr, csv_fieldname, '|', line[csv_fieldname], '|', e.message

                insert_fields.append(self.field_assignment_for_value(value))

            print >> output, ','.join(insert_fields)


    def parse_directory(self, in_path, out_path=None, out_grants_path=None, out_contracts_path=None):
        if not out_path:
            out_path = os.path.join(path, 'out')

        if not os.path.exists(out_path):
            os.mkdir(out_path)

        out_grants = open(out_grants_path, 'w')
        out_contracts = open(out_contracts_path, 'w')

        for file in os.listdir(in_path):
            file_path = os.path.join(in_path, file)

            if os.path.isfile(file_path):
                input = open(file_path, 'rb')

                print file_path

                if self.re_contracts.match(file):
                    self.parse_file(input, out_contracts, fpds.FPDS_FIELDS)
                else:
                    self.parse_file(input, out_grants, faads.FAADS_FIELDS)

                input.close()

        out_grants.close()
        out_contracts.close()


    def field_assignment_for_value(self, value):
        if value:
            if isinstance(value, int):
                return '"%d"' % value
            elif isinstance(value, float):
                return '"%f"' % value
            else:
                return '"%s"' % value
        else:
            return 'NULL'


if __name__ == '__main__':
    out_grants_path = os.path.join(out_path, 'grants.out')
    out_contracts_path = os.path.join(out_path, 'contracts.out')

    USASpendingDenormalizer().parse_directory('../20101101_csv/datafeeds/', None, out_grants_path, out_contracts_path)
