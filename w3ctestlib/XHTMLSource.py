#!/usr/bin/python
# CSS Test Source Manipulation Library
# Initial code by fantasai, joint copyright 2010 W3C and Microsoft
# Licensed under BSD 3-Clause: <http://www.w3.org/Consortium/Legal/2008/03-bsd-license>

import HTMLSerializer

from XMLSource import XMLSource


class XHTMLSource(XMLSource):
  """FileSource object with support for XHTML->HTML conversions."""

  # Public Methods

  def __init__(self, sourceTree, sourcepath, relpath, data=None):
    """Initialize XHTMLSource by loading from XHTML file `sourcepath`.
      Parse errors are stored in `self.errors`,
      and the source is replaced with an XHTML error message.
    """
    XMLSource.__init__(self, sourceTree, sourcepath, relpath, data=data)

  def serializeXHTML(self, doctype=None):
    return self.serializeXML()

  def serializeHTML(self, doctype=None):
    self.validate()
    # Serialize
#    print self.relpath
    serializer = HTMLSerializer.HTMLSerializer()
    output = serializer.serializeHTML(self.tree, doctype)
    return output
