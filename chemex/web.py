# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import requests
from bs4 import BeautifulSoup

# ChemIDplus

idplus_base_rn = 'http://chem.sis.nlm.nih.gov/chemidplus/rn/'

def idplus_heading_by_casrn(rn):
    '''Get the name, CASRN, UNII, and InChIKey of a chemical from ChemIDplus
    for a given CASRN, if available.'''
    try:
        r = requests.get(idplus_base_rn + rn)
        r.raise_for_status()
    except Exception as e:
        print(e)
        return None
    data = dict()
    doc = BeautifulSoup(r.text, 'lxml')
    name = doc.h1.contents[0].split(':\xa0')[1]
    data.update({'Name': name})
    ids = dict([t.text.split(':\xa0') for t in doc.h1.find_all('span')])
    data.update(ids)
    return data

# EPI Suite output

def dict_from_line(txt, sep=':'):
    d = [s.strip() for s in txt.split(sep, 1)]
    return {d[0]: d[1]}

def epi_suite_values(epi_str):
    data = dict()
    lines = epi_str.split('\n')
    for i in lines:
        j = i.strip()
        if j.startswith('Log Kow (') or j.startswith('Log BCF'):
            data.update(dict_from_line(i, '='))
        if j.startswith('Henrys LC') or\
            j.startswith('Log Koa (KOAWIN') or\
            j.startswith('Log Koa (experimental') or\
            j.startswith('Persistence Time') or\
            j.startswith('Ready Biodegradability Prediction'):
            data.update(dict_from_line(i))
    return data

# ChemSpider

def cs_scrape_properties(csid):
    '''Retrieve some of the experimental and predicted chemical properties that
    are not surfaced in the ChemSpider web API.'''
    try:
        r = requests.get('http://www.chemspider.com/Chemical-Structure.{0}.html'.format(csid))
        r.raise_for_status()
    except Exception as e:
        print(e)
        return None
    data = dict()
    doc = BeautifulSoup(r.text, 'lxml')
    # Experimental and predicted properties ("Experimental data" tab):
    props = doc.find_all(class_='user_data_property_name')
    for p in props:
        prop_name = p.get_text().strip(':')
        data.update({prop_name: []})
        li = p.find_parent('li')
        if li:
            values = li.find_all('td')
            for v in values:
                x = v.get_text().strip(' \r\n')
                data[prop_name].append(x)
    # EPI Suite results, as a blob to process later:
    #   Sometimes only returns part of the text, for some reason.
    epi_tab = doc.find(id='epiTab')
    epi_str = epi_tab.get_text() if epi_tab else None
    data.update({'EPI Suite': epi_str})
    # ACD Labs predicted properties:
    # acd_tab = doc.find(id='acdLabsTab')
    # if acd_tab:
    #     pass # ...
    return data

# PubChem

pc_rest_base = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/'
pc_base = 'https://pubchem.ncbi.nlm.nih.gov/'

def pc_img_html(cid, size=300):
    return '<img src="{0}compound/cid/{1}/PNG?image_size=large" width="{2}" height="{2}">'.format(pc_rest_base, cid, size)

def pc_img_link_html(cid, size=300):
    return '<a href="{0}compound/{1}" target="_blank">{2}</a>'.format(pc_base, cid, pc_img_html(cid, size))


# UniChem
# https://www.ebi.ac.uk/unichem/info/webservices

