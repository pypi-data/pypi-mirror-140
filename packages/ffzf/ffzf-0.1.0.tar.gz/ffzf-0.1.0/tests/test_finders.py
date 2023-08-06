import unittest

from ffzf.finders import closest, n_closest

class TestFindingFunctions(unittest.TestCase):

    def test_closest(self):
        self.assertEqual(closest("hello", ["hello", "world"]), "hello")
        self.assertEqual(closest("hello", ["world", "hello"]), "hello")
        self.assertEqual(closest("hello", ["YELLO", "hey there"]), "YELLO")
        self.assertEqual(closest("travel", ["gravel", "gambit", "gated"], algorithm="jaro"), "gravel")
        self.assertEqual(closest("travel", ["gravel", "gambit", "gated"], algorithm="jarowinkler"), "gravel")
        self.assertEqual(closest("travel", ["gravel", "gambit", "guards"], algorithm="hamming"), "gravel")

    
    def test_n_closest(self):
        self.assertEqual(n_closest("hello", ["yello", "jello", "harps", "languid"], n=2), ["yello", "jello"])
        self.assertEqual(n_closest("hello", ["yello", "jello", "harps", "languid"], n=3), ["yello", "jello", "harps"])
        self.assertEqual(n_closest("hello", ["yello", "jello", "harps", "languid"], n=3, algorithm="jaro"), ["yello", "jello", "harps"])
        self.assertEqual(n_closest("hello", ["yello", "jello", "harps", "languid"], n=3, algorithm="jarowinkler"), ["yello", "jello", "harps"])

if __name__ == '__main__':
    unittest.main()