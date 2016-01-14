#!/usr/bin/python
# CSS Test Source Manipulation Library
# Initial code by fantasai, joint copyright 2010 W3C and Microsoft
# Licensed under BSD 3-Clause: <http://www.w3.org/Consortium/Legal/2008/03-bsd-license>


class NamedDict(object):
    def get(self, key):
        if (key in self):
            return self[key]
        return None

    def __eq__(self, other):
        for key in self.__slots__:
            if (self[key] != other[key]):
                return False
        return True

    def __ne__(self, other):
        for key in self.__slots__:
            if (self[key] != other[key]):
                return True
        return False

    def __len__(self):
        return len(self.__slots__)

    def __iter__(self):
        return iter(self.__slots__)

    def __contains__(self, key):
        return (key in self.__slots__)

    def copy(self):
        clone = self.__class__()
        for key in self.__slots__:
            clone[key] = self[key]
        return clone

    def keys(self):
        return self.__slots__

    def has_key(self, key):
        return (key in self)

    def items(self):
        return [(key, self[key]) for key in self.__slots__]

    def iteritems(self):
        return iter(self.items())

    def iterkeys(self):
        return self.__iter__()

    def itervalues(self):
        return iter(self.items())

    def __str__(self):
        return '{ ' + ', '.join([key + ': ' + str(self[key]) for key in self.__slots__]) + ' }'
