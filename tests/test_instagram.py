"""
Unit tests for data parsing, metric abbreviations, and Instagram model parsers.
"""
import unittest
from utils.parser import clean_text, extract_hashtags, parse_abbreviated_number
from scrapers.instagram_profile import parse_profile_from_api_json
from scrapers.instagram_post import parse_instagram_post_node

class TestParserUtils(unittest.TestCase):

    def test_parse_abbreviated_number(self):
        self.assertEqual(parse_abbreviated_number("10.5K"), 10500)
        self.assertEqual(parse_abbreviated_number("1.2M"), 1200000)
        self.assertEqual(parse_abbreviated_number("2B"), 2000000000)
        self.assertEqual(parse_abbreviated_number("1,540"), 1540)
        self.assertEqual(parse_abbreviated_number(500), 500)
        self.assertEqual(parse_abbreviated_number(None), 0)

    def test_extract_hashtags(self):
        caption = "Exploring Bali! #travel #wanderlust #indonesia2026"
        tags = extract_hashtags(caption)
        self.assertEqual(tags, ["travel", "wanderlust", "indonesia2026"])

    def test_clean_text(self):
        dirty = "  Halo \n\n dunia   scraper   "
        self.assertEqual(clean_text(dirty), "Halo dunia scraper")

class TestInstagramParsers(unittest.TestCase):

    def test_parse_profile(self):
        fake_api_response = {
            "data": {
                "user": {
                    "username": "dummy_creator",
                    "full_name": "Dummy Creator",
                    "biography": "Official account #creator",
                    "edge_followed_by": {"count": 15000},
                    "edge_follow": {"count": 120},
                    "edge_owner_to_timeline_media": {"count": 45},
                    "is_verified": True,
                    "profile_pic_url": "https://example.com/pic.jpg"
                }
            }
        }
        profile = parse_profile_from_api_json(fake_api_response)
        self.assertEqual(profile.username, "dummy_creator")
        self.assertEqual(profile.followers_count, 15000)
        self.assertTrue(profile.is_verified)

    def test_parse_post_node(self):
        fake_node = {
            "id": "123456789",
            "shortcode": "CxAbCdEf",
            "taken_at_timestamp": 1700000000,
            "edge_media_to_caption": {"edges": [{"node": {"text": "Hello world #test"}}]},
            "edge_media_preview_like": {"count": 250},
            "edge_media_to_comment": {"count": 15},
            "display_url": "https://example.com/photo.jpg",
            "is_video": False,
        }
        post = parse_instagram_post_node(fake_node, default_author="dummy_creator")
        self.assertEqual(post.id, "123456789")
        self.assertEqual(post.url, "https://www.instagram.com/p/CxAbCdEf/")
        self.assertEqual(post.metrics.likes, 250)
        self.assertEqual(post.hashtags, ["test"])

if __name__ == "__main__":
    unittest.main()
