import unittest
import os
import shutil
import tempfile
import time

from src.dedup_engine import DuplicateGroup
from src.dedup_strategies import KeepStrategy, DedupDecision, select_item_to_keep, generate_dedup_plan

class TestDedupStrategies(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

        # Create dummy files
        self.files = []
        for i, size in enumerate([100, 200, 150]):
            path = os.path.join(self.test_dir, f'file_{i}.txt')
            with open(path, 'wb') as f:
                f.write(b'a' * size)
            self.files.append(path)

        # Set mtimes: file_0=old, file_1=middle, file_2=new
        now = time.time()
        os.utime(self.files[0], (now - 1000, now - 1000))
        os.utime(self.files[1], (now - 500, now - 500))
        os.utime(self.files[2], (now, now))

        self.group = DuplicateGroup(
            items=self.files,
            similarity_scores={f: 100.0 for f in self.files},
            hash_type='test'
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_keep_largest(self):
        decision = select_item_to_keep(self.group, KeepStrategy.LARGEST)
        # file_1 (200 bytes) is largest
        self.assertEqual(decision.keep_item, self.files[1])
        self.assertIn(self.files[0], decision.remove_items)
        self.assertIn(self.files[2], decision.remove_items)

    def test_keep_oldest(self):
        decision = select_item_to_keep(self.group, KeepStrategy.OLDEST)
        # file_0 is oldest (mtime now-1000)
        self.assertEqual(decision.keep_item, self.files[0])
        self.assertIn(self.files[1], decision.remove_items)
        self.assertIn(self.files[2], decision.remove_items)

    def test_keep_newest(self):
        decision = select_item_to_keep(self.group, KeepStrategy.NEWEST)
        # file_2 is newest (mtime now)
        self.assertEqual(decision.keep_item, self.files[2])
        self.assertIn(self.files[0], decision.remove_items)
        self.assertIn(self.files[1], decision.remove_items)

    def test_keep_first(self):
        decision = select_item_to_keep(self.group, KeepStrategy.FIRST)
        self.assertEqual(decision.keep_item, self.files[0])
        self.assertIn(self.files[1], decision.remove_items)
        self.assertIn(self.files[2], decision.remove_items)

    def test_manual(self):
        decision = select_item_to_keep(self.group, KeepStrategy.MANUAL)
        self.assertIsNone(decision.keep_item)
        self.assertEqual(len(decision.remove_items), 0)

if __name__ == '__main__':
    unittest.main()
