# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
import numpy as np
from builtins import str # now str() and unicode() do the same thing

def validate(casrn, boolean=False):
    '''
    Check the validity of a CASRN using the check digit. Returns cleaned CASRN
    as unicode, or None if invalid. If boolean=True, returns True or False.

    Input can be str, unicode, or int. Non-numeric characters are ignored. 
    Based on CAS documentation: 
        https://www.cas.org/content/chemical-substances/checkdig
    '''
    casrn = str(casrn)
    p = re.compile(r'\d+')
    n = ''.join(p.findall(casrn))

    if len(n) < 5:
        valid = False
    else:
        digits = np.array([int(i) for i in n]) 
        check_digit = sum(digits[:-1] * np.arange(1, len(n))[::-1]) % 10
        valid = (check_digit == digits[-1])

    if boolean:
        return valid
    else:
        return '-'.join([n[:-3], n[-3:-1], n[-1:]]) if valid else None
