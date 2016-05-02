import unittest

from w3ctestlib import HTMLSource, SourceTree


class TestHTMLSource(unittest.TestCase):
    def test_default_encoding(self):
        tree = SourceTree.SourceTree()
        f = HTMLSource.HTMLSource(tree,
                                  "a.html",
                                  "a.html",
                                  "<p>Foo")
        f.validate()
        self.assertEquals("windows-1252", f.encoding)

    def test_default_encoding_non_ascii(self):
        tree = SourceTree.SourceTree()
        f = HTMLSource.HTMLSource(tree,
                                  "a.html",
                                  "a.html",
                                  u"<p>C\u00c9fe".encode("windows-1252"))
        f.validate()
        self.assertEquals("windows-1252", f.encoding)
        self.assertIn(u"\u00c9".encode("windows-1252"), f.data())

    def test_detected_utf16(self):
        tree = SourceTree.SourceTree()
        f = HTMLSource.HTMLSource(tree,
                                  "a.html",
                                  "a.html",
                                  u"\uFEFF<p>C\u00c9fe".encode("utf-16-le"))
        f.validate()
        self.assertEquals("utf-16le", f.encoding)

    def test_detected_utf8_bom(self):
        tree = SourceTree.SourceTree()
        f = HTMLSource.HTMLSource(tree,
                                  "a.html",
                                  "a.html",
                                  u"\uFEFF<p>C\u00c9fe".encode("utf-8"))
        f.validate()
        self.assertEquals("utf-8", f.encoding)

    def test_detected_utf8_meta(self):
        tree = SourceTree.SourceTree()
        f = HTMLSource.HTMLSource(tree,
                                  "a.html",
                                  "a.html",
                                  u"<meta charset=utf8><p>C\u00c9fe".encode("utf-8"))
        f.validate()
        self.assertEquals("utf-8", f.encoding)
