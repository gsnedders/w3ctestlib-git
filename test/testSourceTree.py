import unittest

from os.path import sep

import w3ctestlib.SourceTree as SourceTree


class TestSourceTree(unittest.TestCase):
    def test_sep(self):
        if sep == "\\":
            self.assertEquals(SourceTree.split_path("foo\\bar"), (["foo"], "bar"))
            self.assertEquals(SourceTree.split_path("foo\\bar\\xxx"), (["foo", "bar"], "xxx"))
            self.assertEquals(SourceTree.split_path("foo\\bar/xxx"), (["foo"], "bar/xxx"))
            self.assertEquals(SourceTree.split_path("foo/bar\\xxx"), (["foo/bar"], "xxx"))
        else:
            assert sep == "/"
            self.assertEquals(SourceTree.split_path("foo\\bar"), ([], "foo\\bar"))
            self.assertEquals(SourceTree.split_path("foo\\bar\\xxx"), ([], "foo\\bar\\xxx"))
            self.assertEquals(SourceTree.split_path("foo\\bar/xxx"), (["foo\\bar"], "xxx"))
            self.assertEquals(SourceTree.split_path("foo/bar\\xxx"), (["foo"], "bar\\xxx"))

        self.assertEquals(SourceTree.split_path("foo"), ([], "foo"))
        self.assertEquals(SourceTree.split_path("foo/bar"), (["foo"], "bar"))
        self.assertEquals(SourceTree.split_path("foo/bar/xxx"), (["foo", "bar"], "xxx"))

    def test_tracked(self):
        tree = SourceTree.SourceTree()
        # Files in the root dir are ignored
        self.assertFalse(tree.isTracked("foo"))

        # Ensure standard filenames are tracked
        self.assertTrue(tree.isTracked("dir/foo"))
        self.assertTrue(tree.isTracked("dir/foo.html"))
        self.assertTrue(tree.isTracked("dir/foo-ref.html"))
        self.assertTrue(tree.isTracked("dir/foo.png"))

        # ignored dirs
        ignored_dirs = [".hg", ".git", ".svn", "cvs", "incoming", "work-in-progress",
                        "data", "archive", "reports", "test-plan", "test-plans"]
        for d in ignored_dirs:
            self.assertFalse(tree.isTracked("%s/bar" % d))
            self.assertFalse(tree.isTracked("dir/%s/bar" % d))
            self.assertTrue(tree.isTracked("%sx/bar" % d))
            self.assertTrue(tree.isTracked("dir/%sx/bar" % d))

        # tools is only ignored at the top level
        self.assertFalse(tree.isTracked("tools/bar"))
        self.assertTrue(tree.isTracked("dir/tools/bar"))

        # ignored files
        ignored_files_startswith = [".directory", ".hg", ".git"]
        ignored_files = ["lock", "LOCK", ".DS_Store", "sections.dat", "get-spec-sections.pl"]
        for f in ignored_files_startswith:
            self.assertFalse(tree.isTracked("dir/%s" % f))
            self.assertFalse(tree.isTracked("dir/%sx" % f))
        for f in ignored_files:
            self.assertFalse(tree.isTracked("dir/%s" % f))
            self.assertTrue(tree.isTracked("dir/%sx" % f))

    def test_approved_path(self):
        tree = SourceTree.SourceTree()
        self.assertFalse(tree.isApprovedPath("approved"))
        self.assertFalse(tree.isApprovedPath("approved/foo"))
        self.assertFalse(tree.isApprovedPath("approved/foo/bar"))
        self.assertFalse(tree.isApprovedPath("approved/support"))
        self.assertTrue(tree.isApprovedPath("approved/support/foo"))
        self.assertTrue(tree.isApprovedPath("approved/support/foo/bar"))
        self.assertFalse(tree.isApprovedPath("approved/support/.hg/bar"))
        self.assertFalse(tree.isApprovedPath("approved/src"))
        self.assertTrue(tree.isApprovedPath("approved/src/foo"))
        self.assertTrue(tree.isApprovedPath("approved/src/foo/bar"))
        self.assertTrue(tree.isApprovedPath("approved/foo/src/bar"))
        self.assertFalse(tree.isApprovedPath("approved/src/.hg/bar"))

    def test_ignored(self):
        tree = SourceTree.SourceTree()
        # Files in the root dir are ignored
        self.assertTrue(tree.isIgnored("foo"))

        # Ensure standard filenames are tracked
        self.assertFalse(tree.isIgnored("dir/foo"))
        self.assertFalse(tree.isIgnored("dir/foo.html"))
        self.assertFalse(tree.isIgnored("dir/foo-ref.html"))
        self.assertFalse(tree.isIgnored("dir/foo.png"))

        # ignored dirs
        ignored_dirs = [".hg", ".git", ".svn", "cvs", "incoming", "work-in-progress",
                        "data", "archive", "reports", "test-plan", "test-plans"]
        for d in ignored_dirs:
            self.assertTrue(tree.isIgnored("%s/bar" % d))
            self.assertTrue(tree.isIgnored("dir/%s/bar" % d))
            self.assertFalse(tree.isIgnored("%sx/bar" % d))
            self.assertFalse(tree.isIgnored("dir/%sx/bar" % d))

        # tools is only ignored at the top level
        self.assertTrue(tree.isIgnored("tools/bar"))
        self.assertFalse(tree.isIgnored("dir/tools/bar"))

        # ignored files
        ignored_files_startswith = [".directory", ".hg", ".git"]
        ignored_files = ["lock", ".DS_Store", "sections.dat", "get-spec-sections.pl"]
        for f in ignored_files_startswith:
            self.assertTrue(tree.isIgnored("dir/%s" % f))
            self.assertTrue(tree.isIgnored("dir/%sx" % f))
        for f in ignored_files:
            self.assertTrue(tree.isIgnored("dir/%s" % f))
            self.assertFalse(tree.isIgnored("dir/%sx" % f))

    def test_tool(self):
        tree = SourceTree.SourceTree()
        self.assertFalse(tree.isTool("tools"))
        self.assertFalse(tree.isTool("tools/foo"))
        self.assertFalse(tree.isTool("tools/foo/bar"))
        self.assertTrue(tree.isTool("foo/tools/bar"))
        self.assertTrue(tree.isTool("foo/tools/bar/xxx"))

    def test_support(self):
        tree = SourceTree.SourceTree()
        self.assertFalse(tree.isSupport("foo"))
        self.assertTrue(tree.isSupport("support/foo"))
        self.assertTrue(tree.isSupport("foo/bar"))
        self.assertFalse(tree.isSupport("tools/foo"))
        self.assertFalse(tree.isSupport("reftest/foo.html"))
        self.assertFalse(tree.isSupport("reference/foo.html"))
        self.assertFalse(tree.isSupport("foo/ref-bar.html"))
        self.assertFalse(tree.isSupport("foo/notref-bar.html"))
        self.assertFalse(tree.isSupport("foo/bar-ref-xxx.html"))
        self.assertFalse(tree.isSupport("foo/bar-notref-xxx.html"))
        self.assertFalse(tree.isSupport("foo/bar-ref012-xxx.html"))
        self.assertFalse(tree.isSupport("foo/bar-notref012-xxx.html"))
        self.assertFalse(tree.isSupport("foo/bar.html"))
        self.assertFalse(tree.isSupport("foo/bar.svg"))

    def test_reference(self):
        tree = SourceTree.SourceTree()
        self.assertFalse(tree.isReference("foo"))
        self.assertFalse(tree.isReference("foo/bar"))
        self.assertFalse(tree.isReference("support/foo"))
        self.assertFalse(tree.isReference("tools/foo"))
        self.assertTrue(tree.isReference("reftest/foo.html"))
        self.assertTrue(tree.isReference("reference/foo.html"))
        self.assertTrue(tree.isReference("foo/ref-bar.html"))
        self.assertTrue(tree.isReference("foo/notref-bar.html"))
        self.assertTrue(tree.isReference("foo/bar-ref-xxx.html"))
        self.assertTrue(tree.isReference("foo/bar-notref-xxx.html"))
        self.assertTrue(tree.isReference("foo/bar-ref012.html"))
        self.assertTrue(tree.isReference("foo/bar-notref012.html"))


if __name__ == '__main__':
    unittest.main()
