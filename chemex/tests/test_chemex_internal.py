# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import chemex
from chemex.casrn import validate

def test_casrn_with_extra_junk():
    assert validate('50-–00—0', boolean=True) == True
    # The string contains dash, n-dash, and m-dash.

def test_casrn_with_leading_space():
    assert validate(' 50-55-5', boolean=True) == True

def test_casrn_with_trailing_space():
    assert validate('881685-58-1 ', boolean=True) == True

def test_casrn_format():
    assert validate('113852-37-2') == u'113852-37-2'
