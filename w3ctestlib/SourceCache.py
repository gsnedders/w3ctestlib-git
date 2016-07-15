#!/usr/bin/python
# CSS Test Source Manipulation Library
# Initial code by fantasai, joint copyright 2010 W3C and Microsoft
# Licensed under BSD 3-Clause: <http://www.w3.org/Consortium/Legal/2008/03-bsd-license>

from os.path import abspath, basename, realpath
from Utils import getMimeFromExt

from XHTMLSource import XHTMLSource
from HTMLSource import HTMLSource
from SVGSource import SVGSource
from XMLSource import XMLSource
from FileSource import FileSource
from ConfigSource import ConfigSource


class SourceCache:
  """Cache for FileSource objects. Supports one FileSource object
     per sourcepath.
  """

  def __init__(self, sourceTree):
    # Used by build.py
    # Used by Shepherd
    self.__cache = {}
    self.sourceTree = sourceTree

  def generateSource(self, sourcepath, relpath, data=None):
    """Return a FileSource or derivative based on the extensionMap.

       Uses a cache to avoid creating more than one of the same object:
       does not support creating two FileSources with the same sourcepath;
       asserts if this is tried. (.htaccess files are not cached.)

       Cache is bypassed if loading form a change context
    """
    # Used by build.py with 2 args
    # Used by Shepherd with 3 args
    abssourcepath = abspath(realpath(sourcepath))
    key = (abssourcepath, relpath)
    if data is None and key in self.__cache:
      return self.__cache[key]

    if basename(sourcepath) == '.htaccess':
      return ConfigSource(self.sourceTree, sourcepath, relpath, data)
    mime = getMimeFromExt(sourcepath)
    if (mime == 'application/xhtml+xml'):
      source = XHTMLSource(self.sourceTree, sourcepath, relpath, data)
    elif (mime == 'text/html'):
      source = HTMLSource(self.sourceTree, sourcepath, relpath, data)
    elif (mime == 'image/svg+xml'):
      source = SVGSource(self.sourceTree, sourcepath, relpath, data)
    elif (mime == 'application/xml'):
      source = XMLSource(self.sourceTree, sourcepath, relpath, data)
    else:
      source = FileSource(self.sourceTree, sourcepath, relpath, mime, data)
    if data is None:
      self.__cache[key] = source
    return source
