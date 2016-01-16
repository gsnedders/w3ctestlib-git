#!/usr/bin/python
# CSS Test Source Manipulation Library
# Initial code by fantasai, joint copyright 2010 W3C and Microsoft
# Licensed under BSD 3-Clause:
# <http://www.w3.org/Consortium/Legal/2008/03-bsd-license>

import os
import re

import enum

from Utils import assetName


_ignored_paths = {".hg", ".git", ".svn", "cvs", "incoming", "work-in-progress",
                  "data", "archive", "reports", "test-plan", "test-plans"}

_ignored_files = {"lock", "LOCK", ".DS_Store",
                  "sections.dat", "get-spec-sections.pl"}

_ignored_files_startswith = {".directory", ".hg", ".git"}

_test_extensions = {'.xht', '.html', '.xhtml', '.htm', '.xml', '.svg'}

_reference_extensions = _test_extensions | {'.png'}

_reference_paths = {'reftest', 'reference'}

_reference_file_re = re.compile(r'(^|-)(not)?ref[0-9]*(-|\.[^.]+$)')


class FileInfo(object):

    def __init__(self, ignored, approved, category):
        if ignored and approved:
            raise ValueError("test cannot be ignored and approved")
        self.ignored = ignored
        self.approved = approved
        self.category = category


class FileCategory(enum.Enum):
    tool = 1
    reference = 2
    support = 3
    testcase = 4


def split_path(path):
    if '/' in path:
        segments = path.split("/")
    else:
        segments = path.split(os.path.sep)
    pathList = segments[:-1]
    fileName = segments[-1]
    return (pathList, fileName)


def categorize_file(path):
    pathList, fileName = split_path(path)
    baseName, fileExt = os.path.splitext(fileName)

    # Check if ignored
    ignored = (not pathList or
               pathList[0] == "tools" or
               _ignored_paths & set(pathList) or
               fileName in _ignored_files or
               any(fileName.startswith(x) for x in _ignored_files_startswith))

    # Check if approved
    approved = (not ignored and len(pathList) > 1 and pathList[0] == "approved" and
                (pathList[1] == "support" or "src" in pathList))

    # Determine category
    if "tools" in pathList:
        cat = FileCategory.tool
    elif "support" in pathList:
        cat = FileCategory.support
    elif (fileExt in _reference_extensions and
          (_reference_paths & set(pathList) or
           _reference_file_re.search(fileName))):
        cat = FileCategory.reference
    elif fileExt in _test_extensions:
        cat = FileCategory.testcase
    else:
        cat = FileCategory.support

    return FileInfo(bool(ignored), bool(approved), cat)


class SourceTree(object):
    """Class that manages structure of test repository source.
    """

    def __init__(self, repository=None):
        pass

    def isTracked(self, filePath):
        info = categorize_file(filePath)
        return not info.ignored

    def isApprovedPath(self, filePath):
        info = categorize_file(filePath)
        return not info.ignored and info.approved

    def isIgnored(self, filePath):
        info = categorize_file(filePath)
        return info.ignored

    def isIgnoredDir(self, dir):
        if "/" in dir:
            path = dir + "/foo"
        else:
            path = os.path.join(dir, "foo")
        info = categorize_file(path)
        return info.ignored

    def isTool(self, filePath):
        info = categorize_file(filePath)
        return not info.ignored and info.category == FileCategory.tool

    def isSupport(self, filePath):
        info = categorize_file(filePath)
        return not info.ignored and info.category == FileCategory.support

    def isReference(self, filePath):
        info = categorize_file(filePath)
        return not info.ignored and info.category == FileCategory.reference

    def isReferenceAnywhere(self, filePath):
        info = categorize_file(filePath)
        return info.category == FileCategory.reference

    def isTestCase(self, filePath):
        info = categorize_file(filePath)
        return not info.ignored and info.category == FileCategory.testcase

    def getAssetName(self, filePath):
        info = categorize_file(filePath)
        pathList, fileName = split_path(filePath)
        if (info.category == FileCategory.testcase or info.category == FileCategory.reference):
            return assetName(fileName)
        return fileName.lower()  # support files keep full name

    def getAssetType(self, filePath):
        info = categorize_file(filePath)
        if info.category == FileCategory.tool:
            return 'tool'
        elif info.category == FileCategory.reference:
            return 'reference'
        elif info.category == FileCategory.support:
            return 'support'
        elif info.category == FileCategory.testcase:
            return 'testcase'
        else:
            assert False, "unreachable"
