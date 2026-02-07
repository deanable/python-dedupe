import unittest
import os
import shutil
import tempfile
from PIL import Image

from src.utils import get_image_metadata, format_file_size, format_similarity_score, validate_image_format

class TestUtils(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.img_path = os.path.join(self.test_dir, 'img.png')
        self.img = Image.new('RGB', (10, 20), color='green')
        self.img.save(self.img_path)

        self.txt_path = os.path.join(self.test_dir, 'test.txt')
        with open(self.txt_path, 'w') as f:
            f.write('not an image')

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_get_image_metadata(self):
        meta = get_image_metadata(self.img_path)
        self.assertEqual(meta['width'], 10)
        self.assertEqual(meta['height'], 20)
        self.assertEqual(meta['format'], 'PNG')
        self.assertIn('file_size', meta)
        self.assertIn('mtime', meta)

    def test_format_file_size(self):
        self.assertEqual(format_file_size(500), "500.0 B")
        self.assertEqual(format_file_size(1024), "1.0 KB")
        self.assertEqual(format_file_size(1024 * 1024), "1.0 MB")
        self.assertEqual(format_file_size(1024 * 1024 * 1024), "1.0 GB")

    def test_format_similarity_score(self):
        self.assertEqual(format_similarity_score(95.123), "95.12%")
        self.assertEqual(format_similarity_score(100), "100.00%")
        self.assertEqual(format_similarity_score(0), "0.00%")

    def test_validate_image_format(self):
        self.assertTrue(validate_image_format(self.img_path))
        self.assertFalse(validate_image_format(self.txt_path))

if __name__ == '__main__':
    unittest.main()
