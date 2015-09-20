# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import os
import sys
_CUR_PATH = os.path.dirname(os.path.abspath(__file__))
_PARENT_PATH = os.path.dirname(_CUR_PATH)
sys.path.append(_PARENT_PATH)
import glob
import argparse
import re
import csv
import json
from builtins import str
import xlrd
import time
from chemex.casrn import validate, find_valid
from ghs import ghs_hazards, h_statements

DATA_PATH = os.path.join(_PARENT_PATH, 'data', 'ghs')
RESULTS_PATH = os.path.join(_PARENT_PATH, 'results', 'ghs')

# These are the hazard class keywords corresponding to the spreadsheet fields.
# hazard_classes = [
#     'explosive',
#     'flamm_gas',
#     'flamm_aer',
#     'oxid_gas',
#     'gas_press',
#     'flamm_liq',
#     'flamm_sol',
#     'self_react',
#     'pyro_liq',
#     'pyro_sol',
#     'self_heat',
#     'emit_flamm',
#     'oxid_liq',
#     'oxid_sol',
#     'org_perox',
#     'corr_mtl',
#     'acute_oral',
#     'acute_derm',
#     'acute_gas',
#     'acute_vap',
#     'acute_dust',
#     'skin_corr',
#     'eye_dmg',
#     'resp_sens',
#     'skin_sens',
#     'mutagen',
#     'cancer',
#     'repr_tox',
#     'sys_single',
#     'sys_rept',
#     'asp_haz',
#     'aq_acute',
#     'aq_chronic'
#     ]

# These are the hazard class keywords corresponding to the spreadsheet fields,
# and their correspondences to GHS Revision 4.
hazard_classes = {
    'explosive':    '2.1',
    'flamm_gas':    '2.2',
    'flamm_aer':    '2.3',
    'oxid_gas':     '2.4',
    'gas_press':    '2.5',
    'flamm_liq':    '2.6',
    'flamm_sol':    '2.7',
    'self_react':   '2.8',
    'pyro_liq':     '2.9',
    'pyro_sol':     '2.10',
    'self_heat':    '2.11',
    'emit_flamm':   '2.12',
    'oxid_liq':     '2.13',
    'oxid_sol':     '2.14',
    'org_perox':    '2.15',
    'corr_mtl':     '2.16',
    'acute_oral':   '3.1',
    'acute_derm':   '3.1',
    'acute_gas':    '3.1',
    'acute_vap':    '3.1',
    'acute_dust':   '3.1',
    'skin_corr':    '3.2',
    'eye_dmg':      '3.3',
    'resp_sens':    '3.4',
    'skin_sens':    '3.4',
    'mutagen':      '3.5',
    'cancer':       '3.6',
    'repr_tox':     '3.7',
    'sys_single':   '3.8',
    'sys_rept':     '3.9',
    'asp_haz':      '3.10',
    'aq_acute':     '4.1',
    'aq_chronic':   '4.1'
    }

def update(d, key, data):
    # Copies classification data into the dict passed as first argument.
    # Does not overwrite the original classification info with blank
    # sections of the revised classification.
    if key in d['classifications'] and data[1].strip('- ') != '':
        pass # Don't overwrite with blank classification
    else:
        new_cls = {key: {'hazard_name': key,
                         'ghs_code': hazard_classes[key],
                         'classification': data[1].strip('- '),
                         'symbol': data[2].strip('- '),
                         'signal_word': data[3].strip('- '),
                         'hazard_statement': data[4].strip('- '),
                         'rationale': data[5].strip('- '),
                         'date_classified': data[6].strip('- '),
                         'date_imported': time.ctime(),
                         'country_code': 'jp'
                         }}
        d['classifications'].update(new_cls)

def update_all(chms, f):
    # Creates/updates the dict of classifications from a given spreadsheet.
    book = xlrd.open_workbook(f)
    for i in range(1, book.nsheets): # Ignore the first sheet.
        sh = book.sheet_by_index(i)
        # Cells are identified by (row, col) where A1 is (0, 0).
        ID = sh.cell_value(2, 1).strip()
        CASRN = sh.cell_value(2, 2).strip('- ')
        name = sh.cell_value(2, 3).strip()
        # Generate a list of valid CASRNs for each chemical.
        if CASRN == '':
            # Must use something as unique ID if CASRN is blank.
            # The index IDs are not consistent across datasets (2007 - 2009).
            casrns = [ID + (name[:4] + name[-4:]).replace(',', '')]
        else:
            casrns = find_valid(CASRN)
        d = sh.cell_value(7,2) # Date classified
        
        # Treating each CASRN as a unique substance (even if not really unique).
        # The field CML_INPUT_ID will contain "the" CASRN for each item.
        for c in casrns:
            if c not in chms:
                chms[c] = dict(name=name, casrns=casrns, jp_ID=ID,
                                   CML_INPUT_ID=c, classifications=dict())    
            # We are going to extract columns 2-7 from each row individually.
            # col 2: Hazard class name
            # col 3: Classification
            # col 4: Symbol
            # col 5: Signal word
            # col 6: Hazard statement
            # col 7: Rationale for classification
            update(chms[c], 'explosive',  sh.row_values(7)[2:8]  + [d])
            update(chms[c], 'flamm_gas',  sh.row_values(8)[2:8]  + [d])
            update(chms[c], 'flamm_aer',  sh.row_values(9)[2:8]  + [d])
            update(chms[c], 'oxid_gas',   sh.row_values(10)[2:8] + [d])
            update(chms[c], 'gas_press',  sh.row_values(11)[2:8] + [d])
            update(chms[c], 'flamm_liq',  sh.row_values(12)[2:8] + [d])
            update(chms[c], 'flamm_sol',  sh.row_values(13)[2:8] + [d])
            update(chms[c], 'self_react', sh.row_values(14)[2:8] + [d])
            update(chms[c], 'pyro_liq',   sh.row_values(15)[2:8] + [d])
            update(chms[c], 'pyro_sol',   sh.row_values(16)[2:8] + [d])
            update(chms[c], 'self_heat',  sh.row_values(17)[2:8] + [d])
            update(chms[c], 'emit_flamm', sh.row_values(18)[2:8] + [d])
            update(chms[c], 'oxid_liq',   sh.row_values(19)[2:8] + [d])
            update(chms[c], 'oxid_sol',   sh.row_values(20)[2:8] + [d])
            update(chms[c], 'org_perox',  sh.row_values(21)[2:8] + [d])
            update(chms[c], 'corr_mtl',   sh.row_values(22)[2:8] + [d])
            update(chms[c], 'acute_oral', sh.row_values(26)[2:8] + [d])
            update(chms[c], 'acute_derm', sh.row_values(27)[2:8] + [d])
            update(chms[c], 'acute_gas',  sh.row_values(28)[2:8] + [d])
            update(chms[c], 'acute_vap',  sh.row_values(29)[2:8] + [d])
            update(chms[c], 'acute_dust', sh.row_values(30)[2:8] + [d])
            update(chms[c], 'skin_corr',  sh.row_values(31)[2:8] + [d])
            update(chms[c], 'eye_dmg',    sh.row_values(32)[2:8] + [d])
            # For respiratory & skin sensitization, we need to split strings.
            # Don't include cell 2, it's automatically added by splitsens().
            # resp_only, skin_only = splitsens(sh.row_values(31)[3:8])
            # update(chms[c], 'resp_sens',
            #        resp_only + [d])
            # update(chms[c], 'skin_sens',
            #        skin_only + [d])
            update(chms[c], 'resp_sens',  sh.row_values(33)[2:8] + [d])
            update(chms[c], 'skin_sens',  sh.row_values(34)[2:8] + [d])
            update(chms[c], 'mutagen',    sh.row_values(35)[2:8] + [d])
            update(chms[c], 'cancer',     sh.row_values(36)[2:8] + [d])
            update(chms[c], 'repr_tox',   sh.row_values(37)[2:8] + [d])
            update(chms[c], 'sys_single', sh.row_values(38)[2:8] + [d])
            update(chms[c], 'sys_rept',   sh.row_values(39)[2:8] + [d])
            update(chms[c], 'asp_haz',    sh.row_values(40)[2:8] + [d])
            update(chms[c], 'aq_acute',   sh.row_values(44)[2:8] + [d])
            update(chms[c], 'aq_chronic', sh.row_values(45)[2:8] + [d])

def extract():
    # File locations:
    # - separate directories for 'new' and 'revised' classifications.
    # - results all in one place.
    JP_DATA_NEW_PATH = os.path.join(DATA_PATH, 'jp', 'new')
    JP_DATA_REV_PATH = os.path.join(DATA_PATH, 'jp', 'rev')
    JP_RESULTS_PATH = os.path.join(RESULTS_PATH, 'jp')
    # Find files:
    new_search = os.path.join(JP_DATA_NEW_PATH, '*.xl*')
    new_files = glob.glob(new_search)
    rev_search = os.path.join(JP_DATA_REV_PATH, '*.xl*')
    rev_files = glob.glob(rev_search)
    # Initialize a dict that will contain data about all chemicals. 
    # Each key will be a unique ID (mostly CASRN), and each value will itself be 
    # a dict data structure containing the name, classifications, etc.
    chms = dict()
    for f in new_files[1:3]:            ### <<<  TESTING !!!!
        update_all(chms, f)
    for f in rev_files[0:3]:            ### <<<  TESTING !!!!
        update_all(chms, f)

    # Output to JSON...
    print(json.dumps(chms))
    # for c in sorted(chms.keys())[:2]:   ### <<<  TESTING !!!!
    #     print(json.dumps(chms[c]))

def main():
    print('Processing Japan GHS classifications.')
    extract()

if __name__ == '__main__':
    main()