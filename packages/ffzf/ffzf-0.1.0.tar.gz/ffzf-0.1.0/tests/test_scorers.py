import unittest

from ffzf.scorers import (
    levenshtein_distance,
    jaro_similarity,
    jaro_winkler_similarity,
    hamming_distance
)


class TestScoringFunctions(unittest.TestCase):

    def test_levenshtein_distance(self):
        self.assertEqual(levenshtein_distance("", ""), 0.0)
        self.assertEqual(levenshtein_distance("a", ""), 1.0)
        self.assertEqual(levenshtein_distance("", "a"), 1.0)
        self.assertEqual(levenshtein_distance("a", "a"), 0.0)
        self.assertEqual(levenshtein_distance("a", "b"), 1.0)
        self.assertEqual(levenshtein_distance("b", "a"), 1.0)
        self.assertEqual(levenshtein_distance("a", "ab"), 1.0)
        self.assertEqual(levenshtein_distance("ab", "a"), 1.0)
        self.assertEqual(levenshtein_distance("a", "A"), 0.0)
        self.assertEqual(levenshtein_distance("euphoria", "elation"), 7.0)
        self.assertEqual(
            levenshtein_distance("triangle", "abcdefghijklmnopqrstuvwxyz"),
            24.0
        )

    def test_jaro_similarity(self):
        self.assertAlmostEqual(jaro_similarity(
            "subprime", "primers"), 0.779762, places=2)
        self.assertAlmostEqual(jaro_similarity(
            "SubPRIME", "Primers"), 0.779762, places=2)
        self.assertAlmostEqual(jaro_similarity(
            "SUBprime", "prImeRs"), 0.779762, places=2)
        self.assertAlmostEqual(jaro_similarity(
            "codify", "reify"), 0.7, places=2)
        self.assertAlmostEqual(jaro_similarity(
            "absolute", "resolute"), 0.833333, places=2)
        self.assertAlmostEqual(jaro_similarity(
            "anchors", "bank"), 0.595238, places=2)
        self.assertAlmostEqual(jaro_similarity(
            "out", "regaining"), 0.0, places=2)

    def test_jaro_winkler_similarity(self):
        self.assertAlmostEqual(jaro_winkler_similarity(
            "apples", "oranges"), 0.642857, places=2)
        self.assertAlmostEqual(jaro_winkler_similarity(
            "becoming", "trip"), 0.458333, places=2)
        self.assertAlmostEqual(jaro_winkler_similarity(
            "developers", "investment"), 0.532682, places=2)
        self.assertAlmostEqual(jaro_winkler_similarity(
            "trip", "drive"), 0.633333, places=2)
        self.assertAlmostEqual(jaro_winkler_similarity(
            "over", "out"), 0.527778, places=2)

    def test_hamming_distance(self):
        self.assertEqual(hamming_distance("", ""), 0.0)
        self.assertEqual(hamming_distance("ask", "ask"), 0.0)
        self.assertEqual(hamming_distance("men", "hen"), 1.0)
        self.assertEqual(hamming_distance("hello world", "hey there!!"), 9.0)
        with self.assertRaises(ValueError):
            hamming_distance("a short string",
                             "a a string longer than a short string")


if __name__ == '__main__':
    unittest.main()
