# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import os
import sys
_CUR_PATH = os.path.dirname(os.path.abspath(__file__))
_PARENT_PATH = os.path.dirname(_CUR_PATH)
sys.path.append(_PARENT_PATH)
_DATA_PATH = os.path.join(_PARENT_PATH, 'data', 'ghscrunch', 'jp')
import lxml
from lxml.html import parse
import urllib
import urllib2

def main():
    urlbase = 'http://www.safe.nite.go.jp/english/ghs/' 
    r = urllib2.urlopen(urlbase + 'ghs_download.html')
    parsed = parse(r)
    doc = parsed.getroot()
    links = [lnk.get('href') for lnk in doc.findall('.//a')]
    xlnks = [k for k in links if 'xls' in k]
    new_lnks = [k for k in xlnks if 'rev' not in k]
    rev_lnks = [k for k in xlnks if 'rev' in k]

    NEW_PATH = os.path.join(_DATA_PATH, 'new')
    REV_PATH = os.path.join(_DATA_PATH, 'rev')

    for k in new_lnks:
        filename = k.split('/')[-1]
        urllib.urlretrieve(urlbase + k, os.path.join(NEW_PATH, filename))
        print('NEW:', filename)

    for k in rev_lnks:
        filename = k.split('/')[-1]
        urllib.urlretrieve(urlbase + k, os.path.join(REV_PATH, filename))
        print('REV:', filename)

if __name__ == '__main__':
    main()