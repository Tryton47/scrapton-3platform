"""
Unit tests for TikTok profile and video item parsers.
"""
import unittest
from scrapers.tiktok_profile import parse_tiktok_profile_from_api
from scrapers.tiktok_post import parse_tiktok_video_item
from core.models import Platform

class TestTikTokParsers(unittest.TestCase):

    def test_parse_tiktok_profile(self):
        user_data = {
            "uniqueId": "creative_coder",
            "nickname": "Creative Coder ID",
            "signature": "Building scrapers in Python #tech #coding",
            "verified": True,
            "avatarLarger": "https://example.com/tt_avatar.jpg",
        }
        stats_data = {
            "followerCount": 250000,
            "followingCount": 420,
            "videoCount": 85,
        }
        profile = parse_tiktok_profile_from_api(user_data, stats_data)
        self.assertEqual(profile.platform, Platform.TIKTOK)
        self.assertEqual(profile.username, "creative_coder")
        self.assertEqual(profile.followers_count, 250000)
        self.assertTrue(profile.is_verified)
        self.assertEqual(profile.profile_url, "https://www.tiktok.com/@creative_coder")

    def test_parse_tiktok_video_item(self):
        item = {
            "id": "7199999999999999999",
            "desc": "Belajar Python Scraper Anti-Banned #coding #python #tutorial",
            "createTime": 1700000000,
            "author": {
                "uniqueId": "creative_coder",
            },
            "stats": {
                "diggCount": 12500,
                "commentCount": 340,
                "shareCount": 980,
                "playCount": 150000,
                "collectCount": 2100,
            },
            "video": {
                "cover": "https://example.com/cover.jpg",
                "duration": 45,
            },
            "music": {
                "title": "Original Sound - Creative Coder",
            }
        }
        post = parse_tiktok_video_item(item)
        self.assertEqual(post.id, "7199999999999999999")
        self.assertEqual(post.platform, Platform.TIKTOK)
        self.assertEqual(post.author_username, "creative_coder")
        self.assertEqual(post.metrics.likes, 12500)
        self.assertEqual(post.metrics.views, 150000)
        self.assertIn("python", post.hashtags)
        self.assertEqual(post.extra_metadata["music_title"], "Original Sound - Creative Coder")

if __name__ == "__main__":
    unittest.main()
