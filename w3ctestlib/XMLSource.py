#!/usr/bin/python
# CSS Test Source Manipulation Library
# Initial code by fantasai, joint copyright 2010 W3C and Microsoft
# Licensed under BSD 3-Clause: <http://www.w3.org/Consortium/Legal/2008/03-bsd-license>

from os.path import join
import re
import collections
from lxml import etree

from FileSource import FileSource
from StringReader import StringReader
from LineString import LineString

import Utils # set up XML catalog # flake8: noqa
xhtmlns = '{http://www.w3.org/1999/xhtml}'
svgns = '{http://www.w3.org/2000/svg}'
xmlns = '{http://www.w3.org/XML/1998/namespace}'
xlinkns = '{http://www.w3.org/1999/xlink}'


class XMLSource(FileSource):
  """FileSource object with support reading XML trees."""

  NodeTuple = collections.namedtuple('NodeTuple', ['next', 'prev', 'reference', 'notReference'])

  # Public Data
  syntaxErrorDoc = \
  u"""
  <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
  <html xmlns="http://www.w3.org/1999/xhtml">
    <head><title>Syntax Error</title></head>
    <body>
      <p>The XML file <![CDATA[%s]]> contains a syntax error and could not be parsed.
      Please correct it and try again.</p>
      <p>The parser's error report was:</p>
      <pre><![CDATA[%s]]></pre>
    </body>
  </html>
  """

  # Private Data and Methods
  __parser = etree.XMLParser(no_network=True,
  # perf nightmare           dtd_validation=True,
                             remove_comments=False,
                             strip_cdata=False,
                             resolve_entities=False)

  # Public Methods

  def __init__(self, sourceTree, sourcepath, relpath, data=None):
    """Initialize XMLSource by loading from XML file `sourcepath`.
      Parse errors are reported in `self.errors`,
      and the source is replaced with an XHTML error message.
    """
    FileSource.__init__(self, sourceTree, sourcepath, relpath, data=data)
    self.tree = None
    self.injectedTags = {}

  def cacheAsParseError(self, filename, e):
      """Replace document with an error message."""
      errorDoc = self.syntaxErrorDoc % (filename, e)
      from StringIO import StringIO
      self.tree = etree.parse(StringIO(errorDoc), parser=self.__parser)

  def parse(self):
    """Parse file and store any parse errors in self.errors"""
    self.errors = None
    try:
      data = self.data()
      if (data):
        self.tree = etree.parse(StringReader(data), parser=self.__parser)
        self.encoding = self.tree.docinfo.encoding or 'utf-8'
        self.injectedTags = {}
      else:
        self.tree = None
        self.errors = ['Empty source file']
        self.encoding = 'utf-8'

      FileSource.loadMetadata(self)
      if ((not self.metadata) and self.tree and (not self.errors)):
        self.extractMetadata(self.tree)
    except etree.ParseError as e:
      print "PARSE ERROR: " + self.sourcepath
      self.cacheAsParseError(self.sourcepath, e)
      e.W3CTestLibErrorLocation = self.sourcepath
      self.errors = [str(e)]
      self.encoding = 'utf-8'

  def validate(self):
    """Parse file if not parsed, and store any parse errors in self.errors"""
    if self.tree is None:
      self.parse()

  def getMeatdataContainer(self):
    return self.tree.getroot().find(xhtmlns + 'head')

  def injectMetadataLink(self, rel, href, tagCode=None):
    """Inject (prepend) <link> with data given inside metadata container.
       Injected element is tagged with `tagCode`, which can be
       used to clear it with clearInjectedTags later.
    """
    self.validate()
    container = self.getMeatdataContainer()
    if (container):
      node = etree.Element(xhtmlns + 'link', {'rel': rel, 'href': href})
      node.tail = container.text
      container.insert(0, node)
      self.injectedTags[node] = tagCode or True
      return node
    return None

  def clearInjectedTags(self, tagCode=None):
    """Clears all injected elements from the tree, or clears injected
       elements tagged with `tagCode` if `tagCode` is given.
    """
    if not self.injectedTags or not self.tree:
      return
    for node in self.injectedTags:
      node.getparent().remove(node)
      del self.injectedTags[node]

  def serializeXML(self):
    self.validate()
    return etree.tounicode(self.tree)

  def data(self):
    if ((not self.tree) or (self.metaSource)):
      return FileSource.data(self)
    return self.serializeXML().encode(self.encoding, 'xmlcharrefreplace')

  def unicode(self):
    if ((not self.tree) or (self.metaSource)):
      return FileSource.unicode(self)
    return self.serializeXML()

  def write(self, format, output=None):
    """Write Source through OutputFormat `format`.
       Write contents as string `output` instead if specified.
    """
    if not output:
      output = self.unicode()

    # write
    with open(format.dest(self.relpath), 'w') as f:
      f.write(output.encode(self.encoding, 'xmlcharrefreplace'))

  def compact(self):
    self.tree = None

  def getMetadataElements(self, tree):
    container = self.getMeatdataContainer()
    if container is not None:
      return [node for node in container]
    return None

  def extractMetadata(self, tree):
    """Extract metadata from tree."""
    links = []
    credits = []
    reviewers = []
    flags = []
    asserts = []
    title = ''

    def tokenMatch(token, string):
        return bool(re.search('(^|\s+)%s($|\s+)' % token, string)) if (string) else False

    errors = []
    readFlags = False
    metaElements = self.getMetadataElements(tree)
    if (not metaElements):
        errors.append("Missing <head> element")
    else:
        # Scan and cache metadata
        for node in metaElements:
            if (node.tag == xhtmlns + 'link'):
                # help links
                if tokenMatch('help', node.get('rel')):
                    link = node.get('href').strip() if node.get('href') else None
                    if (not link):
                        errors.append(LineString("Help link missing href value.", node.sourceline))
                    elif (not (link.startswith('http://') or link.startswith('https://'))):
                        errors.append(LineString("Help link " + link.encode('utf-8') + " must be absolute URL.", node.sourceline))
                    elif (link in links):
                        errors.append(LineString("Duplicate help link " + link.encode('utf-8') + ".", node.sourceline))
                    else:
                        links.append(LineString(link, node.sourceline))
                # == references
                elif tokenMatch('match', node.get('rel')) or tokenMatch('reference', node.get('rel')):
                    refPath = node.get('href').strip() if node.get('href') else None
                    if (not refPath):
                        errors.append(LineString("Reference link missing href value.", node.sourceline))
                    else:
                        refName = self.sourceTree.getAssetName(join(self.sourcepath, refPath))
                        if (refName in self.refs):
                            errors.append(LineString("Reference " + refName.encode('utf-8') + " already specified.", node.sourceline))
                        else:
                            self.refs[refName] = ('==', refPath, node, None)
                # != references
                elif tokenMatch('mismatch', node.get('rel')) or tokenMatch('not-reference', node.get('rel')):
                    refPath = node.get('href').strip() if node.get('href') else None
                    if (not refPath):
                        errors.append(LineString("Reference link missing href value.", node.sourceline))
                    else:
                        refName = self.sourceTree.getAssetName(join(self.sourcepath, refPath))
                        if (refName in self.refs):
                            errors.append(LineString("Reference " + refName.encode('utf-8') + " already specified.", node.sourceline))
                        else:
                            self.refs[refName] = ('!=', refPath, node, None)
                else: # may have both author and reviewer in the same link
                    # credits
                    if tokenMatch('author', node.get('rel')):
                        name = node.get('title')
                        name = name.strip() if name else name
                        if (not name):
                            errors.append(LineString("Author link missing name (title attribute).", node.sourceline))
                        else:
                            link = node.get('href').strip() if node.get('href') else None
                            if (not link):
                                errors.append(LineString("Author link for \"" + name.encode('utf-8') + "\" missing contact URL (http or mailto).", node.sourceline))
                            else:
                                credits.append((name, link))
                    # reviewers
                    if tokenMatch('reviewer', node.get('rel')):
                        name = node.get('title')
                        name = name.strip() if name else name
                        if (not name):
                            errors.append(LineString("Reviewer link missing name (title attribute).", node.sourceline))
                        else:
                            link = node.get('href').strip() if node.get('href') else None
                            if (not link):
                                errors.append(LineString("Reviewer link for \"" + name.encode('utf-8') + "\" missing contact URL (http or mailto).", node.sourceline))
                            else:
                                reviewers.append((name, link))
            elif (node.tag == xhtmlns + 'meta'):
                metatype = node.get('name')
                metatype = metatype.strip() if metatype else metatype
                # requirement flags
                if ('flags' == metatype):
                    if (readFlags):
                        errors.append(LineString("Flags must only be specified once.", node.sourceline))
                    else:
                        readFlags = True
                        if (node.get('content') is None):
                            errors.append(LineString("Flags meta missing content attribute.", node.sourceline))
                        else:
                            for flag in sorted(node.get('content').split()):
                                flags.append(flag)
                # test assertions
                elif ('assert' == metatype):
                    if (node.get('content') is None):
                        errors.append(LineString("Assert meta missing content attribute.", node.sourceline))
                    else:
                        asserts.append(node.get('content').strip().replace('\t', ' '))
            # title
            elif (node.tag == xhtmlns + 'title'):
                title = node.text.strip() if node.text else ''
                match = re.match('(?:[^:]*)[tT]est(?:[^:]*):(.*)', title, re.DOTALL)
                if (match):
                    title = match.group(1)
                title = title.strip()
            # script
            elif (node.tag == xhtmlns + 'script'):
                src = node.get('src').strip() if node.get('src') else None
                if (src):
                    self.scripts[src] = node

    if (asserts or credits or reviewers or flags or links or title):
        self.metadata = {'asserts': asserts,
                         'credits': credits,
                         'reviewers': reviewers,
                         'flags': flags,
                         'links': links,
                         'title': title
                         }

    if (errors):
        if (self.errors):
            self.errors += errors
        else:
            self.errors = errors

  def augmentMetadata(self, next=None, prev=None, reference=None, notReference=None):
     """Add extra useful metadata to the head. All arguments are optional.
          * Adds next/prev links to  next/prev Sources given
          * Adds reference link to reference Source given
     """
     self.validate()
     if next:
       next = self.injectMetadataLink('next', self.relativeURL(next), 'next')
     if prev:
       prev = self.injectMetadataLink('prev', self.relativeURL(prev), 'prev')
     if reference:
       reference = self.injectMetadataLink('match', self.relativeURL(reference), 'ref')
     if notReference:
       notReference = self.injectMetadataLink('mismatch', self.relativeURL(notReference), 'not-ref')
     return self.NodeTuple(next, prev, reference, notReference)
