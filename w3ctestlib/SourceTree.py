#!/usr/bin/python
# CSS Test Source Manipulation Library
# Initial code by fantasai, joint copyright 2010 W3C and Microsoft
# Licensed under BSD 3-Clause: <http://www.w3.org/Consortium/Legal/2008/03-bsd-license>

import os
import re
from Utils import assetName


class SourceTree(object):
  """Class that manages structure of test repository source.
     Temporarily hard-coded path and filename rules, this should be configurable.
  """

  def __init__(self, repository=None):
    self.mTestExtensions = ['.xht', '.html', '.xhtml', '.htm', '.xml', '.svg']
    self.mReferenceExtensions = ['.xht', '.html', '.xhtml', '.htm', '.xml', '.png', '.svg']
    self.mRepository = repository

  def _splitDirs(self, dir):
    if ('' == dir):
      pathList = []
    elif ('/' in dir):
      pathList = dir.split('/')
    else:
      pathList = dir.split(os.path.sep)
    return pathList

  def _splitPath(self, filePath):
    """split a path into a list of directory names and the file name
       paths may come form the os or mercurial, which always uses '/' as the
       directory separator
    """
    dir, fileName = os.path.split(filePath.lower())
    return (self._splitDirs(dir), fileName)

  def isTracked(self, filePath):
    pathList, fileName = self._splitPath(filePath)
    return (not self._isIgnored(pathList, fileName))

  def _isApprovedPath(self, pathList):
    return ((1 < len(pathList)) and ('approved' == pathList[0]) and (('support' == pathList[1]) or ('src' in pathList)))

  def isApprovedPath(self, filePath):
    pathList, fileName = self._splitPath(filePath)
    return (not self._isIgnored(pathList, fileName)) and self._isApprovedPath(pathList)

  def _isIgnoredPath(self, pathList):
      return (('.hg' in pathList) or ('.git' in pathList) or
              ('.svn' in pathList) or ('cvs' in pathList) or
              ('incoming' in pathList) or ('work-in-progress' in pathList) or
              ('data' in pathList) or ('archive' in pathList) or
              ('reports' in pathList) or ('tools' == pathList[0]) or
              ('test-plan' in pathList) or ('test-plans' in pathList))

  def _isIgnored(self, pathList, fileName):
    if (pathList):  # ignore files in root
      return (self._isIgnoredPath(pathList) or
              fileName.startswith('.directory') or ('lock' == fileName) or
              ('.ds_store' == fileName) or
              fileName.startswith('.hg') or fileName.startswith('.git') or
              ('sections.dat' == fileName) or ('get-spec-sections.pl' == fileName))
    return True

  def isIgnored(self, filePath):
    pathList, fileName = self._splitPath(filePath)
    return self._isIgnored(pathList, fileName)

  def isIgnoredDir(self, dir):
    pathList = self._splitDirs(dir)
    return self._isIgnoredPath(pathList)

  def _isToolPath(self, pathList):
    return ('tools' in pathList)

  def _isTool(self, pathList, fileName):
    return self._isToolPath(pathList)

  def isTool(self, filePath):
    pathList, fileName = self._splitPath(filePath)
    return (not self._isIgnored(pathList, fileName)) and self._isTool(pathList, fileName)

  def _isSupportPath(self, pathList):
    return ('support' in pathList)

  def _isSupport(self, pathList, fileName):
    return (self._isSupportPath(pathList) or
            ((not self._isTool(pathList, fileName)) and
             (not self._isReference(pathList, fileName)) and
             (not self._isTestCase(pathList, fileName))))

  def isSupport(self, filePath):
    pathList, fileName = self._splitPath(filePath)
    return (not self._isIgnored(pathList, fileName)) and self._isSupport(pathList, fileName)

  def _isReferencePath(self, pathList):
    return (('reftest' in pathList) or ('reference' in pathList))

  def _isReference(self, pathList, fileName):
    if ((not self._isSupportPath(pathList)) and (not self._isToolPath(pathList))):
      baseName, fileExt = os.path.splitext(fileName)[:2]
      if (bool(re.search('(^ref-|^notref-).+', baseName)) or
          bool(re.search('.+(-ref[0-9]*$|-notref[0-9]*$)', baseName)) or
          ('-ref-' in baseName) or ('-notref-' in baseName)):
        return (fileExt in self.mReferenceExtensions)
      if (self._isReferencePath(pathList)):
        return (fileExt in self.mReferenceExtensions)
    return False

  def isReference(self, filePath):
    pathList, fileName = self._splitPath(filePath)
    return (not self._isIgnored(pathList, fileName)) and self._isReference(pathList, fileName)

  def isReferenceAnywhere(self, filePath):
    pathList, fileName = self._splitPath(filePath)
    return self._isReference(pathList, fileName)

  def _isTestCase(self, pathList, fileName):
    if ((not self._isToolPath(pathList)) and (not self._isSupportPath(pathList)) and (not self._isReference(pathList, fileName))):
      fileExt = os.path.splitext(fileName)[1]
      return (fileExt in self.mTestExtensions)
    return False

  def isTestCase(self, filePath):
    pathList, fileName = self._splitPath(filePath)
    return (not self._isIgnored(pathList, fileName)) and self._isTestCase(pathList, fileName)

  def getAssetName(self, filePath):
    pathList, fileName = self._splitPath(filePath)
    if (self._isReference(pathList, fileName) or self._isTestCase(pathList, fileName)):
      return assetName(fileName)
    return fileName.lower() # support files keep full name

  def getAssetType(self, filePath):
    pathList, fileName = self._splitPath(filePath)
    if (self._isReference(pathList, fileName)):
      return 'reference'
    if (self._isTestCase(pathList, fileName)):
      return 'testcase'
    if (self._isTool(pathList, fileName)):
      return 'tool'
    return 'support'
