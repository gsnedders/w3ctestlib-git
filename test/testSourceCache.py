import posixpath
import unittest

from w3ctestlib import SourceCache, SourceTree


_ref_template = """
<title>Foobar</title>
<link rel="help" href="http://example.com">
<link rel="match" href="%s">
<p>Foo
"""


class TestSourceCache(unittest.TestCase):
    def test_ref_paths(self):
        """Check we handle different relpaths correctly

        This test is in SourceCache because it's ultimately relied upon
        the cache not conflating different relpaths."""
        tree = SourceTree.SourceTree()
        cache = SourceCache.SourceCache(tree)

        # Get all our test FileSource objects
        test_a_source = cache.generateSource("a/test_a.html",
                                             "test_a.html",
                                             _ref_template % "../b/c.xht")
        ref_source_a = cache.generateSource("a/../b/c.xht",
                                            "../b/c.xht")
        test_ax_source = cache.generateSource("a/x/test_ax.html",
                                              "test_ax.html",
                                              _ref_template % "../../b/c.xht")
        ref_source_b = cache.generateSource("a/x/../../b/c.xht",
                                            "../../b/c.xht")

        # Get metadata for the tests
        self.assertIsNotNone(test_a_source.getMetadata())
        self.assertIsNotNone(test_ax_source.getMetadata())

        # Check some identities hold
        self.assertEquals(posixpath.normpath(ref_source_a.sourcepath),
                          posixpath.normpath(ref_source_b.sourcepath))
        self.assertEquals(ref_source_a.name(),
                          ref_source_b.name())
        self.assertIn(ref_source_a.name(), test_a_source.refs)
        self.assertIn(ref_source_b.name(), test_ax_source.refs)

        # Check getReferencePaths gives real sourcepaths
        test_a_refs = test_a_source.getReferencePaths()
        self.assertEquals(1, len(test_a_refs))
        refSrcPath, _, _ = test_a_refs[0]
        self.assertEquals("b/c.xht", posixpath.normpath(refSrcPath))

        test_ax_refs = test_ax_source.getReferencePaths()
        self.assertEquals(1, len(test_ax_refs))
        refSrcPath, _, _ = test_ax_refs[0]
        self.assertEquals("b/c.xht", posixpath.normpath(refSrcPath))

        # Call addReference to (possibly) rewrite path
        test_a_source.addReference(ref_source_a)
        test_ax_source.addReference(ref_source_b)

        # Check getReferencePaths still gives real sourcepaths
        test_a_refs = test_a_source.getReferencePaths()
        self.assertEquals(1, len(test_a_refs))
        refSrcPath, _, _ = test_a_refs[0]
        self.assertEquals("b/c.xht", posixpath.normpath(refSrcPath))

        test_ax_refs = test_ax_source.getReferencePaths()
        self.assertEquals(1, len(test_ax_refs))
        refSrcPath, _, _ = test_ax_refs[0]
        self.assertEquals("b/c.xht", posixpath.normpath(refSrcPath))
