#!/usr/bin/python
# CSS Test Source Manipulation Library
# Initial code by fantasai, joint copyright 2010 W3C and Microsoft
# Licensed under BSD 3-Clause: <http://www.w3.org/Consortium/Legal/2008/03-bsd-license>

from NamedDict import NamedDict


class ReferenceData(NamedDict):
    __slots__ = ('name', 'type', 'relpath', 'repopath')

    def __init__(self, name=None, type=None, relpath=None, repopath=None):
        self.name = name
        self.type = type
        self.relpath = relpath
        self.repopath = repopath
