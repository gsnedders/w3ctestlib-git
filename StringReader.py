#!/usr/bin/python
# CSS Test Source Manipulation Library
# Initial code by fantasai, joint copyright 2010 W3C and Microsoft
# Licensed under BSD 3-Clause: <http://www.w3.org/Consortium/Legal/2008/03-bsd-license>

try:
  from cStringIO import StringIO as StringReader
except ImportError:
  from StringIO import StringIO as StringReader

__all__ = ["StringReader"]
