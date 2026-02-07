# Python Dedupe 🖼️

A powerful Python library for detecting duplicate and similar images using perceptual and cryptographic hashing algorithms.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Tests](https://img.shields.io/badge/tests-28%20passing-brightgreen.svg)

## ✨ Features

- **Multiple Hash Algorithms**
  - **Perceptual Hashes**: pHash, dHash, aHash, wHash - detect visually similar images even with modifications
  - **Cryptographic Hashes**: MD5, SHA1, SHA256, SHA512 - detect byte-identical duplicates

- **Smart Deduplication**
  - Find exact duplicates (identical files)
  - Find similar images based on configurable similarity threshold
  - Transitive grouping using Union-Find algorithm

- **Flexible Keep Strategies**
  - `LARGEST` - Keep the largest file
  - `OLDEST` - Keep the oldest file (by modification time)
  - `NEWEST` - Keep the newest file
  - `FIRST` - Keep the first file encountered
  - `MANUAL` - Flag for manual review

- **Multiple Storage Formats**
  - JSON serialization
  - Delimited string format
  - Raw dictionary format

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/deanable/python-dedupe.git
cd python-dedupe

# Install dependencies
pip install -r requirements.txt
```

### Requirements

- Python 3.8+
- Pillow
- ImageHash
- NumPy

## 🚀 Quick Start

### Basic Usage

```python
from src import ImageDeduplicator, KeepStrategy, generate_dedup_plan

# Initialize the deduplicator with 95% similarity threshold
deduplicator = ImageDeduplicator(similarity_threshold=95.0)

# List of images to analyze
images = [
    "photos/vacation1.jpg",
    "photos/vacation1_copy.jpg",
    "photos/vacation2.jpg",
    "photos/edited_vacation1.jpg"
]

# Build hash map using perceptual hash
hash_map = deduplicator.build_hash_map(images, algorithm='phash')

# Find exact duplicates (identical hashes)
exact_groups = deduplicator.find_exact_duplicates(hash_map)

# Find similar images (within threshold)
similar_groups = deduplicator.find_similar_images(hash_map)

# Generate deduplication plan
decisions = generate_dedup_plan(similar_groups, KeepStrategy.LARGEST)

for decision in decisions:
    print(f"Keep: {decision.keep_item}")
    print(f"Remove: {decision.remove_items}")
    print(f"Reason: {decision.reason}")
```

### Calculate Individual Hashes

```python
from src import ImageHashCalculator

calculator = ImageHashCalculator()

# Load image and calculate perceptual hash
image = calculator.load_image_from_path("photo.jpg")
result = calculator.calculate_perceptual_hash(image, algorithm='phash')

print(f"Hash: {result.hash_value}")
print(f"Algorithm: {result.algorithm}")
print(f"Bit Length: {result.bit_length}")

# Calculate cryptographic hash from file bytes
with open("photo.jpg", "rb") as f:
    file_bytes = f.read()
    
crypto_result = calculator.calculate_cryptographic_hash(file_bytes, algorithm='sha256')
print(f"SHA256: {crypto_result.hash_value}")
```

### Compare Hashes

```python
from src import (
    calculate_hamming_distance,
    calculate_similarity_percentage,
    are_hashes_similar,
    are_hashes_exact_match
)

hash1 = "a1b2c3d4e5f6a7b8"
hash2 = "a1b2c3d4e5f6a7b9"

# Calculate Hamming distance (number of differing bits)
distance = calculate_hamming_distance(hash1, hash2)
print(f"Hamming Distance: {distance}")

# Calculate similarity percentage
bit_length = len(hash1) * 4  # 4 bits per hex character
similarity = calculate_similarity_percentage(distance, bit_length)
print(f"Similarity: {similarity:.2f}%")

# Check if similar within threshold
is_similar = are_hashes_similar(hash1, hash2, threshold=90.0)
print(f"Are similar (90%+): {is_similar}")

# Check exact match
is_exact = are_hashes_exact_match(hash1, hash2)
print(f"Exact match: {is_exact}")
```

### Store and Retrieve Hashes

```python
from src import (
    ImageHashCalculator,
    HashFormat,
    format_hash_for_storage,
    parse_hash_from_storage
)

calculator = ImageHashCalculator()
image = calculator.load_image_from_path("photo.jpg")

with open("photo.jpg", "rb") as f:
    image_bytes = f.read()

# Calculate all hashes
all_hashes = calculator.calculate_all_hashes(image, image_bytes)

# Store as JSON
json_str = format_hash_for_storage(all_hashes, HashFormat.JSON)
print(json_str)

# Store as delimited string (compact)
delimited_str = format_hash_for_storage(all_hashes, HashFormat.DELIMITED)
print(delimited_str)  # "ahash:abc123|dhash:def456|..."

# Parse back from storage
parsed = parse_hash_from_storage(json_str, HashFormat.JSON)
```

## 📖 API Reference

### Core Classes

#### `ImageHashCalculator`

| Method | Description |
|--------|-------------|
| `load_image_from_path(path)` | Load image from file path |
| `load_image_from_bytes(data)` | Load image from bytes |
| `load_image_from_base64(b64)` | Load image from base64 string |
| `calculate_perceptual_hash(image, algorithm)` | Calculate perceptual hash |
| `calculate_cryptographic_hash(bytes, algorithm)` | Calculate cryptographic hash |
| `calculate_all_hashes(image, bytes)` | Calculate all supported hashes |

#### `ImageDeduplicator`

| Method | Description |
|--------|-------------|
| `build_hash_map(images, algorithm)` | Generate hash map for list of images |
| `find_exact_duplicates(hash_map)` | Find groups with identical hashes |
| `find_similar_images(hash_map, threshold)` | Find groups within similarity threshold |

#### `KeepStrategy` (Enum)

| Value | Description |
|-------|-------------|
| `LARGEST` | Keep the file with largest size |
| `OLDEST` | Keep the file with oldest modification time |
| `NEWEST` | Keep the file with newest modification time |
| `FIRST` | Keep the first file in the group |
| `MANUAL` | Defer to manual review |

### Data Classes

#### `HashResult`
```python
@dataclass
class HashResult:
    hash_value: str      # The computed hash
    algorithm: str       # Algorithm used (e.g., 'phash', 'sha256')
    timestamp: float     # When hash was computed
    bit_length: int      # Hash bit length
    metadata: Dict       # Additional metadata
```

#### `DuplicateGroup`
```python
@dataclass
class DuplicateGroup:
    items: List[str]                    # Image paths in group
    similarity_scores: Dict[str, float] # Similarity to pivot
    hash_type: str                      # Algorithm used
```

#### `DedupDecision`
```python
@dataclass
class DedupDecision:
    keep_item: Optional[str]  # Item to keep
    remove_items: List[str]   # Items to remove
    reason: str               # Explanation
```

## 🏗️ Architecture

```
python-dedupe/
├── src/
│   ├── __init__.py          # Public API exports
│   ├── hash_calculator.py   # Hash computation (perceptual + crypto)
│   ├── hash_comparison.py   # Hamming distance & similarity
│   ├── hash_storage.py      # Serialization formats
│   ├── dedup_engine.py      # Core deduplication engine
│   ├── dedup_strategies.py  # Keep strategy implementations
│   └── utils.py             # Utility functions
├── tests/                   # Unit tests
├── requirements.txt         # Dependencies
└── README.md               # This file
```

### Algorithm Details

**Perceptual Hashing**: Converts images to small fingerprints that remain similar even after resizing, compression, or minor edits. Uses the [ImageHash](https://github.com/JohannesBuchner/imagehash) library.

**Similarity Grouping**: Uses the Union-Find (Disjoint Set Union) algorithm to efficiently group transitively similar images. If A is similar to B, and B is similar to C, then A, B, and C are all in the same group.

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_hash_calculator.py -v

# Run with unittest
python -m unittest discover tests -v
```

**Test Coverage**: 28 tests covering all modules

## 📋 Supported Formats

| Hash Type | Algorithms |
|-----------|------------|
| Perceptual | pHash, dHash, aHash, wHash |
| Cryptographic | MD5, SHA1, SHA256, SHA512 |

| Image Formats | Support |
|---------------|---------|
| JPEG, PNG, GIF, BMP, TIFF, WebP | ✅ Full |
| HEIC, RAW formats | Via Pillow plugins |

## 🔮 Future Enhancements

- [ ] CLI interface (`python -m python_dedupe`)
- [ ] Locality-Sensitive Hashing (LSH) for O(N) similarity search
- [ ] Async/parallel hash computation
- [ ] Progress callbacks for large batches
- [ ] Database backend for hash persistence

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

Made with ❤️ by [deanable](https://github.com/deanable)
