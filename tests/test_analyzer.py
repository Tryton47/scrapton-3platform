"""
Unit tests for utils/comment_analyzer.py.
"""
import unittest
from utils.comment_analyzer import (
    clean_comment_text,
    extract_mentions,
    is_likely_spam,
    detect_sentiment_polarity,
    analyze_comment,
)

class TestCommentAnalyzer(unittest.TestCase):
    def test_clean_comment_text(self):
        raw = "   Halo   semuanya!\n\nKeren   banget  videonya!   "
        expected = "Halo semuanya! Keren banget videonya!"
        self.assertEqual(clean_comment_text(raw), expected)
        self.assertEqual(clean_comment_text(""), "")

    def test_extract_mentions(self):
        text = "Cc ke @user_1 dan @user.2 juga @user_1 dong"
        mentions = extract_mentions(text)
        self.assertEqual(mentions, ["user_1", "user.2"])

    def test_sentiment_polarity_positive(self):
        text = "Kontennya sangat keren, bagus banget dan bermanfaat"
        label, score = detect_sentiment_polarity(text)
        self.assertEqual(label, "positive")
        self.assertGreater(score, 0.0)

    def test_sentiment_polarity_negative(self):
        text = "Produk ini sangat jelek, parah, dan mengecewakan, saya benci"
        label, score = detect_sentiment_polarity(text)
        self.assertEqual(label, "negative")
        self.assertLess(score, 0.0)

    def test_sentiment_polarity_neutral(self):
        text = "Besok pagi jam 8"
        label, score = detect_sentiment_polarity(text)
        self.assertEqual(label, "neutral")
        self.assertEqual(score, 0.0)

    def test_spam_detection(self):
        self.assertTrue(is_likely_spam("Yuk cek bio untuk info lengkap slot gacor"))
        self.assertTrue(is_likely_spam("Hubungi wa.me/62812345678 ya kak"))
        self.assertTrue(is_likely_spam("DM me for promo"))
        self.assertFalse(is_likely_spam("Terima kasih atas informasinya ya kak!"))

    def test_analyze_comment_pipeline(self):
        sample = {
            "comment_id": "c123",
            "author_username": "andi_dev",
            "content": "Keren banget bang @budi! Sangat suka",
            "likes_count": 5
        }
        enriched = analyze_comment(sample)
        self.assertEqual(enriched["sentiment"], "positive")
        self.assertEqual(enriched["mentions_count"], 1)
        self.assertFalse(enriched["is_spam"])
        self.assertIn("polarity_score", enriched)

if __name__ == "__main__":
    unittest.main()
