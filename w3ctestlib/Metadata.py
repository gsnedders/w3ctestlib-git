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
