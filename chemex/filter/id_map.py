# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import os
import json
import time
#import codecs
#import string
from collections import OrderedDict
from threading import RLock
import pandas as pd
from pandas import DataFrame
#from ..apis import *
from ..casrn import validate


# Based on link_map.py from Erosion

class _synchronized(object):

    def __init__(self, lock, func):
        self.lock = lock
        self.func = func

    def __call__(self, *args, **kwargs):
        with self.lock:
            return self.func(*args, **kwargs)

    def __get__(self, obj, type_=None):
        if obj is None:
            return self
        return self.__class__(self.lock,
                              self.func.__get__(obj, type))

def synchronized(lock):
    return lambda func: _synchronized(lock, func)

LOCK = RLock()

# Start: 
#   import data from file...
#   - one DataFrame with columns (index), 'CASRN', 'CID', 'status'
#   - another DataFrame associating key identifiers with trusted names
# 
# Initialize something that loops through groupby('CASRN')
#   and for each group, displays widgets allowing user to set 'status'
#   or move to next group
# Values of status: 'accepted', 'rejected'
# 
#
# Finish:
#   add lines to json file


class IDMap(object):
    def __init__(self, path):
        self.path = path
        entries = _load_entries_from_file(path)
        self.link_map = OrderedDict([(e.alias, e) for e in entries])

    @synchronized(LOCK)
    def add_entry(self, target, alias=None, expiry=None, max_count=None):
        next_id = self._get_next_id()
        if not alias:
            alias = id_encode(next_id)
        if alias in self.link_map:
            raise ValueError('alias already in use %r' % alias)
        expire_time = self._get_expiry_time(expiry)

        entry = LinkEntry(next_id, target, alias, expire_time, max_count)
        self.link_map[entry.alias] = entry
        return entry

    def _get_expiry_time(self, expire_interval_name):
        expire_interval_name = expire_interval_name or _DEFAULT_EXPIRY
        expiry_seconds = _EXPIRY_MAP[expire_interval_name]
        if expiry_seconds is _NEVER:
            expiry_time = None
        else:
            cur_time = time.time()
            expiry_time = int(cur_time + expiry_seconds)
        return expiry_time

    def _get_next_id(self):
        try:
            last_alias = next(reversed(self.link_map))
            last_id = self.link_map[last_alias].link_id
        except:
            last_id = 41660
        return last_id + 1

    @synchronized(LOCK)
    def get_entry(self, alias, enforce=True):
        ret = self.link_map[alias]
        if enforce:
            if ret.max_count <= ret.count or ret.expiry_time < time.time():
                raise ValueError()
        return ret

    @synchronized(LOCK)
    def use_entry(self, alias):
        try:
            ret = self.get_entry(alias)
        except:
            return None
        ret.count += 1
        return ret

    @synchronized(LOCK)
    def save(self):
        # TODO: high-water mark appending
        with open(self.path, 'w') as f:
            for alias, entry in self.link_map.iteritems():
                entry_json = json.dumps(entry.to_dict())
                f.write(entry_json)
                f.write('\n')
        # sync


@synchronized(LOCK)
def _load_entries_from_file(path):
    ret = []
    if not os.path.exists(path):
        return ret
    with codecs.open(path, 'r', 'utf-8') as f:
        for line in f:
            entry_dict = json.loads(line)
            ret.append(LinkEntry.from_dict(entry_dict))
    return ret


####

class CASRN_CID_Align():

    def __init__(self, known_df, data_df):
        self.known_df = known_df # DataFrame of names INDEXED by known IDs
        self.data_df = data_df   # DataFrame of multiple possible ID correlations

    def run(self):
        for known_id, group in self.data_df.groupby('CASRN'):
            status = {x: [group.loc[x,'CID'], group.loc[x,'status']] for x in group.index}

            for x in group.index:
                    self.data_df.loc[x, 'status'] = new_status[x][1]

    # def write_data_df(self): ...

    def accept(self, x):
        self.new_ids[x]['status'] = 'accepted'
        return self.new_ids

    def reject(self, x):
        self.new_ids[x]['status'] = 'rejected'
        return self.new_ids

    def idk_next(self):
        return self.new_ids
        self.erase()

