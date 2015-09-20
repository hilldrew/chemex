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
import xlrd
import pandas as pd
from pandas import DataFrame
import time
from chemex.casrn import validate, find_valid

DATA_PATH = os.path.join(_PARENT_PATH, 'data', 'ghs')
RESULTS_PATH = os.path.join(_PARENT_PATH, 'results', 'ghs')
# File locations for GHS Japan:
#   Separate directories for 'new' and 'revised' classifications.
#   Results all in one place.
JP_DATA_NEW_PATH = os.path.join(DATA_PATH, 'jp', 'new')
JP_DATA_REV_PATH = os.path.join(DATA_PATH, 'jp', 'rev')
JP_RESULTS_PATH = os.path.join(RESULTS_PATH, 'jp')

# These are the hazard class keywords corresponding to the spreadsheet fields
# and their correspondences to GHS Revision 4.
jp_haz_keywords = {
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
    'aq_chronic':   '4.1',
    'ozone':        '4.2'
    }

# These are the hazard class keywords corresponding to the spreadsheet fields
# and their full names, which differ slightly from top-level GHS classes.
jp_haz_classes = {
    'explosive':  'Explosives',
    'flamm_gas':  'Flammable gases（including chemically unstable gases',
    'flamm_aer':  'Aerosols',
    'oxid_gas':   'Oxidizing gases',
    'gas_press':  'Gases under pressure',
    'flamm_liq':  'Flammable liquids',
    'flamm_sol':  'Flammable solids',
    'self_react': 'Self-reactive substances and mixtures',
    'pyro_liq':   'Pyrophoric liquids',
    'pyro_sol':   'Pyrophoric solids',
    'self_heat':  'Self-heating substances and mixtures',
    'emit_flamm': 'Substances and mixtures which, in contact with water, emit flammable gases',
    'oxid_liq':   'Oxidizing liquids',
    'oxid_sol':   'Oxidizing solids',
    'org_perox':  'Organic peroxides',
    'corr_mtl':   'Corrosive to metals',
    'acute_oral': 'Acute toxicity（Oral)',
    'acute_derm': 'Acute toxicity（Dermal)',
    'acute_gas':  'Acute toxicity（Inhalation: Gases)',
    'acute_vap':  'Acute toxicity（Inhalation: Vapours)',
    'acute_dust': 'Acute toxicity（Inhalation: Dusts and mists)',
    'skin_corr':  'Skin corrosion/irritation',
    'eye_dmg':    'Serious eye damage/eye irritation',
    'resp_sens':  'Respiratory sensitization',
    'skin_sens':  'Skin sensitization',
    'mutagen':    'Germ cell mutagenicity',
    'cancer':     'Carcinogenicity',
    'repr_tox':   'Reproductive toxicity',
    'sys_single': 'Specific target organ toxicity (Single exposure)',
    'sys_rept':   'Specific target organ toxicity (Repeated exposure)',
    'asp_haz':    'Aspiration hazard',
    'aq_acute':   'Hazardous to the aquatic environment（Acute',
    'aq_chronic': 'Hazardous to the aquatic environment（Long-term)',
    'ozone':      'Hazardous to the ozone layer'
}

# Columns in output Excel files.
xl_cols =  ['CML_INPUT_ID',  'casrns', 'name', 'classification', 
            'hazard_statement', 'symbol', 'signal_word', 'rationale',
          # 'ghs_code', 'hazard_name', # << Leaving these fields out.
            'country_code', 'jp_ID', 'date_classified', 'date_imported',
            'source_filename'] 

def update(d, key, data):
    # Copies classification data into the dict d['classifications'][key].
    # Does not overwrite the original classification info with blank
    # sections of the revised classification.
    if data[0].strip('- ') == '':
        # If the classification is blank, don't add or overwrite data.
        pass
    else:
        cls = {key: {'hazard_name': key,
                     'ghs_code': jp_haz_keywords[key],
                     'classification': data[0].strip('- '),
                     'symbol': data[1].strip('- ').replace('\n', ', '),
                     'signal_word': data[2].strip('- ').replace('\n', ', '),
                     'hazard_statement': data[3].strip('- ')\
                                                .replace('\n', ', '),
                     'rationale': data[4].strip('- '),
                     'source_filename': data[5],
                     'date_classified': data[6].strip('- '),
                     'date_imported': time.ctime(),
                     'country_code': 'jp'
                     }}
        d['classifications'].update(cls)

def update_all(chms, f):
    # Creates/updates the dict of classifications from a given spreadsheet.
    book = xlrd.open_workbook(f)
    for i in range(1, book.nsheets): # Ignore the first sheet.
        sh = book.sheet_by_index(i)
        # Cells are identified by (row, col) where A1 is (0, 0).
        ID = sh.cell_value(1, 2).strip()
        CASRN = sh.cell_value(2, 2).strip('- ')
        name = sh.cell_value(3, 2).strip()
        # Generate a list of valid CASRNs for each chemical.
        if CASRN == '':
            # Must use something as unique ID if CASRN is blank.
            # The index IDs are not consistent across datasets (2007 - 2009).
            casrns = [ID + (name[:4] + name[-4:]).replace(',', '')]
        else:
            casrns = find_valid(CASRN)
        meta = [os.path.basename(f), # File name
                sh.cell_value(2, 7)] # Date classified
        
        # Treating each CASRN as a unique substance (even if not really unique).
        # The field CML_INPUT_ID will contain "the" CASRN for each item.
        for c in casrns:
            if c not in chms:
                chms[c] = dict(name=name, casrns=casrns, jp_ID=ID,
                                   CML_INPUT_ID=c, classifications=dict())    
            # We are going to extract columns 3-7 from each row individually.
            # col 2: Hazard class name (not retrieving)
            # col 3: Classification
            # col 4: Symbol
            # col 5: Signal word
            # col 6: Hazard statement
            # col 7: Rationale for classification
            update(chms[c], 'explosive',  sh.row_values(7,  3, 8) + meta)
            update(chms[c], 'flamm_gas',  sh.row_values(8,  3, 8) + meta)
            update(chms[c], 'flamm_aer',  sh.row_values(9,  3, 8) + meta)
            update(chms[c], 'oxid_gas',   sh.row_values(10, 3, 8) + meta)
            update(chms[c], 'gas_press',  sh.row_values(11, 3, 8) + meta)
            update(chms[c], 'flamm_liq',  sh.row_values(12, 3, 8) + meta)
            update(chms[c], 'flamm_sol',  sh.row_values(13, 3, 8) + meta)
            update(chms[c], 'self_react', sh.row_values(14, 3, 8) + meta)
            update(chms[c], 'pyro_liq',   sh.row_values(15, 3, 8) + meta)
            update(chms[c], 'pyro_sol',   sh.row_values(16, 3, 8) + meta)
            update(chms[c], 'self_heat',  sh.row_values(17, 3, 8) + meta)
            update(chms[c], 'emit_flamm', sh.row_values(18, 3, 8) + meta)
            update(chms[c], 'oxid_liq',   sh.row_values(19, 3, 8) + meta)
            update(chms[c], 'oxid_sol',   sh.row_values(20, 3, 8) + meta)
            update(chms[c], 'org_perox',  sh.row_values(21, 3, 8) + meta)
            update(chms[c], 'corr_mtl',   sh.row_values(22, 3, 8) + meta)
            update(chms[c], 'acute_oral', sh.row_values(26, 3, 8) + meta)
            update(chms[c], 'acute_derm', sh.row_values(27, 3, 8) + meta)
            update(chms[c], 'acute_gas',  sh.row_values(28, 3, 8) + meta)
            update(chms[c], 'acute_vap',  sh.row_values(29, 3, 8) + meta)
            update(chms[c], 'acute_dust', sh.row_values(30, 3, 8) + meta)
            update(chms[c], 'skin_corr',  sh.row_values(31, 3, 8) + meta)
            update(chms[c], 'eye_dmg',    sh.row_values(32, 3, 8) + meta)
            update(chms[c], 'resp_sens',  sh.row_values(33, 3, 8) + meta)
            update(chms[c], 'skin_sens',  sh.row_values(34, 3, 8) + meta)
            update(chms[c], 'mutagen',    sh.row_values(35, 3, 8) + meta)
            update(chms[c], 'cancer',     sh.row_values(36, 3, 8) + meta)
            update(chms[c], 'repr_tox',   sh.row_values(37, 3, 8) + meta)
            update(chms[c], 'sys_single', sh.row_values(38, 3, 8) + meta)
            update(chms[c], 'sys_rept',   sh.row_values(39, 3, 8) + meta)
            update(chms[c], 'asp_haz',    sh.row_values(40, 3, 8) + meta)
            update(chms[c], 'aq_acute',   sh.row_values(44, 3, 8) + meta)
            update(chms[c], 'aq_chronic', sh.row_values(45, 3, 8) + meta)
            # Not all the sheets have a row for ozone depletion.
            # (Some sheets have a row but it's all empty.)
            if sh.nrows > 46:
                update(chms[c], 'ozone',  sh.row_values(46, 3, 8) + meta)
    book.release_resources()

def extract():
    # Find files:
    new_search = os.path.join(JP_DATA_NEW_PATH, '*.xl*')
    new_files = glob.glob(new_search)
    rev_search = os.path.join(JP_DATA_REV_PATH, '*.xl*')
    rev_files = glob.glob(rev_search)
    # Initialize a dict that will contain data about all chemicals. 
    # Each key will be a unique ID (mostly CASRN), and each value will itself be 
    # a dict data structure containing the name, classifications, etc.
    chms = dict()
    for f in new_files:
        update_all(chms, f)
    for f in rev_files:
        update_all(chms, f)

    return chms

def writeout(chms):
    # Serialize the extracted data to a single large JSON object.
    with open(os.path.join(JP_RESULTS_PATH, 'ghs_jp.json'), 'w') as f:
        json.dump(chms, f, sort_keys=True)
    # Also output to Excel files, one for each hazard class. So we need to make
    # a hazard-specific classification list for all chemicals in the dataset.
    for h in sorted(jp_haz_keywords.keys()):
        haz_list = []
        for c in chms.keys():
            if h not in chms[c]['classifications']:
                continue
            d = {k: chms[c][k] for k in chms[c].keys() \
                 if k != 'classifications'}
            d['casrns'] = ', '.join(d['casrns'])
            d.update(chms[c]['classifications'][h])
            d['classification'] = jp_haz_classes[h] + ' - ' \
                                  + d['classification']
            haz_list.append(d)
        df = DataFrame(haz_list, columns=xl_cols).set_index('CML_INPUT_ID')
        df.to_excel(os.path.join(JP_RESULTS_PATH, h + '.xlsx'),
                    engine='xlsxwriter')

def main():
    print('Processing Japan GHS classifications.')
    writeout(extract())

if __name__ == '__main__':
    main()