#!/usr/bin/python
# CSS Test Source Manipulation Library
# Initial code by fantasai, joint copyright 2010 W3C and Microsoft
# Licensed under BSD 3-Clause: <http://www.w3.org/Consortium/Legal/2008/03-bsd-license>

from os.path import join
import re

from XMLSource import XMLSource
from LineString import LineString

xhtmlns = '{http://www.w3.org/1999/xhtml}'
svgns = '{http://www.w3.org/2000/svg}'
xmlns = '{http://www.w3.org/XML/1998/namespace}'
xlinkns = '{http://www.w3.org/1999/xlink}'


class SVGSource(XMLSource):
  """FileSource object with support for extracting metadata from SVG."""

  def __init__(self, sourceTree, sourcepath, relpath, data=None):
    """Initialize SVGSource by loading from SVG file `sourcepath`.
      Parse errors are stored in `self.errors`,
      and the source is replaced with an XHTML error message.
    """
    XMLSource.__init__(self, sourceTree, sourcepath, relpath, data=data)

  def getMeatdataContainer(self):
    groups = self.tree.getroot().findall(svgns + 'g')
    for group in groups:
      if ('testmeta' == group.get('id')):
        return group
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
        errors.append("Missing <g id='testmeta'> element")
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
            elif (node.tag == svgns + 'metadata'):
                metatype = node.get('class')
                metatype = metatype.strip() if metatype else metatype
                # requirement flags
                if ('flags' == metatype):
                    if (readFlags):
                        errors.append(LineString("Flags must only be specified once.", node.sourceline))
                    else:
                        readFlags = True
                        text = node.find(svgns + 'text')
                        flagString = text.text if (text) else node.text
                        if (flagString):
                            for flag in sorted(flagString.split()):
                                flags.append(flag)
            elif (node.tag == svgns + 'desc'):
                metatype = node.get('class')
                metatype = metatype.strip() if metatype else metatype
                # test assertions
                if ('assert' == metatype):
                    asserts.append(node.text.strip().replace('\t', ' '))
            # test title
            elif node.tag == svgns + 'title':
                title = node.text.strip() if node.text else ''
                match = re.match('(?:[^:]*)[tT]est(?:[^:]*):(.*)', title, re.DOTALL)
                if (match):
                    title = match.group(1)
                title = title.strip()
            # script tag (XXX restricted to metadata container?)
            elif (node.tag == svgns + 'script'):
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
