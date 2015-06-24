# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from chemex.casrn import validate, find_valid

def test_casrn_with_extra_junk():
    assert validate('50-–00—0', boolean=True) == True
    # The string contains dash, n-dash, and m-dash.

def test_casrn_with_leading_space():
    assert validate(' 50-55-5', boolean=True) == True

def test_casrn_with_trailing_space():
    assert validate('881685-58-1 ', boolean=True) == True

def test_casrn_format():
    assert validate('113852-37-2') == u'113852-37-2'

def test_find_no_casrn():
    assert find_valid('this string has no casrn in it') == []

def test_find_one_casrn():
    assert find_valid('this string has 50-00-0') == [u'50-00-0']

def test_find_one_valid_casrn():
    assert find_valid('this string has 50-00-0 and 50-00-1') == [u'50-00-0']

def test_find_two_casrns():
    assert find_valid('there are 50-00-0 and 71-43-2') == [u'50-00-0', u'71-43-2']
