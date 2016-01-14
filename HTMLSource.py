#!/usr/bin/python
# CSS Test Source Manipulation Library
# Initial code by fantasai, joint copyright 2010 W3C and Microsoft
# Licensed under BSD 3-Clause: <http://www.w3.org/Consortium/Legal/2008/03-bsd-license>

import html5lib
from html5lib import treebuilders
from lxml import etree
import HTMLSerializer
import warnings

from FileSource import FileSource
from XMLSource import XMLSource

xhtmlns = '{http://www.w3.org/1999/xhtml}'
svgns = '{http://www.w3.org/2000/svg}'
xmlns = '{http://www.w3.org/XML/1998/namespace}'
xlinkns = '{http://www.w3.org/1999/xlink}'


class HTMLSource(XMLSource):
  """FileSource object with support for HTML metadata and HTML->XHTML conversions (untested)."""

  # Private Data and Methods
  __parser = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder('lxml'))

  # Public Methods

  def __init__(self, sourceTree, sourcepath, relpath, data=None):
    """Initialize HTMLSource by loading from HTML file `sourcepath`.
    """
    XMLSource.__init__(self, sourceTree, sourcepath, relpath, data=data)

  def parse(self):
    """Parse file and store any parse errors in self.errors"""
    self.errors = None
    try:
      data = self.data()
      if data:
        with warnings.catch_warnings():
          warnings.simplefilter("ignore")
          htmlStream = html5lib.inputstream.HTMLInputStream(data)
          if ('utf-8-sig' != self.encoding):  # if we found a BOM, respect it
            self.encoding = htmlStream.detectEncoding()[0]
          self.tree = self.__parser.parse(data, encoding=self.encoding)
          self.injectedTags = {}
      else:
        self.tree = None
        self.errors = ['Empty source file']
        self.encoding = 'utf-8'

      FileSource.loadMetadata(self)
      if ((not self.metadata) and self.tree and (not self.errors)):
        self.extractMetadata(self.tree)
    except Exception as e:
      print "PARSE ERROR: " + self.sourcepath
      e.W3CTestLibErrorLocation = self.sourcepath
      self.errors = [str(e)]
      self.encoding = 'utf-8'

  def _injectXLinks(self, element, nodeList):
    injected = False

    xlinkAttrs = ['href', 'type', 'role', 'arcrole', 'title', 'show', 'actuate']
    if (element.get('href') or element.get(xlinkns + 'href')):
      for attr in xlinkAttrs:
        if (element.get(xlinkns + attr)):
          injected = True
        if (element.get(attr)):
          injected = True
          value = element.get(attr)
          del element.attrib[attr]
          element.set(xlinkns + attr, value)
          nodeList.append((element, xlinkns + attr, attr))

    for child in element:
        if isinstance(child.tag, basestring): # element node
            qName = etree.QName(child.tag)
            if ('foreignobject' != qName.localname.lower()):
                injected |= self._injectXLinks(child, nodeList)
    return injected

  def _findElements(self, namespace, elementName):
      elements = self.tree.findall('.//{' + namespace + '}' + elementName)
      if (self.tree.getroot().tag == '{' + namespace + '}' + elementName):
          elements.insert(0, self.tree.getroot())
      return elements

  def _injectNamespace(self, elementName, prefix, namespace, doXLinks, nodeList):
    attr = xmlns + prefix if (prefix) else 'xmlns'
    elements = self._findElements(namespace, elementName)
    for element in elements:
      if not element.get(attr):
        element.set(attr, namespace)
        nodeList.append((element, attr, None))
        if (doXLinks):
          if (self._injectXLinks(element, nodeList)):
            element.set(xmlns + 'xlink', 'http://www.w3.org/1999/xlink')
            nodeList.append((element, xmlns + 'xlink', None))

  def injectNamespaces(self):
    nodeList = []
    self._injectNamespace('html', None, 'http://www.w3.org/1999/xhtml', False, nodeList)
    self._injectNamespace('svg', None, 'http://www.w3.org/2000/svg', True, nodeList)
    self._injectNamespace('math', None, 'http://www.w3.org/1998/Math/MathML', True, nodeList)
    return nodeList

  def removeNamespaces(self, nodeList):
      if nodeList:
          for element, attr, oldAttr in nodeList:
              if (oldAttr):
                  value = element.get(attr)
                  del element.attrib[attr]
                  element.set(oldAttr, value)
              else:
                  del element.attrib[attr]

  def serializeXHTML(self, doctype=None):
    self.validate()
    # Serialize
    nodeList = self.injectNamespaces()
#    print self.relpath
    serializer = HTMLSerializer.HTMLSerializer()
    o = serializer.serializeXHTML(self.tree, doctype)

    self.removeNamespaces(nodeList)
    return o

  def serializeHTML(self, doctype=None):
    self.validate()
    # Serialize
#    print self.relpath
    serializer = HTMLSerializer.HTMLSerializer()
    o = serializer.serializeHTML(self.tree, doctype)

    return o

  def data(self):
    if ((not self.tree) or (self.metaSource)):
      return FileSource.data(self)
    return self.serializeHTML().encode(self.encoding, 'xmlcharrefreplace')

  def unicode(self):
    if ((not self.tree) or (self.metaSource)):
      return FileSource.unicode(self)
    return self.serializeHTML()
