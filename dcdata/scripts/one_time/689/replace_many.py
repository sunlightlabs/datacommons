#!/usr/bin/env python

import sys, os, os.path

replacements_file = sys.argv[-2]
file_to_operate_on = sys.argv[-1]
replacements_fh = open(os.path.abspath(replacements_file), 'r')

for line in replacements_fh:
    str,replace = [ x.strip() for x in line.split('|') ]

    os.system("sed -i 's/{0}/{1}/g' {2}".format(str, replace, file_to_operate_on))

