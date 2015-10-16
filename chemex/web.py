# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import urllib.request
from urllib.error import HTTPError
import requests
from time import sleep
import lxml
from lxml.html import parse

# ChemIDplus

idplus_base_rn = 'http://chem.sis.nlm.nih.gov/chemidplus/rn/'

def idplus_heading_by_casrn(rn):
    '''Get the name, CASRN, UNII, and InChIKey of a chemical from ChemIDplus
    for a given CASRN.'''
    data = None
    try:
        r = urllib.request.urlopen(idplus_base_rn + rn)
        parsed = parse(r)
        doc = parsed.getroot()
        heading = doc.find('.//h1')
        name = heading.text.split('\xa0')[1]
        ids = [e.text.split('\xa0')[1] for e in heading if e.text is not None]
        keys = ['Name', 'CASRN', 'UNII', 'InChIKey']
        data = dict(zip(keys, [name] + ids))
    except HTTPError as e:
        print('{0}: {1}.'.format(rn, e))
    return data


# PubChem

pc_rest_base = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/'
pc_base = 'https://pubchem.ncbi.nlm.nih.gov/'

def pc_img_html(cid, size=300):
    return '<img src="{0}compound/cid/{1}/PNG?image_size=large" width="{2}" height="{2}">'.format(pc_rest_base, cid, size)

def pc_img_link_html(cid, size=300):
    return '<a href="{0}compound/{1}" target="_blank"><img src="https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{0}/PNG?image_size=large" width="{2}" height="{2}"></a>'.format(pc_base, cid, size)