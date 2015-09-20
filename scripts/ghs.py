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
from builtins import str
import xlrd
from chemex import casrn

DATA_PATH = os.path.join(_PARENT_PATH, 'data', 'ghs')
RESULTS_PATH = os.path.join(_PARENT_PATH, 'results', 'ghs')

# ghs.py
# Extract GHS chemical hazard classification information out of various
# international government documents. By Akos Kokai.

# GHS hazard classes, based on GHS Revision 4 chapter reference.
ghs_hazards = {
    '2.1': 'Explosives',
    '2.2': 'Flammable gases',
    '2.3': 'Aerosols',
    '2.4': 'Oxidizing gases',
    '2.5': 'Gases under pressure',
    '2.6': 'Flammable liquids',
    '2.7': 'Flammable solids',
    '2.8': 'Self-reactive substances and mixtures',
    '2.9': 'Pyrophoric liquids',
    '2.10': 'Pyrophoric solids',
    '2.11': 'Self-heating substances and mixtures',
    '2.12': 'Substances and mixtures which, in contact with water, emit flammable gases',
    '2.13': 'Oxidizing liquids',
    '2.14': 'Oxidizing solids',
    '2.15': 'Organic peroxides',
    '2.16': 'Corrosive to metals',
    '3.1': 'Acute toxicity',
    '3.2': 'Skin corrosion/irritation',
    '3.3': 'Serious eye damage/irritation',
    '3.4': 'Respiratory or skin sensitization',
    '3.5': 'Germ cell mutagenicity',
    '3.6': 'Carcinogenicity',
    '3.7': 'Reproductive toxicity',
    '3.8': 'Specific target organ toxicity - Single exposure',
    '3.9': 'Specific target organ toxicity - Repeated exposure',
    '3.10': 'Aspiration hazard',
    '4.1': 'Hazardous to the aquatic environment',
    '4.2': 'Hazardous to the ozone layer'
    }

# H-statements: List from GHS Revision 4.
# Did not include the abbreviated combinations (e.g. H302 + H332).
h_statements = {
    'H200': 'Unstable explosive',
    'H201': 'Explosive; mass explosion hazard',
    'H202': 'Explosive; severe projection hazard',
    'H203': 'Explosive; fire, blast or projection hazard',
    'H204': 'Fire or projection hazard',
    'H205': 'May mass explode in fire',
    'H220': 'Extremely flammable gas',
    'H221': 'Flammable gas',
    'H222': 'Extremely flammable aerosol',
    'H223': 'Flammable aerosol',
    'H224': 'Extremely flammable liquid and vapour',
    'H225': 'Highly flammable liquid and vapour',
    'H226': 'Flammable liquid and vapour',
    'H227': 'Combustible liquid',
    'H228': 'Flammable solid',
    'H229': 'Pressurized container: may burst if heated',
    'H230': 'May react explosively even in the absence of air',
    'H231': 'May react explosively even in the absence of air at elevated pressure and/or temperature',
    'H240': 'Heating may cause an explosion',
    'H241': 'Heating may cause a fire or explosion',
    'H242': 'Heating may cause a fire',
    'H250': 'Catches fire spontaneously if exposed to air',
    'H251': 'Self-heating; may catch fire',
    'H252': 'Self-heating in large quantities; may catch fire',
    'H260': 'In contact with water releases flammable gases which may ignite spontaneously',
    'H261': 'In contact with water releases flammable gas',
    'H270': 'May cause or intensify fire; oxidizer',
    'H271': 'May cause fire or explosion; strong oxidizer',
    'H272': 'May intensify fire; oxidizer',
    'H280': 'Contains gas under pressure; may explode if heated',
    'H281': 'Contains refrigerated gas; may cause cryogenic burns or injury',
    'H290': 'May be corrosive to metals',
    'H300': 'Fatal if swallowed',
    'H301': 'Toxic if swallowed',
    'H302': 'Harmful if swallowed',
    'H303': 'May be harmful if swallowed',
    'H304': 'May be fatal if swallowed and enters airways',
    'H305': 'May be harmful if swallowed and enters airways',
    'H310': 'Fatal in contact with skin',
    'H311': 'Toxic in contact with skin',
    'H312': 'Harmful in contact with skin',
    'H313': 'May be harmful in contact with skin',
    'H314': 'Causes severe skin burns and eye damage',
    'H315': 'Causes skin irritation',
    'H316': 'Causes mild skin irritation',
    'H317': 'May cause an allergic skin reaction',
    'H318': 'Causes serious eye damage',
    'H319': 'Causes serious eye irritation',
    'H320': 'Causes eye irritation',
    'H330': 'Fatal if inhaled',
    'H331': 'Toxic if inhaled',
    'H332': 'Harmful if inhaled',
    'H333': 'May be harmful if inhaled',
    'H334': 'May cause allergy or asthma symptoms or breathing difficulties if inhaled',
    'H335': 'May cause respiratory irritation',
    'H336': 'May cause drowsiness or dizziness',
    'H340': 'May cause genetic defects',
    'H341': 'Suspected of causing genetic defects',
    'H350': 'May cause cancer',
    'H351': 'Suspected of causing cancer',
    'H360': 'May damage fertility or the unborn child',
    'H361': 'Suspected of damaging fertility or the unborn child',
    'H362': 'May cause harm to breast-fed children',
    'H370': 'Causes damage to organs',
    'H371': 'May cause damage to organs',
    'H372': 'Causes damage to organs through prolonged or repeated exposure',
    'H373': 'May cause damage to organs through prolonged or repeated exposure',
    'H400': 'Very toxic to aquatic life',
    'H401': 'Toxic to aquatic life',
    'H402': 'Harmful to aquatic life',
    'H410': 'Very toxic to aquatic life with long lasting effects',
    'H411': 'Toxic to aquatic life with long lasting effects',
    'H412': 'Harmful to aquatic life with long lasting effects',
    'H413': 'May cause long lasting harmful effects to aquatic life',
    'H420': 'Harms public health and the environment by destroying ozone in the upper atmosphere'
    }

def extract_jp():
    import ghs_jp
    ghs_jp.extract()

def extract_kr():
    # Process the Korea GHS classification (2011).
    KR_DATA_PATH = os.path.join(DATA_PATH, 'kr')
    KR_RESULTS_PATH = os.path.join(RESULTS_PATH, 'kr')
    chembook = xlrd.open_workbook(os.path.join(_KR_DATA_PATH, # THE FILENAME...
                                               'GHS-kr-2011-04-15.xls'))
    chemsheet = chembook.sheet_by_index(0)
    outfile = open(os.path.join(_KR_RESULTS_PATH, 'GHS-kr.csv'), 'w')
    listwriter = csv.writer(outfile)
    # For practical purposes, I am going to combine the hazard class,
    # category, and H-statement fields into one 'Hazard sublist' field. 
    listwriter.writerow(['CASRN', 'Name', 'Synonyms', 'Hazard sublist', 
                         'M-factor'])
    # I also want to enumerate the unique class/category/H-statement
    # combinations (sublists).
    sublists = set()
    # Read in the spreadsheet; process and output results for each line.
    for r in range(16,1208):
        # Name:           (r, 1)
        # CASRN:          (r, 3)
        # Don't overwrite name and CASRN with blanks from merged cells.
        if chemsheet.cell_value(r, 1) != '':
            name_field = chemsheet.cell_value(r, 1)
            # Split lists of synonyms into 2 fields.
            names = name_field.split(';', 1)
            for i in range(len(names)):
                names[i] = names[i].strip()
            while len(names) < 2:
                names.append('')
        if chemsheet.cell_value(r, 3) != '':
            casrn_field = chemsheet.cell_value(r, 3)
        # Hazard class    (r, 4)
        # Hazard category (r, 5)
        # Pictogram code  (r, 6) - (not used anymore?)
        # Signal word     (r, 7) - (in Korean)
        # H-stmnt code    (r, 8)
        # M-factor        (r, 9)
        haz_class_field = chemsheet.cell_value(r, 4)
        ref = haz_class_field[haz_class_field.find('('):].strip('()')
        haz_class_en = ghs_hazards[ref]
        if ref == '3.1':
            if u'급성 독성-경구' in haz_class_field:
                haz_class_en = 'Acute toxicity (oral)'
            elif u'급성 독성-경피' in haz_class_field:
                haz_class_en = 'Acute toxicity (dermal)'
            elif u'급성 독성-흡입' in haz_class_field:
                haz_class_en = 'Acute toxicity (inhalation)'
            else:
                print('Found a different hazard class 3.1 in row ' + str(r))
        if ref == '3.4':
            if u'피부 과민성' in haz_class_field:
                haz_class_en = 'Skin sensitization'
            elif u'호흡기 과민성' in haz_class_field:
                haz_class_en = 'Respiratory sensitization'
            else:
                print('Found a different hazard class 3.4 in row ' + str(r))
        if ref == '4.1':
            if u'수생환경유해성-급성' in haz_class_field:
                haz_class_en = 'Hazardous to the aquatic environment (acute)'
            elif u'수생환경유해성-만성' in haz_class_field:
                haz_class_en = 'Hazardous to the aquatic environment (chronic)'
            else:
                print('Found a different hazard class 4.1 in row ' + str(r))
        # Category values are integers stored as floats.
        category = 'Category ' + str(int(chemsheet.cell_value(r, 5)))
        h_code = chemsheet.cell_value(r, 8)
        h_state = h_code + ' - ' + h_statements[h_code]
        # Make the combined hazard class/category/H-statement field:
        s = haz_class_en + ' - ' + category + ' [' + h_state + ']'
        sublists.add(s)
        # Make M-factor field (though not really using it for anything now).
        if chemsheet.cell_value(r, 9) != '':
            m_factor = str(int(chemsheet.cell_value(r, 9)))
        else:
            m_factor = ''
        # Ensure one CASRN per line when writing output:
        for casrn in casrn_field.split(', '):
            listwriter.writerow([casrn] + names + [s, m_factor])
    outfile.close()
    # Output some helpful information about the hazard sublists.
    with open(os.path.join(_KR_RESULTS_PATH, 'sublists.txt'), 'w') as subtxt:
        for sub in sorted(sublists):
            print(sub, file=subtxt)


def extract_nz():
    # Process the HSNO CCID export.
    # Translate HSNO classifications into GHS classifications, and perform
    # some additional processing to filter out certain substances.
    hsno_ghs = {
                # These are GHS translations of the HSNO classes/categories,
                # used to create a 'Hazard description' field.
                '1.1': ['Explosives', 'Division 1.1'],
                '1.2': ['Explosives', 'Division 1.2'],
                '1.3': ['Explosives', 'Division 1.3'],
                '1.4': ['Explosives', 'Division 1.4'],
                '1.5': ['Explosives', 'Division 1.5'],
                '1.6': ['Explosives', 'Division 1.6'],
                '2.1.1A': ['Flammable gases', 'Category 1'],
                '2.1.1B': ['Flammable gases', 'Category 2'],
                '2.1.2A': ['Flammable aerosols', 'Category 1'],
                '3.1A': ['Flammable liquids', 'Category 1'],
                '3.1B': ['Flammable liquids', 'Category 2'],
                '3.1C': ['Flammable liquids', 'Category 3'],
                '3.1D': ['Flammable liquids', 'Category 4'],
                '4.1.1A': ['Flammable solids', 'Category 1'],
                '4.1.1B': ['Flammable solids', 'Category 2'],
                '4.1.2A': ['Self-reactive substances and mixtures', 'Type A'],
                '4.1.2B': ['Self-reactive substances and mixtures', 'Type B'],
                '4.1.2C': ['Self-reactive substances and mixtures', 'Type C'],
                '4.1.2D': ['Self-reactive substances and mixtures', 'Type D'],
                '4.1.2E': ['Self-reactive substances and mixtures', 'Type E'],
                '4.1.2F': ['Self-reactive substances and mixtures', 'Type F'],
                '4.1.2G': ['Self-reactive substances and mixtures', 'Type G'],
                # HSNO doesn't distinguish pyrophoric liquids and solids.
                '4.2A': ['Pyrophoric substances', 'Category 1'],
                '4.2B': ['Self-heating substances and mixtures', 'Category 1'],
                '4.2C': ['Self-heating substances and mixtures', 'Category 2'],
                '4.3A': ['Substances and mixtures, which in contact with water, emit flammable gases', 'Category 1'],
                '4.3B': ['Substances and mixtures, which in contact with water, emit flammable gases', 'Category 2'],
                '4.3C': ['Substances and mixtures, which in contact with water, emit flammable gases', 'Category 3'],
                # HSNO doesn't distinguish between oxidizing liquids and solids 
                # but does distinguish them from oxidizing gases.
                '5.1.1A': ['Oxidizing liquids/solids', 'Category 1'],
                '5.1.1B': ['Oxidizing liquids/solids', 'Category 2'],
                '5.1.1C': ['Oxidizing liquids/solids', 'Category 3'],
                '5.1.2A': ['Oxidizing gases', 'Category 1'],
                '5.2A': ['Organic peroxides', 'Type A'],
                '5.2B': ['Organic peroxides', 'Type B'],
                '5.2C': ['Organic peroxides', 'Type C'],
                '5.2D': ['Organic peroxides', 'Type D'],
                '5.2E': ['Organic peroxides', 'Type E'],
                '5.2F': ['Organic peroxides', 'Type F'],
                '5.2G': ['Organic peroxides', 'Type G'],
                '6.1A (dermal)': ['Acute toxicity: Dermal', 'Category 1'],
                '6.1A (inhalation)': ['Acute toxicity: Inhalation', 'Category 1'],
                '6.1A (oral)': ['Acute toxicity: Oral', 'Category 1'],
                '6.1B (dermal)': ['Acute toxicity: Dermal', 'Category 2'],
                '6.1B (inhalation)': ['Acute toxicity: Inhalation', 'Category 2'],
                '6.1B (oral)': ['Acute toxicity: Oral', 'Category 2'],
                '6.1C (dermal)': ['Acute toxicity: Dermal', 'Category 3'],
                '6.1C (inhalation)': ['Acute toxicity: Inhalation', 'Category 3'],
                '6.1C (oral)': ['Acute toxicity: Oral', 'Category 3'],
                '6.1D (dermal)': ['Acute toxicity: Dermal', 'Category 4'],
                '6.1D (inhalation)': ['Acute toxicity: Inhalation', 'Category 4'],
                '6.1D (oral)': ['Acute toxicity: Oral', 'Category 4'],
                '6.1E (dermal)': ['Acute toxicity: Dermal', 'Category 5'],
                '6.1E (inhalation)': ['Acute toxicity: Inhalation', 'Category 5'],
                '6.1E (oral)': ['Acute toxicity: Oral', 'Category 5'],
                '6.3A': ['Skin corrosion/irritation', 'Category 2'],
                '6.3B': ['Skin corrosion/irritation', 'Category 3'],
                # 6.4A is both Category 2A and 2B.
                '6.4A': ['Serious eye damage/eye irritation', 'Category 2'],
                '6.5A (respiratory)': ['Respiratory sensitization', 'Category 1'],
                '6.5B (contact)': ['Skin sensitization', 'Category 1'],
                # 6.6A is both Category 1A and 1B.
                '6.6A': ['Germ cell mutagenicity', 'Category 1'],
                '6.6B': ['Germ cell mutagenicity', 'Category 2'],
                # 6.7A is both Category 1A and 1B.
                '6.7A': ['Carcinogenicity', 'Category 1'],
                '6.7B': ['Carcinogenicity', 'Category 2'],
                # 6.8A is both Category 1A and 1B.
                '6.8A': ['Reproductive toxicity', 'Category 1'],
                '6.8B': ['Reproductive toxicity', 'Category 2'],
                '6.8C': ['Reproductive toxicity', 'Effects on or via lactation'],
                # HSNO doesn't distinguish between single or repeated exposure,
                # but does distinguish among exposure routes.
                '6.9A (dermal)': ['Specific Target Organ Systemic Toxicity', 'Category 1'],
                '6.9A (inhalation)': ['Specific Target Organ Systemic Toxicity', 'Category 1'],
                '6.9A (oral)': ['Specific Target Organ Systemic Toxicity', 'Category 1'],
                '6.9A (other)': ['Specific Target Organ Systemic Toxicity', 'Category 1'],
                '6.9B (dermal)': ['Specific Target Organ Systemic Toxicity', 'Category 2'],
                '6.9B (inhalation)': ['Specific Target Organ Systemic Toxicity', 'Category 2'],
                '6.9B (oral)': ['Specific Target Organ Systemic Toxicity', 'Category 2'],
                '6.9B (other)': ['Specific Target Organ Systemic Toxicity', 'Category 2'],
                '8.1A': ['Corrosive to metals', 'Category 1'],
                '8.2A': ['Skin corrosion/irritation', 'Category 1A'],
                '8.2B': ['Skin corrosion/irritation', 'Category 1B'],
                '8.2C': ['Skin corrosion/irritation', 'Category 1C'],
                '8.3A': ['Serious eye damage/eye irritation', 'Category 1'],
                # In 9.1A, HSNO doesn't distinguish between acute and chronic.
                '9.1A (algal)': ['Aquatic toxicity (Acute or Chronic)', 'Category 1'],
                '9.1A (crustacean)': ['Aquatic toxicity (Acute or Chronic)', 'Category 1'],
                '9.1A (fish)': ['Aquatic toxicity (Acute or Chronic)', 'Category 1'],
                '9.1A (other)': ['Aquatic toxicity (Acute or Chronic)', 'Category 1'],
                '9.1B (algal)': ['Aquatic toxicity (Chronic)', 'Category 2'],
                '9.1B (crustacean)': ['Aquatic toxicity (Chronic)', 'Category 2'],
                '9.1B (fish)': ['Aquatic toxicity (Chronic)', 'Category 2'],
                '9.1B (other)': ['Aquatic toxicity (Chronic)', 'Category 2'],
                '9.1C (algal)': ['Aquatic toxicity (Chronic)', 'Category 3'],
                '9.1C (crustacean)': ['Aquatic toxicity (Chronic)', 'Category 3'],
                '9.1C (fish)': ['Aquatic toxicity (Chronic)', 'Category 3'],
                '9.1C (other)': ['Aquatic toxicity (Chronic)', 'Category 3'],
                # The mapping of 9.1D to GHS is very odd.
                '9.1D (algal)': ['Aquatic toxicity', 'Category 2-3 (Acute) or Category 4 (Chronic)'],
                '9.1D (crustacean)': ['Aquatic toxicity', 'Category 2-3 (Acute) or Category 4 (Chronic)'],
                '9.1D (fish)': ['Aquatic toxicity', 'Category 2-3 (Acute) or Category 4 (Chronic)'],
                '9.1D (other)': ['Aquatic toxicity', 'Category 2-3 (Acute) or Category 4 (Chronic)'],
                # Classes that aren't GHS-translatable:
                '3.2A': '', # Liquid desensitized explosives
                '3.2B': '', # Liquid desensitized explosives
                '3.2C': '', # Liquid desensitized explosives
                '4.1.3A': '', # Solid desensitized explosives: high hazard
                '4.1.3B': '', # Solid desensitized explosives: medium hazard
                '4.1.3C': '', # Solid desensitized explosives: low hazard
                '9.2A': '', # Ecotoxic to soil environment
                '9.2B': '', # Ecotoxic to soil environment
                '9.2C': '', # Ecotoxic to soil environment
                '9.2D': '', # Ecotoxic to soil environment
                '9.3A': '', # Ecotoxic to terrestrial vertebrates
                '9.3B': '', # Ecotoxic to terrestrial vertebrates
                '9.3C': '', # Ecotoxic to terrestrial vertebrates
                '9.4A': '', # Ecotoxic to terrestrial invertebrates
                '9.4B': '', # Ecotoxic to terrestrial invertebrates
                '9.4C': '', # Ecotoxic to terrestrial invertebrates
                }
    NZ_DATA_PATH = os.path.join(DATA_PATH, 'nz')
    NZ_RESULTS_PATH = os.path.join(RESULTS_PATH, 'nz')
    ccidbook = xlrd.open_workbook(os.path.join(NZ_DATA_PATH, # WHAT FILENAME?
                                  'CCID Key Studies (4 June 2013).xls'))
    ccid = ccidbook.sheet_by_index(0)
    # Initialize a dictionary of CASRN-identified chemicals. See below...
    chemicals = dict()
    # Also, enumerate the unique classifications (sublists).
    sublists = dict()
    # Read in the spreadsheet and generate GHS translations.
    for r in range(1, ccid.nrows):
        # CASRN                 (r, 0)
        # Substance name        (r, 1)
        # Approval              (r, 2) - ignored
        # Classification Text   (r, 3)
        # Classification Code   (r, 4)
        # Key Study             (r, 5)
        casrn = str(ccid.cell_value(r, 0)).strip()
        # There is conveniently one substance without a CASRN. If there were
        # more, it might pose a problem for the redundancy filtering (below).
        if casrn == '':
            casrn = 'no_id'
        name = ccid.cell_value(r, 1).strip()
        # The following needs to be known for every substance:
        c = str(ccid.cell_value(r, 4))  # Classification code
        k = str(ccid.cell_value(r, 5))  # Key study
        # Fix inconsistent spaces around punctuation (for style):
        if '(' in c:
            c = c[:c.index('(')].strip() + ' ' + c[c.index('('):].strip()
        # Keep track of what classifications actually show up in the dataset,
        # and store them in a dict where the keys are classification codes.
        if c not in sublists:
            # Tidy up classification text:
            t = ccid.cell_value(r, 3)
            if ':' in t:
                t = t[:t.index(':')].strip() + ': ' + \
                    t[t.index(':')+1:].strip()
            # I also want to combine classification codes and text, e.g.
            #   "3.1D - Flammable Liquids: low hazard"
            s = c + ' - ' + t
            # Find the appropriate GHS translation, if any.
            if hsno_ghs[c] != '':
                # For my purposes I want it to say 'GHS: ' at the beginning.
                g = 'GHS: ' + hsno_ghs[c][0] + ' - ' + hsno_ghs[c][1]
            else:
                g = ''
            sublists[c] = [s, t, g]
        # Now put the chemical classifications into a convoluted data 
        # structure from which we can filter out redundant variants.
        # In the dictionary chemicals, each key is a CASRN, and each 
        # corresponding value is itself a dictionary. The keys of that dict
        # are all the different chemical names assigned to that CASRN.
        # The values for those keys will be dictionaries (!) where the keys
        # are classification codes and the values are key study summaries. 
        if casrn not in chemicals:
            chemicals[casrn] = {name: {c: k}}
        elif name not in chemicals[casrn]:
            chemicals[casrn][name] = {c: k}
        elif c in chemicals[casrn][name]:
            chemicals[casrn][name][c] = chemicals[casrn][name][c] + '\n' + k
        else: 
            chemicals[casrn][name][c] = k
    # Create output files...
    outfile_inc = open(os.path.join(NZ_RESULTS_PATH, 'GHS-nz.csv'), 'w')
    outfile_var = open(os.path.join(NZ_RESULTS_PATH, 'variants.csv'), 'w')
    outfile_exc = open(os.path.join(NZ_RESULTS_PATH, 'exclude.csv'), 'w')
    writer_inc = csv.writer(outfile_inc)
    writer_var = csv.writer(outfile_var)
    writer_exc = csv.writer(outfile_exc)
    header = ['CASRN', 'Substance name', 'HSNO code',
              'HSNO classification text', 'GHS translation', 'Key study']
    writer_inc.writerow(header)
    writer_var.writerow(header)
    writer_exc.writerow(header)
    # The following section attempts to filter the list so that pure
    # substances, solutions, and 'redundant' solutions are output in separate
    # files. This is done for practical reasons, to avoid minting hundreds of
    # identifiers for differently-dilute solutions of the same chemical.
    for casrn in sorted(chemicals.keys()):
        # The list of names given to this CASRN:
        names = sorted(chemicals[casrn].keys())
        # Find the principal (definitely non-redundant) substance from the 
        # list of names. If they all contain %, then there's no pure substance.
        # If there are multiple names which do not contain %, then all but one
        # of those will end up in the redundant list. So far, the only such
        # case is a substance that seems redundant anyway.
        p = -1
        for i in range(len(names)):
            if '%' not in names[i]:
                p = i
                break
        # If we didn't find any pure substances, assume they are all 
        # potentially non-redundant; output and continue to next CASRN.
        if p == -1:
            for j in range(len(names)):
                thisclass = chemicals[casrn][names[j]]
                for c in sorted(thisclass.keys()):
                    writer_var.writerow(
                        ['_v' + str(j) + '_' + casrn, names[j], c] + 
                         sublists[c][1:] + [thisclass[c]])
            continue
        # Having found the principal substance, pop it out of the list of
        # names, save its set of classifications, and output them.
        pname = names.pop(p)
        pclass = chemicals[casrn][pname]
        pset = pclass.keys()
        for c in sorted(pset):
            writer_inc.writerow(
                [casrn, pname, c] + sublists[c][1:] + [pclass[c]])
        # Next, screen the rest of the named substances against the principal.
        # Since these all should be variants of the principal substance, I'll
        # add a flag to the CASRN field to help with identifier wrangling.
        for n in range(len(names)):
            thisclass = chemicals[casrn][names[n]]
            thisset = set(thisclass.keys())
            if thisset <= pset:
                # Redundant: All classifications are included within the
                # principal substance's classifications.
                for c in sorted(thisset):
                    writer_exc.writerow(
                        ['_v' + str(n) + '_' + casrn, names[n], c] + 
                         sublists[c][1:] + [thisclass[c]])
            else:
                # Not redundant, but set aside for further scrutiny.
                for c in sorted(thisset):
                    writer_var.writerow(
                        ['_v' + str(n) + '_' + casrn, names[n], c] + 
                         sublists[c][1:] + [thisclass[c]])
    outfile_inc.close()
    outfile_var.close()
    outfile_exc.close()
    # Output some helpful information about the classification sublists.
    subs = sorted(sublists.keys())
    subfile = open(os.path.join(NZ_RESULTS_PATH, 'sublists.csv'), 'w')
    subwriter = csv.writer(subfile)
    subwriter.writerow(['HSNO code', 'HSNO classification', 'GHS translation'])
    for sl in subs:
        subwriter.writerow([sl] + [sublists[sl][0], sublists[sl][2]])
    subfile.close()


def main():
    parser = argparse.ArgumentParser(description='Extract GHS hazard \
                classifications from country-specific documents.') 
    parser.add_argument('countries', action='store', nargs='+', 
                choices=['jp', 'kr', 'nz'], 
                help='Process GHS classifications from these countries.')
    args = parser.parse_args()
    if 'jp' in args.countries:
        print('Processing Japan GHS classifications.')
        extract_jp()
    if 'kr' in args.countries:
        print('Processing Republic of Korea GHS classifications.')
        extract_kr()
    if 'nz' in args.countries:
        print('Processing Aotearoa New Zealand HSNO classifications.')
        extract_nz()


if __name__ == '__main__':
    main()
