# -*- coding: utf-8 -*-
from __future__ import unicode_literals
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

def extract(in_path, out_path, cmg):
    with open(in_path) as f:
        data = f.readlines() # Reads the file as one giant list.
    # Based on how PubChem search results are formatted, this takes every
    # fourth line of the file, alternately starting from lines 4 and 2,
    # to get separate lists of the CIDs and synonym strings. 
    cids = data[3::4]
    syns = data[1::4]
    if len(cids) != len(syns):
        print '%s: Warning: unequal number of CIDs & synonym strings.' % cmg
    # Extract CIDs:
    cids = [x.lstrip('CID: ').rstrip('\r\n') for x in cids]
    # Extract CASRNs:
    casrns = [casrn.find_valid(x) for x in syns]
    # Arbitrarily extract the first synonym in the list:
    syn1 = [x.split(';')[0].split('.')[1] for x in syns]
    # Compile into a dict:
    results = {cids[i]: {'casrn': casrns[i], 'syn': syn1[i]}
               for i in range(len(cids))}

    # Output as JSON:
    with open(os.path.join(out_path, cmg + '.json'), 'w') as f:
        # This will write out the entire data structure, including
        # all CASRNs found among the synonyms for each CID.
        json.dump(results, f)

    # Output as CSV (abridged):
    with open(os.path.join(out_path, cmg + '.csv'), 'w') as f:
        w = csv.writer(f)
        w.writerow(['CID', 'synonym', 'CASRN', 'CMG'])
        # This will only output the first CASRN if there are more than one.
        for c in cids:
            if len(results[c]['casrn']) > 0:
                cas = results[c]['casrn'][0]
            else:
                cas = ''
            w.writerow([c, results[c]['syn'], cas, cmg])
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