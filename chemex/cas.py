# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import numpy as np


def casrn_numeric(casrn):
    '''
    Take a string or int representation of a CASRN and return only the numbers
    as a NumPy ndarray.
    '''
    z = set('0123456789')
    y = list(str(casrn))
    return np.array([int(i) for i in y if i in z])
    # There should be a way to do this with regex instead of NumPy: 
    # something like match(/([0-9]{2,7})-([0-9]{2})-[0-9]/)
    # except the '-' are not always the same

def casrn_valid(casrn):
    '''
    Check the validity of a CAS registry number by calculating the check digit
    and comparing it with the final given digit.

    Argument may be an ndarray output from casrn_numeric, or a string or int
    representation. Non-numeric characters are automatically ignored. Based on
    CAS documentation: https://www.cas.org/content/chemical-substances/checkdig
    '''
    if type(casrn) == np.ndarray and casrn.dtype == int:
        pass
    else:
        casrn = casrn_numeric(casrn)
    if len(casrn) < 5:
        return False
    else:
        last_digit = casrn[-1]
        check_digit = sum(casrn[:-1] * np.arange(1, len(casrn))[::-1]) % 10
        return check_digit == last_digit


def casrn_format(casrn):
    '''
    Check the validity of a CAS registry number and return the number as a
    properly hyphenated string if valid, otherwise return None.

    Argument may be an ndarray output from casrn_numeric, or a string or int
    representation. Non-numeric characters are automatically ignored.
    '''
    if type(casrn) == np.ndarray and casrn.dtype == int:
        pass
    else:
        casrn = casrn_numeric(casrn)
    if casrn_valid(casrn):
        n = ''.join([str(x) for x in casrn])
        return '-'.join([n[:-3], n[-3:-1], n[-1:]])
    else:
        return None
