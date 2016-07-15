#!/usr/bin/python
# CSS Test Source Manipulation Library
# Initial code by fantasai, joint copyright 2010 W3C and Microsoft
# Licensed under BSD 3-Clause: <http://www.w3.org/Consortium/Legal/2008/03-bsd-license>

import filecmp

from FileSource import FileSource


class ConfigSource(FileSource):
  """Object representing a text-based configuration file.
     Capable of merging multiple config-file contents.
  """

  def __init__(self, sourceTree, sourcepath, relpath, mimetype=None, data=None):
    """Init ConfigSource from source path. Give it relative path relpath.
    """
    FileSource.__init__(self, sourceTree, sourcepath, relpath, mimetype, data)
    self.sourcepath = [sourcepath]

  def __eq__(self, other):
    if not isinstance(other, ConfigSource):
      return False
    if self is other or self.sourcepath == other.sourcepath:
      return True
    if len(self.sourcepath) != len(other.sourcepath):
      return False
    for this, that in zip(self.sourcepath, other.sourcepath):
      if not filecmp.cmp(this, that):
        return False
    return True

  def __ne__(self, other):
    return not self == other

  def name(self):
    return '.htaccess'

  def type(self):
    return 'support'

  def data(self):
    """Merge contents of all config files represented by this source."""
    data = ''
    for src in self.sourcepath:
      with open(src) as f:
        data += f.read()
      data += '\n'
    return data

  def getMetadata(self, asUnicode=False):
    return None

  def append(self, other):
    """Appends contents of ConfigSource `other` to this source.
       Asserts if self.relpath != other.relpath.
    """
    assert isinstance(other, ConfigSource)
    assert self != other and self.relpath == other.relpath
    self.sourcepath.extend(other.sourcepath)
