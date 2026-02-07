import unittest
import io
import base64
from PIL import Image
import numpy as np

from src.hash_calculator import ImageHashCalculator, HashResult

class TestImageHashCalculator(unittest.TestCase):

    def setUp(self):
        self.calculator = ImageHashCalculator()

        # Create a simple test image (10x10 white square)
        self.test_image = Image.new('RGB', (10, 10), color='white')
        self.test_image_bytes = io.BytesIO()
        self.test_image.save(self.test_image_bytes, format='PNG')
        self.test_image_bytes = self.test_image_bytes.getvalue()

        self.test_b64 = base64.b64encode(self.test_image_bytes).decode('utf-8')

    def test_load_image_from_bytes(self):
        img = self.calculator.load_image_from_bytes(self.test_image_bytes)
        self.assertIsInstance(img, Image.Image)
        self.assertEqual(img.size, (10, 10))

    def test_load_image_from_base64(self):
        img = self.calculator.load_image_from_base64(self.test_b64)
        self.assertIsInstance(img, Image.Image)
        self.assertEqual(img.size, (10, 10))

    def test_calculate_perceptual_hash(self):
        result = self.calculator.calculate_perceptual_hash(self.test_image, algorithm='phash')
        self.assertIsInstance(result, HashResult)
        self.assertEqual(result.algorithm, 'phash')
        self.assertIsInstance(result.hash_value, str)
        self.assertGreater(len(result.hash_value), 0)

    def test_calculate_cryptographic_hash(self):
        result = self.calculator.calculate_cryptographic_hash(self.test_image_bytes, algorithm='sha256')
        self.assertIsInstance(result, HashResult)
        self.assertEqual(result.algorithm, 'sha256')
        self.assertEqual(len(result.hash_value), 64) # SHA256 is 64 hex chars

    def test_calculate_all_hashes(self):
        results = self.calculator.calculate_all_hashes(self.test_image, self.test_image_bytes)
        self.assertIn('phash', results)
        self.assertIn('sha256', results)
        self.assertIn('md5', results)

    def test_invalid_algorithm(self):
        with self.assertRaises(ValueError):
            self.calculator.calculate_perceptual_hash(self.test_image, algorithm='invalid')

    def test_calculate_all_hashes_without_bytes(self):
        # Should exclude crypto hashes
        results = self.calculator.calculate_all_hashes(self.test_image, image_bytes=None)
        self.assertIn('phash', results)
        self.assertNotIn('sha256', results)

if __name__ == '__main__':
    unittest.main()
