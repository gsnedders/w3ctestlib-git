import copy
import csv
import re

_space_chars = "\x09\x0a\x0c\x0d\x20"
_space_re = re.compile("[%s]+" % _space_chars)


def _collapse_whitespace(s):
    return _space_re.sub(' ', s).strip(_space_chars)


class SuperSuite(object):
    def __init__(self):
        self.suites = []

    def __iter__(self):
        for suite in self.suites:
            if suite.group is not None:
                for test in suite.group.iterTests():
                    yield test

    def buildIndex(self, fp):
        fields = ["id", "references", "title", "flags", "links", "revision", "credits", "assertion"]
        writer = csv.DictWriter(fp, fields, delimiter="\t", quoting=csv.QUOTE_NONE, quotechar="\0")
        writer.writeheader()
        seen = set()
        for test in self:
            if test.sourcepath in seen:
                continue
            seen.add(test.sourcepath)

            meta = copy.copy(test.getMetadata())
            if not meta:
                # error parsing test
                continue
            if (meta['scripttest']):
                meta['flags'].append('script')
            if meta.references:
                references = ";".join([(",".join([(("!" if ref.type == "!=" else "") + ref.repopath)
                                                  for ref in group]))
                                       for group in meta.references])
            else:
                references = ""

            row = {
                "id": test.sourcepath,
                "references": references,
                "title": _collapse_whitespace(meta.title),
                "flags": ",".join(meta.flags),
                "links": ",".join(meta.links),
                "revision": meta.revision,
                "credits": ",".join(["`%s`<%s>" % x for x in meta.credits]),
                "assertion": _collapse_whitespace(' '.join(meta.asserts))
            }
            writer.writerow(row)
