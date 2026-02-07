import unittest

from src.hash_comparison import calculate_hamming_distance, calculate_similarity_percentage, are_hashes_similar, are_hashes_exact_match

class TestHashComparison(unittest.TestCase):

    def test_calculate_hamming_distance(self):
        # 0 (0000) vs f (1111) -> 4 bits
        self.assertEqual(calculate_hamming_distance("0", "f"), 4)
        # a (1010) vs b (1011) -> 1 bit
        self.assertEqual(calculate_hamming_distance("a", "b"), 1)
        # Same -> 0
        self.assertEqual(calculate_hamming_distance("ffff", "ffff"), 0)

        # Test error
        with self.assertRaises(ValueError):
            calculate_hamming_distance("0", "ff")

    def test_calculate_similarity_percentage(self):
        # Distance 0 -> 100%
        self.assertEqual(calculate_similarity_percentage(0, 100), 100.0)
        # Distance 50/100 -> 50%
        self.assertEqual(calculate_similarity_percentage(50, 100), 50.0)
        # Distance 10/100 -> 90%
        self.assertEqual(calculate_similarity_percentage(10, 100), 90.0)

    def test_are_hashes_similar(self):
        # bit length 16 (hex length 4)
        # Distance 0 -> 100%
        self.assertTrue(are_hashes_similar("aaaa", "aaaa", threshold=100))

        # Distance 1 -> (15/16)*100 = 93.75%
        # Threshold 90 -> True
        # "aaaa" (1010 1010 1010 1010)
        # "aaab" (1010 1010 1010 1011) -> dist 1
        self.assertTrue(are_hashes_similar("aaaa", "aaab", threshold=90))
        # Threshold 95 -> False
        self.assertFalse(are_hashes_similar("aaaa", "aaab", threshold=95))

    def test_are_hashes_exact_match(self):
        self.assertTrue(are_hashes_exact_match("abc", "abc"))
        self.assertFalse(are_hashes_exact_match("abc", "abd"))

if __name__ == '__main__':
    unittest.main()
