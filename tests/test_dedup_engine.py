import unittest
import os
import shutil
import tempfile
from PIL import Image

from src.dedup_engine import ImageDeduplicator, DuplicateGroup
from src.hash_calculator import HashResult

class TestImageDeduplicator(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()

        # Create base image (random noise) to ensure structure for pHash
        self.img1_path = os.path.join(self.test_dir, 'img1.jpg')
        # Use os.urandom to generate random bytes for RGB image
        # 100x100x3 = 30000 bytes
        random_data = os.urandom(100 * 100 * 3)
        self.img1 = Image.frombytes('RGB', (100, 100), random_data)
        self.img1.save(self.img1_path)

        # Create exact duplicate
        self.img2_path = os.path.join(self.test_dir, 'img2.jpg')
        shutil.copy(self.img1_path, self.img2_path)

        # Create slightly modified image (small patch changed)
        self.img3_path = os.path.join(self.test_dir, 'img3.jpg')
        self.img3 = self.img1.copy()
        # Modify a 5x5 block in the center to ensure small change
        for x in range(48, 53):
            for y in range(48, 53):
                self.img3.putpixel((x, y), (0, 0, 0))
        self.img3.save(self.img3_path)

        # Create completely different image (different random noise)
        self.img4_path = os.path.join(self.test_dir, 'img4.jpg')
        random_data2 = os.urandom(100 * 100 * 3)
        self.img4 = Image.frombytes('RGB', (100, 100), random_data2)
        self.img4.save(self.img4_path)

        self.deduplicator = ImageDeduplicator(similarity_threshold=90.0)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_build_hash_map(self):
        images = [self.img1_path, self.img2_path, self.img3_path, self.img4_path]
        hash_map = self.deduplicator.build_hash_map(images, algorithm='phash')
        self.assertEqual(len(hash_map), 4)
        for path in images:
            self.assertIn(path, hash_map)
            self.assertIsInstance(hash_map[path], HashResult)

    def test_find_exact_duplicates_phash(self):
        # phash might be identical for img1 and img3 if change is small enough
        # But definitely for img1 and img2
        images = [self.img1_path, self.img2_path, self.img3_path, self.img4_path]
        hash_map = self.deduplicator.build_hash_map(images, algorithm='phash')

        groups = self.deduplicator.find_exact_duplicates(hash_map)

        # img1 and img2 should be in same group
        # img3 might be in same group depending on phash robustness (1 pixel change usually doesn't change phash)
        # img4 should be separate

        found_group = False
        for group in groups:
            if self.img1_path in group.items and self.img2_path in group.items:
                found_group = True
                self.assertEqual(group.similarity_scores[self.img1_path], 100.0)
        self.assertTrue(found_group)

    def test_find_exact_duplicates_crypto(self):
        # SHA256 should distinguish img1 and img3
        images = [self.img1_path, self.img2_path, self.img3_path, self.img4_path]
        hash_map = self.deduplicator.build_hash_map(images, algorithm='sha256')

        groups = self.deduplicator.find_exact_duplicates(hash_map)

        # Only img1 and img2 are identical
        found_group_12 = False
        found_group_3 = False # single items not returned as groups usually?
        # find_exact_duplicates returns groups with len > 1

        for group in groups:
            items = set(group.items)
            if self.img1_path in items:
                self.assertIn(self.img2_path, items)
                self.assertNotIn(self.img3_path, items)
                found_group_12 = True

        self.assertTrue(found_group_12)

    def test_find_similar_images(self):
        # Use a lower threshold to group img1, img2, img3
        # img4 is different
        self.deduplicator.similarity_threshold = 80.0
        images = [self.img1_path, self.img2_path, self.img3_path, self.img4_path]
        hash_map = self.deduplicator.build_hash_map(images, algorithm='phash')

        groups = self.deduplicator.find_similar_images(hash_map)

        # Expect group with [img1, img2, img3]
        found_group = False
        for group in groups:
            items = set(group.items)
            if self.img1_path in items:
                # check if img3 is also there (it should be very similar)
                # 1 pixel change in 100x100 is insignificant for phash
                self.assertIn(self.img3_path, items)
                self.assertNotIn(self.img4_path, items)
                found_group = True
        self.assertTrue(found_group)

if __name__ == '__main__':
    unittest.main()
