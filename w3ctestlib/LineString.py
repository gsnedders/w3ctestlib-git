#!/usr/bin/python
# CSS Test Source Manipulation Library
# Initial code by fantasai, joint copyright 2010 W3C and Microsoft
# Licensed under BSD 3-Clause: <http://www.w3.org/Consortium/Legal/2008/03-bsd-license>


class LineString(str):
    def __new__(cls, value, line):
        self = str.__new__(cls, value)
        self.line = line
        return self

    def lineValue(self):
        return 'Line ' + str(self.line) + ': ' + str.__str__(self) if (self.line) else str.__str__(self)
