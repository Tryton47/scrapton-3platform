"""
Unit tests for utils/filter_engine.py.
"""
import unittest
from utils.filter_engine import (
    CommentFilterCriteria,
    filter_comments,
    sort_comments,
)

class TestFilterEngine(unittest.TestCase):
    def setUp(self):
        self.sample_comments = [
            {
                "id": "1",
                "content": "Keren banget bang, sangat suka!",
                "author_username": "andi_dev",
                "likes_count": 50,
                "sentiment": "positive",
                "is_spam": False,
                "platform": "tiktok",
                "reply_to_id": None,
            },
            {
                "id": "2",
                "content": "Cek bio untuk bonus deposit gacor",
                "author_username": "bot_promo",
                "likes_count": 0,
                "sentiment": "neutral",
                "is_spam": True,
                "platform": "tiktok",
                "reply_to_id": None,
            },
            {
                "id": "3",
                "content": "Jelek dan sangat mengecewakan",
                "author_username": "budi_user",
                "likes_count": 15,
                "sentiment": "negative",
                "is_spam": False,
                "platform": "instagram",
                "reply_to_id": "1",
            },
        ]

    def test_filter_by_keyword(self):
        criteria = CommentFilterCriteria(keyword="keren")
        res = filter_comments(self.sample_comments, criteria)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["id"], "1")

    def test_filter_by_min_likes(self):
        criteria = CommentFilterCriteria(min_likes=20)
        res = filter_comments(self.sample_comments, criteria)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["id"], "1")

    def test_filter_exclude_spam(self):
        criteria = CommentFilterCriteria(exclude_spam=True)
        res = filter_comments(self.sample_comments, criteria)
        self.assertEqual(len(res), 2)
        ids = [r["id"] for r in res]
        self.assertNotIn("2", ids)

    def test_filter_by_sentiment(self):
        criteria = CommentFilterCriteria(sentiment="positive")
        res = filter_comments(self.sample_comments, criteria)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["sentiment"], "positive")

    def test_filter_by_platform(self):
        criteria = CommentFilterCriteria(platform="instagram")
        res = filter_comments(self.sample_comments, criteria)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["platform"], "instagram")

    def test_sort_comments_by_likes(self):
        sorted_list = sort_comments(self.sample_comments, by="likes", descending=True)
        self.assertEqual(sorted_list[0]["id"], "1")
        self.assertEqual(sorted_list[-1]["id"], "2")

if __name__ == "__main__":
    unittest.main()
