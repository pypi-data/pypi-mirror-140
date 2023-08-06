#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import json
import pathlib
import sys
import signal
import threading


def load(file, serializer=json, auto_dump=True, sig=True):
    return SerializeDB(file, serializer, auto_dump, sig)

OPERATED = True

class SerializeDB(object):

    def __init__(self, file, serializer=json, auto_dump=True, sigterm=True):
        self.file = file
        self.serializer = serializer
        self.auto_dump = auto_dump
        self.sigterm = sigterm
        self.db = None
        self.dump_thread = None
        self._autoload()
        self._set_sigterm_handler()

    def __len__(self):
        return len(self.db)

    def __setitem__(self, key, value):
        return self.set(key, value)

    def __getitem__(self, key):
        return self.get(key)

    def __delitem__(self, key):
        return self.rem(key)

    def __iter__(self):
        return self.db

    def _autoload(self):
        self.file = pathlib.Path(self.file)
        if self.file.exists():
            try:
                with open(self.file, 'rt') as f:
                    self.db = self.serializer.load(f)
            except:
                if not self.file.stat().st_size == 0:
                    raise ValueError
        self.db = dict() if self.db is None else self.db

    def _set_sigterm_handler(self):
        def sigterm_handler():
            if self.dump_thread is not None:
                self.dump_thread.join(timeout=None)
            sys.exit(0)
        if self.sigterm:
            signal.signal(signal.SIGTERM, sigterm_handler)

    def _autodump(self):
        if self.auto_dump:
            return self.dump()

    def dump(self):
        self.serializer.dump(self.db, open(self.file, 'wt'))
        self.dump_thread = threading.Thread(
            target=self.serializer.dump,
            args=(self.db, open(self.file, 'wt'),),
            daemon=True,
        )
        self.dump_thread.start()
        self.dump_thread.join(timeout=None)
        return OPERATED

    def setdefault(self, key, default):
        self.db[key] = default
        self._autodump()
        return OPERATED

    def set(self, key, value):
        '''Set the str value of a key'''
        self.db[key] = value
        self._autodump()
        return OPERATED

    def get(self, key, default=None):
        '''Get the value of a key'''
        if not self.exists(key):
            return default
        return self.db[key]

    def copy(self, key):
        if not self.exists(key):
            return None
        return copy.deepcopy(self.db[key])

    def exists(self, key):
        '''Determine if a key exists'''
        return key in self.db

    def keys(self):
        '''Get all keys'''
        return list(self.db.keys())

    def rem(self, key):
        '''Remove a key'''
        if not self.exists(key):
            return None
        value = self.db.pop(key)
        self._autodump()
        return value

    def flush(self):
        '''flush all'''
        self.db.clear()
        self._autodump()
        return OPERATED

    def lcreate(self, key):
        '''Create a list'''
        if self.exists(key):
            return not OPERATED
        self.setdefault(key, [])
        return OPERATED

    def rpush(self, key, element):
        '''Append an element to a list'''
        l = self.get(key)
        if not isinstance(l, list):
            return not OPERATED
        l.append(element)
        self._autodump()
        return OPERATED

    def lpush(self, key, element):
        '''Prepend an element to a list'''
        return self.linsert(key, 0, element)

    def linsert(self, key, index, element):
        '''Insert an element in a list by its index'''
        l = self.get(key)
        if not isinstance(l, list):
            return not OPERATED
        l.insert(index, element)
        self._autodump()
        return OPERATED

    def lindex(self, key, index):
        '''Get an element from a list by its index'''
        l = self.get(key)
        if not isinstance(l, list):
            return None
        try:
            return l[index]
        except:
            return []

    def lrange(self, key, start=None, stop=None):
        '''Get a range of elements from a list'''
        l = self.get(key)
        if not isinstance(l, list):
            return None
        return l[start:stop]

    def lempty(self, key):
        '''Determine if a list is empty'''
        if self.llen(key) is None:
            return None
        return self.llen(key) == 0

    def llen(self, key):
        '''Get the length of a list'''
        l = self.get(key)
        if not isinstance(l, list):
            return None
        return len(l)

    def lset(self, key, index, element):
        '''Set the value of an element in a list by its index'''
        l = self.get(key)
        if not isinstance(l, list) or index > len(l) - 1:
            return not OPERATED
        l[index] = element
        self._autodump()
        return OPERATED

    def rpop(self, key):
        '''Remove and get the last element in a list'''
        l = self.get(key)
        if not isinstance(l, list) or len(l) == 0:
            return None
        element = l.pop()
        self._autodump()
        return element

    def lpop(self, key):
        '''Remove and get the first element in a list'''
        return self.lrem(key, 0)

    def lrem(self, key, index):
        '''Remove and get an element in a list by its index'''
        l = self.get(key)
        if not isinstance(l, list) or index > len(l) - 1:
            return None
        element = l.pop(index)
        self._autodump()
        return element

    def lclear(self, key):
        '''Remove all in a list'''
        l = self.get(key)
        if not isinstance(l, list):
            return not OPERATED
        l.clear()
        self._autodump()
        return OPERATED

    def dcreate(self, key):
        '''Create a dict'''
        if self.exists(key):
            return not OPERATED
        self.setdefault(key, {})
        return OPERATED

    def dset(self, key, field, element):
        '''Set the element (value) of a dict field (key)'''
        d = self.get(key)
        if not isinstance(d, dict):
            return not OPERATED
        d[field] = element
        self._autodump()
        return OPERATED

    def dget(self, key, field):
        '''Get the element (value) of a dict field (key)'''
        if not self.dexists(key, field):
            return None
        return self.db[key][field]

    def dexists(self, key, field):
        '''Determine if a dict field (key) exists'''
        d = self.get(key)
        if not isinstance(d, dict):
            return None
        return field in d

    def dkeys(self, key):
        '''Get all the fields (keys) in a dict'''
        d = self.get(key)
        if not isinstance(d, dict):
            return None
        return d.keys()

    def dvals(self, key):
        '''Get all the elements (values) in a dict'''
        d = self.get(key)
        if not isinstance(d, dict):
            return None
        return d.values()

    def dempty(self, key):
        '''Determine if a dict is empty'''
        if self.dlen(key) is None:
            return None
        return self.dlen(key) == 0

    def dlen(self, key):
        '''Get the number of fields (keys) in a dict'''
        d = self.get(key)
        if not isinstance(d, dict):
            return None
        return len(d)

    def drem(self, key, field):
        '''Remove a dict field (key)'''
        if not self.dexists(key, field):
            return None
        element = self.db[key].pop(field)
        self._autodump()
        return element

    def dclear(self, key):
        '''Remove all from a dict'''
        d = self.get(key)
        if not isinstance(d, dict):
            return not OPERATED
        d.clear()
        self._autodump()
        return OPERATED
