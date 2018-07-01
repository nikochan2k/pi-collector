#!/usr/bin/python2
# -*- encoding: utf-8 -*-

import sys
import os


def generate(in_path, out_path):
    out_file = open(out_path, 'w')
    out_file.write('VENDORS = {}\n')
    in_file = open(in_path, 'r')
    for line in in_file:
        if not '(hex)' in line:
            continue
        chunks = line.split('(hex)')
        vendor_id = chunks[0].strip().upper().replace('-',':')
        vendor_name = chunks[1].strip()
        out_file.write("VENDORS['%s'] = '%s'\n" % (vendor_id, vendor_name.replace("'", "\\'")))
    in_file.close()
    out_file.close()


if __name__ == '__main__':
    args = sys.argv
    if len(args) < 2:
        print('genoui.py [oui.txt]')
        sys.exit(1)
        
    generate(args[1], 'oui.py')

