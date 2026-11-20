"""
Unit tests for utils/url_parser.py.
"""
import unittest
from utils.url_parser import (
    normalize_url,
    is_shortlink,
    extract_post_id,
    parse_social_url,
)

class TestUrlParser(unittest.TestCase):
    def test_normalize_url(self):
        url_with_query = "https://www.tiktok.com/@creator/video/1234567890?is_from_webapp=1&sender_device=pc"
        normalized = normalize_url(url_with_query)
        self.assertEqual(normalized, "https://www.tiktok.com/@creator/video/1234567890")

    def test_extract_tiktok_id(self):
        url = "https://www.tiktok.com/@user/video/7123456789012345678"
        post_id = extract_post_id(url)
        self.assertEqual(post_id, "7123456789012345678")

    def test_extract_instagram_shortcode(self):
        url_post = "https://www.instagram.com/p/DFxyz123_45/?utm_source=ig_web"
        url_reel = "https://www.instagram.com/reel/C-abcDEFghi/"
        self.assertEqual(extract_post_id(url_post), "DFxyz123_45")
        self.assertEqual(extract_post_id(url_reel), "C-abcDEFghi")

    def test_extract_twitter_id(self):
        url = "https://x.com/elonmusk/status/1887654321098765432"
        self.assertEqual(extract_post_id(url), "1887654321098765432")

    def test_shortlink_detection(self):
        self.assertTrue(is_shortlink("https://vm.tiktok.com/ZM8abcDEF/"))
        self.assertTrue(is_shortlink("https://vt.tiktok.com/ZSxyz123/"))
        self.assertTrue(is_shortlink("https://t.co/xyz123"))
        self.assertFalse(is_shortlink("https://www.instagram.com/p/abc123/"))

    def test_parse_social_url(self):
        res = parse_social_url("https://www.tiktok.com/@test/video/9988776655")
        self.assertEqual(res["platform"], "tiktok")
        self.assertEqual(res["post_id"], "9988776655")
        self.assertFalse(res["is_shortlink"])

if __name__ == "__main__":
    unittest.main()
