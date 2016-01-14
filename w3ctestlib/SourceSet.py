#!/usr/bin/python
# CSS Test Source Manipulation Library
# Initial code by fantasai, joint copyright 2010 W3C and Microsoft
# Licensed under BSD 3-Clause: <http://www.w3.org/Consortium/Legal/2008/03-bsd-license>

from ConfigSource import ConfigSource


class SourceSet:
  """Set of FileSource objects. No two FileSources of the same type in the set may
     have the same name (except .htaccess files, which are merged).
  """

  def __init__(self, sourceCache):
    self.sourceCache = sourceCache
    self.pathMap = {} # type/name -> source

  def __len__(self):
    return len(self.pathMap)

  def _keyOf(self, source):
    return source.type() + '/' + source.name()

  def __contains__(self, source):
    return self._keyOf(source) in self.pathMap

  def iter(self):
    """Iterate over FileSource objects in SourceSet.
    """
    return self.pathMap.itervalues()

  def addSource(self, source, ui):
    """Add FileSource `source`. Throws exception if we already have
       a FileSource with the same path relpath but different contents.
       (ConfigSources are exempt from this requirement.)
    """
    cachedSource = self.pathMap.get(self._keyOf(source))
    if not cachedSource:
      self.pathMap[self._keyOf(source)] = source
    else:
      if source != cachedSource:
        if isinstance(source, ConfigSource):
          cachedSource.append(source)
        else:
          ui.warn("File merge mismatch %s vs %s for %s\n" %
                  (cachedSource.sourcepath, source.sourcepath, source.name()))

  def add(self, sourcepath, relpath, ui):
    """Generate and add FileSource from sourceCache. Return the resulting
       FileSource.

       Throws exception if we already have a FileSource with the same path
       relpath but different contents.
    """
    source = self.sourceCache.generateSource(sourcepath, relpath)
    self.addSource(source, ui)
    return source

  @staticmethod
  def combine(a, b, ui):
    """Merges a and b, and returns whichever one contains the merger (which
       one is chosen based on merge efficiency). Can accept None as an argument.
    """
    if not (a and b):
      return a or b
    if len(a) < len(b):
      return b.merge(a, ui)
    return a.merge(b, ui)

  def merge(self, other, ui):
    """Merge sourceSet's contents into this SourceSet.

       Throws a RuntimeError if there's a sourceCache mismatch.
       Throws an Exception if two files with the same relpath mismatch.
       Returns merge result (i.e. self)
    """
    if self.sourceCache is not other.sourceCache:
      raise RuntimeError

    for source in other.pathMap.itervalues():
      self.addSource(source, ui)
    return self

  def adjustContentPaths(self, format):
    for source in self.pathMap.itervalues():
      source.adjustContentPaths(format)

  def write(self, format):
    """Write files out through OutputFormat `format`.
    """
    for source in self.pathMap.itervalues():
      format.write(source)
