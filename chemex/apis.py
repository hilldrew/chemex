# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import requests
from time import sleep

# PubChem PUG REST API

pc_api_base = 'http://pubchem.ncbi.nlm.nih.gov/rest/pug/'

# Properties
# Some available properties that might be useful for identification purposes:
    # MolecularFormula
    # MolecularWeight
    # CanonicalSMILES
    # IsomericSMILES
    # InChI
    # InChIKey
    # IUPACName
    # Charge

pc_default_props = 'IUPACName,MolecularFormula,InChI,InChIKey'

# The following functions are for getting info about a compound identified by CID.
# Also, we're using the dict data structure that comes from the JSON
# to store information about the compound. 
#   i.e. data[CID] will contain other dicts...

def pc_get_cid_properties(data, properties=pc_default_props):
    r = requests.get(pc_api_base + 'compound/CID/{0}/property/{1}/JSON'
                     .format(data['CID'], properties)).json()
    data.update(r['PropertyTable']['Properties'][0])
    return data

# Synonyms
# To my knowledge, can't get synonyms in the same API request as compound properties.
def pc_get_cid_synonyms(data):
    r = requests.get(pc_api_base + 'compound/CID/{0}/synonyms/JSON'
                     .format(data['CID'])).json()
    data.update(r['InformationList']['Information'][0])
    return data

# Title and description
# To my knowledge, can't get these in the same API request as compound properties.
def pc_get_cid_title(data):
    r = requests.get(pc_api_base + 'compound/CID/{0}/description/JSON'
                     .format(data['CID'])).json()
    data.update(r['InformationList']['Information'][0])
    # Note: r['InformationList']['Information'][1] contains 'Description',
    # 'DescriptionSourceName', and 'DescriptionURL'.
    return data

def pc_img_html(cid, size=300):
    return '<img src="https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{0}/PNG?image_size=large" width="{1}" height="{1}">'.format(cid, size)

def pc_img_link_html(cid, size=300):
    return '<a href="https://pubchem.ncbi.nlm.nih.gov/compound/{0}" target="_blank"><img src="https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{0}/PNG?image_size=large" width="{1}" height="{1}"></a>'.format(cid, size)

# Direct lookup of a CASRN
def pc_casrn_cid_lookup(rn, properties=pc_default_props, verbose=False):
    rn = cx.cas.casrn_format(rn)
    if verbose:
        print(rn)
    results = []
    # CASRN-to-CIDs lookup using PubChem API.
    while True:
        try:
            r = requests.get('http://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/xref/RN/{0}/JSON'
                             .format(rn)).json()
        except ConnectionError as e:
            if verbose:
                print('Connection error while requesting CIDs for CASRN {0}: {1}'
                      .format(rn, e))
                print('Trying again...')
            sleep(15)
            continue
        else:
            break
    # Wait before making the next API call -- not sure if this is necessary.
    sleep(0.1)
    # Add all CIDs (if any) to the results & look up additional properties.
    try:
        cpds = r['PC_Compounds']
    except KeyError as e:
        if verbose:
            print('No data for CASRN {0}: {1}'.format(rn, e))
        results.append({'CASRN': rn})
    else:
        for c in cpds:
            data = {'CASRN': rn, 'CID': c['id']['id']['cid']}
            # Retrieve the desired properties, if any.
            if properties:
                data = pc_get_cid_properties(data, verbose=verbose)
            results.append(data)
    return results
