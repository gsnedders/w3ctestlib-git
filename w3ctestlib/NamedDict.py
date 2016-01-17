#!/usr/bin/python
# CSS Test Source Manipulation Library
# Initial code by fantasai, joint copyright 2010 W3C and Microsoft
# Licensed under BSD 3-Clause: <http://www.w3.org/Consortium/Legal/2008/03-bsd-license>

from collections import MutableMapping


class NamedDict(MutableMapping):
    def __getitem__(self, key):
        if key in self:
            return getattr(self, key)
        else:
            raise KeyError, key

    def __setitem__(self, key, value):
        if key in self:
            setattr(self, key, value)
        else:
            raise KeyError, key

    def __delitem__(self, key):
        raise TypeError, "cannot remove from a NamedDict"

    def __len__(self):
        return len(self.__slots__)

    def __iter__(self):
        return iter(self.__slots__)

    def __contains__(self, key):
        return (key in self.__slots__)
