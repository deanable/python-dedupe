import unittest
import json
import time

from src.hash_storage import HashFormat, format_hash_for_storage, parse_hash_from_storage, validate_hash_format
from src.hash_calculator import HashResult

class TestHashStorage(unittest.TestCase):

    def setUp(self):
        self.result1 = HashResult(
            hash_value="abc",
            algorithm="phash",
            timestamp=time.time(),
            bit_length=64,
            metadata={'w': 100, 'h': 100}
        )
        self.result2 = HashResult(
            hash_value="def",
            algorithm="sha256",
            timestamp=time.time(),
            bit_length=256,
            metadata={'size': 1024}
        )
        self.results = {
            'phash': self.result1,
            'sha256': self.result2
        }

    def test_json_format(self):
        stored = format_hash_for_storage(self.results, HashFormat.JSON)
        self.assertIsInstance(stored, str)
        parsed = parse_hash_from_storage(stored, HashFormat.JSON)
        self.assertIsInstance(parsed, dict)
        self.assertIn('phash', parsed)
        self.assertIn('sha256', parsed)
        self.assertEqual(parsed['phash']['hash_value'], "abc")

    def test_delimited_format(self):
        stored = format_hash_for_storage(self.results, HashFormat.DELIMITED)
        # Expected: "phash:abc|sha256:def" (sorted by key)
        self.assertEqual(stored, "phash:abc|sha256:def")

        parsed = parse_hash_from_storage(stored, HashFormat.DELIMITED)
        self.assertIsInstance(parsed, dict)
        self.assertIn('phash', parsed)
        self.assertEqual(parsed['phash']['hash_value'], "abc")
        self.assertEqual(parsed['phash']['algorithm'], "phash")

    def test_separate_fields_format(self):
        stored = format_hash_for_storage(self.results, HashFormat.SEPARATE_FIELDS)
        self.assertIsInstance(stored, dict)
        self.assertIn('phash', stored)
        self.assertEqual(stored['phash']['hash_value'], "abc")

        parsed = parse_hash_from_storage(stored, HashFormat.SEPARATE_FIELDS)
        self.assertEqual(parsed, stored)

    def test_validate_hash_format(self):
        stored = format_hash_for_storage(self.results, HashFormat.JSON)
        self.assertTrue(validate_hash_format(stored, HashFormat.JSON))
        self.assertFalse(validate_hash_format("invalid json", HashFormat.JSON))

        stored_delim = format_hash_for_storage(self.results, HashFormat.DELIMITED)
        self.assertTrue(validate_hash_format(stored_delim, HashFormat.DELIMITED))

        # This might pass as DELIMITED if split('|') works. Empty string -> empty dict.
        self.assertTrue(validate_hash_format("", HashFormat.DELIMITED))

if __name__ == '__main__':
    unittest.main()
