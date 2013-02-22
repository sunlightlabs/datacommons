from csv import DictReader, DictWriter
from name_cleaver import PoliticianNameCleaver
import sys

with open(sys.argv[-2], 'r') as input_file:
    with open(sys.argv[-1], 'w') as output_file:
        dr = DictReader(input_file)

        new_fieldnames = dr.fieldnames
        new_fieldnames.append('name_confidence')

        dw = DictWriter(output_file, fieldnames=new_fieldnames)

        dw.writeheader()

        for row in dr:
            name_x = PoliticianNameCleaver(row['name.x']).parse()
            name_y = PoliticianNameCleaver(row['name.y']).parse()

            score = 0
            if name_x.last == name_y.last:
                score += 1
            else:
                score -= 1

            if name_x.first and name_y.first:
                if name_x.first == name_y.first:
                    score += 1
                elif name_x.first[0] == name_y.first[0]:
                    score += .3
            else:
                score -= .5

            if name_x.middle and name_y.middle:
                if name_x.middle == name_y.middle:
                    score += 1
                elif name_x.middle[0] == name_y.middle[0]:
                    score += .2

            row['name_confidence'] = score

            dw.writerow(row)



