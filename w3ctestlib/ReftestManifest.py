#!/usr/bin/python
# CSS Test Source Manipulation Library
# Initial code by fantasai, joint copyright 2010 W3C and Microsoft
# Licensed under BSD 3-Clause: <http://www.w3.org/Consortium/Legal/2008/03-bsd-license>

from os.path import exists, join
import re
from Utils import basepath, isPathInsideBase

from ConfigSource import ConfigSource


class ReftestFilepathError(Exception):
  pass


class ReftestManifest(ConfigSource):
  """Object representing a reftest manifest file.
     Iterating the ReftestManifest returns (testpath, refpath) tuples
     with paths relative to the manifest.
  """

  def __init__(self, sourceTree, sourcepath, relpath, data=None):
    """Init ReftestManifest from source path. Give it relative path `relpath`
       and load its .htaccess file.
    """
    ConfigSource.__init__(self, sourceTree, sourcepath, relpath, mimetype='config/reftest', data=data)

  def basepath(self):
    """Returns the base relpath of this reftest manifest path, i.e.
       the parent of the manifest file.
    """
    return basepath(self.relpath)

  baseRE = re.compile(r'^#\s*relstrip\s+(\S+)\s*')
  stripRE = re.compile(r'#.*')
  parseRE = re.compile(r'^\s*([=!]=)\s*(\S+)\s+(\S+)')

  def __iter__(self):
    """Parse the reftest manifest files represented by this ReftestManifest
       and return path information about each reftest pair as
         ((test-sourcepath, ref-sourcepath), (test-relpath, ref-relpath), reftype)
       Raises a ReftestFilepathError if any sources file do not exist or
       if any relpaths point higher than the relpath root.
    """
    striplist = []
    for src in self.sourcepath:
      relbase = basepath(self.relpath)
      srcbase = basepath(src)
      with open(src) as f:
        for line in f:
          strip = self.baseRE.search(line)
          if strip:
            striplist.append(strip.group(1))
          line = self.stripRE.sub('', line)
          m = self.parseRE.search(line)
          if m:
            record = ((join(srcbase, m.group(2)), join(srcbase, m.group(3))),
                      (join(relbase, m.group(2)), join(relbase, m.group(3))),
                      m.group(1))
            # for strip in striplist:
            # strip relrecord
            if not exists(record[0][0]):
              raise ReftestFilepathError("Manifest Error in %s: "
                                         "Reftest test file %s does not exist."
                                         % (src, record[0][0]))
            elif not exists(record[0][1]):
              raise ReftestFilepathError("Manifest Error in %s: "
                                         "Reftest reference file %s does not exist."
                                         % (src, record[0][1]))
            elif not isPathInsideBase(record[1][0]):
              raise ReftestFilepathError("Manifest Error in %s: "
                                         "Reftest test replath %s not within relpath root."
                                         % (src, record[1][0]))
            elif not isPathInsideBase(record[1][1]):
              raise ReftestFilepathError("Manifest Error in %s: "
                                         "Reftest test replath %s not within relpath root."
                                         % (src, record[1][1]))
            yield record
