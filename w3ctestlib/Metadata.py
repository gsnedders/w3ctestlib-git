#!/usr/bin/python
# CSS Test Source Manipulation Library
# Initial code by fantasai, joint copyright 2010 W3C and Microsoft
# Licensed under BSD 3-Clause: <http://www.w3.org/Consortium/Legal/2008/03-bsd-license>

from NamedDict import NamedDict


class Metadata(NamedDict):
    __slots__ = ('name', 'title', 'asserts', 'credits', 'reviewers', 'flags', 'links', 'references', 'revision', 'selftest', 'scripttest')

    def __init__(self, name=None, title=None, asserts=[], credits=[], reviewers=[], flags=[], links=[],
                 references=[], revision=None, selftest=True, scripttest=False):
        self.name = name
        self.title = title
        self.asserts = asserts
        self.credits = credits
        self.reviewers = reviewers
        self.flags = flags
        self.links = links
        self.references = references
        self.revision = revision
        self.selftest = selftest
        self.scripttest = scripttest

    def __getitem__(self, key):
        if ('name' == key):
            return self.name
        if ('title' == key):
            return self.title
        if ('asserts' == key):
            return self.asserts
        if ('credits' == key):
            return self.credits
        if ('reviewers' == key):
            return self.reviewers
        if ('flags' == key):
            return self.flags
        if ('links' == key):
            return self.links
        if ('references' == key):
            return self.references
        if ('revision' == key):
            return self.revision
        if ('selftest' == key):
            return self.selftest
        if ('scripttest' == key):
            return self.scripttest
        return None

    def __setitem__(self, key, value):
        if ('name' == key):
            self.name = value
        elif ('title' == key):
            self.title = value
        elif ('asserts' == key):
            self.asserts = value
        elif ('credits' == key):
            self.credits = value
        elif ('reviewers' == key):
            self.reviewers = value
        elif ('flags' == key):
            self.flags = value
        elif ('links' == key):
            self.links = value
        elif ('references' == key):
            self.references = value
        elif ('revision' == key):
            self.revision = value
        elif ('selftest' == key):
            self.selftest = value
        elif ('scripttest' == key):
            self.scripttest = value
        else:
            raise KeyError()
