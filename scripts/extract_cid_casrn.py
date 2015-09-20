# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import os
import sys
_CUR_PATH = os.path.dirname(os.path.abspath(__file__))
_PARENT_PATH = os.path.dirname(_CUR_PATH)
sys.path.append(_PARENT_PATH)
import argparse
import glob
import re
import csv
import json
from chemex import casrn

def clean_names(syns):
    # The list is '; '-delimited, and includes names like 'beryllium;lead'...
    z = syns.split('; ')
    # Separate the first synoynm in the list from the heading number.
    z[0] = z[0].split('.')[1]
    # Clean up all the synonyms.
    z = [x.strip('\r\n ') for x in z]
    # Try (imperfectly) to find the first name that's not an alphanumeric ID.
    p = re.compile(r'[0-9A-Z_-]{5,}')
    for x in z:
        if p.match(x):
            continue
        else:
            s = x
            break
    else:
        s = z[0]
    # Returns: [best synonym, [all synonyms]]
    return [s, z]

def extract(in_path, out_path, cmg):
    with open(in_path) as f:
        data = f.readlines() # Reads the file as one giant list.
    # Based on how PubChem search results are formatted, this takes every
    # fourth line of the file, alternately starting from lines 4 and 2,
    # to get separate lists of the CIDs and synonym strings. 
    cids = data[3::4]
    syns = data[1::4]
    if len(cids) != len(syns):
        print('{0}: Warning: unequal number of CIDs & synonym strings.'.format(cmg))
    # Extract CIDs:
    cids = [x.lstrip('CID: ').rstrip('\r\n') for x in cids]
    # Extract CASRNs:
    cas_rns = [casrn.find_valid(x) for x in syns]
    # Find what looks like a 'name', and also gather all synonyms as a list.
    names = [clean_names(x) for x in syns]
    # Compile into a dict:
    results = {cids[i]: {'casrn': cas_rns[i], 'name': names[i][0],
                         'syns': names[i][1]} for i in range(len(cids))}
    # Output as JSON: This writes out the entire data structure.
    with open(os.path.join(out_path, cmg + '.json'), 'w') as f:
        json.dump(results, f)
    # Output as CSV (abridged): This only writes out entries for which a valid
    # CASRN was found; includes only the first CASRN if found more than one;
    # and includes only one synonym.
    with open(os.path.join(out_path, cmg + '.csv'), 'w') as f:
        w = csv.writer(f)
        w.writerow(['CID', 'synonym', 'CASRN', 'CMG'])
        for c in cids:
            if len(results[c]['casrn']) > 0:
                w.writerow([c, results[c]['name'],
                            results[c]['casrn'][0], cmg])
            else:
                pass

def main():
    d = 'Extract CID-CASRN correspondences from PubChem structure output.'
    parser = argparse.ArgumentParser(description=d)
    parser.add_argument('-i', metavar='input_dir',
                        help='directory containing input files (CMG*.txt)',
                        default='data/extract-cid-casrn')
    parser.add_argument('-o', metavar='output_dir',
                        help='directory where output files will be generated',
                        default='results/extract-cid-casrn')
    args = parser.parse_args()
    in_path = os.path.abspath(args.i)
    out_path = os.path.abspath(args.o)
    input_search = os.path.join(in_path, 'CMG*.txt')
    files = glob.glob(input_search)
    for f in files:
        cmg = os.path.split(f)[1].split('.')[0]
        extract(f, out_path, cmg)

if __name__ == '__main__':
    main()