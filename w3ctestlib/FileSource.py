#!/usr/bin/python
# CSS Test Source Manipulation Library
# Initial code by fantasai, joint copyright 2010 W3C and Microsoft
# Licensed under BSD 3-Clause: <http://www.w3.org/Consortium/Legal/2008/03-bsd-license>

from os.path import join
import os
import filecmp
import collections
import codecs
from Utils import getMimeFromExt, escapeToNamedASCII, basepath, relativeURL
import hashlib

from ReferenceData import ReferenceData
from Metadata import Metadata

UserData = collections.namedtuple('UserData', ('name', 'link'))


class FileSource:
  """Object representing a file. Two FileSources are equal if they represent
     the same file contents. It is recommended to use a SourceCache to generate
     FileSources.
  """

  def __init__(self, sourceTree, sourcepath, relpath, mimetype=None, data=None):
    """Init FileSource from source path. Give it relative path relpath.

       `mimetype` should be the canonical MIME type for the file, if known.
        If `mimetype` is None, guess type from file extension, defaulting to
        the None key's value in extensionMap.

       `data` if provided, is a the contents of the file. Otherwise the file is read
        from disk.
    """
    self.sourceTree = sourceTree
    self.sourcepath = sourcepath
    self.relpath = relpath
    self.mimetype = mimetype or getMimeFromExt(sourcepath)  # Used by build.py
    self._data = data
    self.errors = None  # Used by build.py & Shepherd
    self.encoding = 'utf-8'
    self.refs = {}
    self.scripts = {}
    self.metadata = None
    self.metaSource = None

  def __eq__(self, other):
    if not isinstance(other, FileSource):
      return False
    return (self.sourcepath == other.sourcepath or
            filecmp.cmp(self.sourcepath, other.sourcepath))

  def __ne__(self, other):
    return not self == other

  def __cmp__(self, other):
    return cmp(self.name(), other.name())

  def name(self):
    return self.sourceTree.getAssetName(self.sourcepath)

  def type(self):
    return self.sourceTree.getAssetType(self.sourcepath)

  def relativeURL(self, other):
    return relativeURL(self.relpath, other.relpath)

  def data(self):
    """Return file contents as a byte string."""
    if (self._data is None):
      with open(self.sourcepath, 'r') as f:
        self._data = f.read()
    if (self._data.startswith(codecs.BOM_UTF8)):
      self.encoding = 'utf-8-sig' # XXX look for other unicode BOMs
    return self._data

  def unicode(self):
    try:
      return self.data().decode(self.encoding)
    except UnicodeDecodeError:
      return None

  def parse(self):
    """Parses and validates FileSource data from sourcepath."""
    self.loadMetadata()

  def validate(self):
    """Ensure data is loaded from sourcepath."""
    self.parse()

  def adjustContentPaths(self, format):
    """Adjust any paths in file content for output format
       XXX need to account for group paths"""
    if (self.refs):
      seenRefs = {}
      seenRefs[self.sourcepath] = '=='

      def adjustReferences(source):
        newRefs = {}
        for refName in source.refs:
          refType, refPath, refNode, refSource = source.refs[refName]
          if refSource:
            refPath = relativeURL(format.dest(self.relpath), format.dest(refSource.relpath))
            if (refSource.sourcepath not in seenRefs):
              seenRefs[refSource.sourcepath] = refType
              adjustReferences(refSource)
          else:
            refPath = relativeURL(format.dest(self.relpath), format.dest(refPath))
          if (refPath != refNode.get('href')):
            refNode.set('href', refPath)
          newRefs[refName] = (refType, refPath, refNode, refSource) # update path in metadata
        source.refs = newRefs
      adjustReferences(self)

    if (self.scripts):   # force testharness.js scripts to absolute path
      for src in self.scripts:
        if (src.endswith('/resources/testharness.js')):   # accept relative paths to testharness.js
            scriptNode = self.scripts[src]
            scriptNode.set('src', '/resources/testharness.js')
        elif (src.endswith('/resources/testharnessreport.js')):
            scriptNode = self.scripts[src]
            scriptNode.set('src', '/resources/testharnessreport.js')

  def write(self, format):
    """Writes FileSource.data() out to `self.relpath` through Format `format`."""
    data = self.data()
    with open(format.dest(self.relpath), 'w') as f:
      f.write(data)
    if (self.metaSource):
      self.metaSource.write(format) # XXX need to get output path from format, but not let it choose actual format

  def compact(self):
    """Clears all cached data, preserves computed data."""
    pass

  def revision(self):
    """Returns hash of the contents of this file and any related file, references, support files, etc.
       XXX also needs to account for .meta file
    """
    sha = hashlib.sha1()
    sha.update(self.data())
    seenRefs = set(self.sourcepath)

    def hashReference(source):
        for refName in source.refs:
            refSource = source.refs[refName][3]
            if (refSource and (refSource.sourcepath not in seenRefs)):
                sha.update(refSource.data())
                seenRefs.add(refSource.sourcepath)
                hashReference(refSource)
    hashReference(self)
    return sha.hexdigest()

  def loadMetadata(self):
    """Look for .meta file and load any metadata from it if present
    """
    pass

  def augmentMetadata(self, next=None, prev=None, reference=None, notReference=None):
    if (self.metaSource):
      return self.metaSource.augmentMetadata(next, prev, reference, notReference)
    return None

  # See http://wiki.csswg.org/test/css2.1/format for more info on metadata
  def getMetadata(self, asUnicode=False):
    """Return dictionary of test metadata. Stores list of errors
       in self.errors if there are parse or metadata errors.
       Data fields include:
         - asserts [list of strings]
         - credits [list of (name string, url string) tuples]
         - reviewers [ list of (name string, url string) tuples]
         - flags   [list of token strings]
         - links   [list of url strings]
         - name    [string]
         - title   [string]
         - references [list of ReferenceData per reference; None if not reftest]
         - revision   [revision id of last commit]
         - selftest [bool]
         - scripttest [bool]
       Strings are given in ascii unless asUnicode==True.
    """
    # Used by build.py
    # Used by Shepherd

    self.validate()

    def encode(str):
        return str if (hasattr(str, 'line')) else str.encode('utf-8')

    def escape(str):
      return str.encode('utf-8') if asUnicode else escapeToNamedASCII(str)

    def listReferences(source, seen):
        refGroups = []
        for refType, refRelPath, refNode, refSource in source.refs.values():
            if ('==' == refType):
                if (refSource):
                    refSourcePath = refSource.sourcepath
                else:
                    refSourcePath = os.path.normpath(join(basepath(source.sourcepath), refRelPath))
                if (refSourcePath in seen):
                    continue
                seen.add(refSourcePath)
                if (refSource):
                    sourceData = ReferenceData(name=self.sourceTree.getAssetName(refSourcePath), type=refType,
                                               relpath=refRelPath, repopath=refSourcePath)
                    if (refSource.refs):
                        subRefLists = listReferences(refSource, seen.copy())
                        if (subRefLists):
                            for subRefList in subRefLists:
                                refGroups.append([sourceData] + subRefList)
                        else:
                            refGroups.append([sourceData])
                    else:
                        refGroups.append([sourceData])
                else:
                    sourceData = ReferenceData(name=self.sourceTree.getAssetName(refSourcePath), type=refType,
                                               relpath=relativeURL(self.sourcepath, refSourcePath),
                                               repopath=refSourcePath)
                    refGroups.append([sourceData])
        notRefs = {}
        for refType, refRelPath, refNode, refSource in source.refs.values():
            if ('!=' == refType):
                if (refSource):
                    refSourcePath = refSource.sourcepath
                else:
                    refSourcePath = os.path.normpath(join(basepath(source.sourcepath), refRelPath))
                if (refSourcePath in seen):
                    continue
                seen.add(refSourcePath)
                if (refSource):
                    sourceData = ReferenceData(name=self.sourceTree.getAssetName(refSourcePath), type=refType,
                                               relpath=refRelPath, repopath=refSourcePath)
                    notRefs[sourceData.name] = sourceData
                    if (refSource.refs):
                        for subRefList in listReferences(refSource, seen):
                            for subRefData in subRefList:
                                notRefs[subRefData.name] = subRefData
                else:
                    sourceData = ReferenceData(name=self.sourceTree.getAssetName(refSourcePath), type=refType,
                                               relpath=relativeURL(self.sourcepath, refSourcePath),
                                               repopath=refSourcePath)
                    notRefs[sourceData.name] = sourceData
        if (notRefs):
            for refData in notRefs.values():
                refData.type = '!='
            if (refGroups):
                for refGroup in refGroups:
                    for notRef in notRefs.values():
                        for ref in refGroup:
                            if (ref.name == notRef.name):
                                break
                        else:
                            refGroup.append(notRef)
            else:
                refGroups.append(notRefs.values())
        return refGroups

    references = listReferences(self, set([self.sourcepath])) if (self.refs) else None

    if (self.metadata):
      data = Metadata(name=encode(self.name()),
                      title=escape(self.metadata['title']),
                      asserts=[escape(assertion) for assertion in self.metadata['asserts']],
                      credits=[UserData(escape(name), encode(link)) for name, link in self.metadata['credits']],
                      reviewers=[UserData(escape(name), encode(link)) for name, link in self.metadata['reviewers']],
                      flags=[encode(flag) for flag in self.metadata['flags']],
                      links=[encode(link) for link in self.metadata['links']],
                      references=references,
                      revision=self.revision(),
                      selftest=self.isSelftest(),
                      scripttest=self.isScripttest())
      return data
    return None

  def addReference(self, referenceSource, match=None):
    """Add reference source."""
    self.validate()
    refName = referenceSource.name()
    refPath = self.relativeURL(referenceSource)
    if refName not in self.refs:
      node = None
      if match == '==':
        node = self.augmentMetadata(reference=referenceSource).reference
      elif match == '!=':
        node = self.augmentMetadata(notReference=referenceSource).notReference
      self.refs[refName] = (match, refPath, node, referenceSource)
    else:
      node = self.refs[refName][2]
      node.set('href', refPath)
      if (match):
        node.set('rel', 'mismatch' if ('!=' == match) else 'match')
      else:
        match = self.refs[refName][0]
      self.refs[refName] = (match, refPath, node, referenceSource)

  def getReferencePaths(self):
    """Get list of paths to references as tuple(path, relPath, refType)."""
    self.validate()
    return [(os.path.join(os.path.dirname(self.sourcepath), ref[1]),
             os.path.join(os.path.dirname(self.relpath), ref[1]),
             ref[0])
            for ref in self.refs.values()]

  def isTest(self):
    # Used by build.py
    self.validate()
    return bool(self.metadata) and bool(self.metadata.get('links'))

  def isReftest(self):
    return self.isTest() and bool(self.refs)

  def isSelftest(self):
    return self.isTest() and (not bool(self.refs))

  def isScripttest(self):
    if (self.isTest() and self.scripts):
        for src in self.scripts:
            if (src.endswith('/resources/testharness.js')):   # accept relative paths to testharness.js
                return True
    return False

  def hasFlag(self, flag):
    data = self.getMetadata()
    if data:
      return flag in data['flags']
    return False
