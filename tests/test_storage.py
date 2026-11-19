"""
Unit tests for core/storage.py with SocialComment datasets.
"""
import tempfile
import unittest
from pathlib import Path
from core.models import Platform, SocialComment
from core.storage import StorageManager

class TestStorageManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.storage = StorageManager(self.temp_dir.name)
        self.sample_comments = [
            SocialComment(
                id="c1",
                platform=Platform.TIKTOK,
                post_url="https://tiktok.com/@u/video/1",
                author_username="user1",
                author_nickname="User One",
                content="Komentar pertama",
                likes_count=10,
                reply_count=2,
            ),
            SocialComment(
                id="c2",
                platform=Platform.INSTAGRAM,
                post_url="https://instagram.com/p/abc",
                author_username="user2",
                content="Komentar kedua",
                likes_count=5,
            ),
        ]

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_save_comments_to_json(self):
        path = self.storage.save_to_json(self.sample_comments, "test.json")
        self.assertTrue(path.exists())
        self.assertGreater(path.stat().st_size, 0)

    def test_save_comments_to_jsonl(self):
        path = self.storage.save_to_jsonl(self.sample_comments, "test.jsonl")
        self.assertTrue(path.exists())
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        self.assertEqual(len(lines), 2)

    def test_save_comments_to_csv(self):
        path = self.storage.save_to_csv(self.sample_comments, "test.csv")
        self.assertTrue(path.exists())
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("user1", content)
        self.assertIn("user2", content)

    def test_save_comments_all_formats(self):
        exports = self.storage.save_comments(self.sample_comments, "batch_export")
        self.assertEqual(len(exports), 4)
        for fmt, p in exports.items():
            self.assertTrue(p.exists(), f"Format {fmt} file does not exist")

if __name__ == "__main__":
    unittest.main()
