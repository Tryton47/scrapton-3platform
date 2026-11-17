"""
Unit tests for comment models and URL platform detection.
"""
import unittest
from core.models import Platform, SocialComment
from scrapers.comment_scraper import detect_platform_from_url

class TestCommentScraper(unittest.TestCase):

    def test_detect_platform_from_url(self):
        self.assertEqual(detect_platform_from_url("https://www.tiktok.com/@user/video/123"), Platform.TIKTOK)
        self.assertEqual(detect_platform_from_url("https://www.instagram.com/p/ABCxyz/"), Platform.INSTAGRAM)
        self.assertEqual(detect_platform_from_url("https://x.com/user/status/789"), Platform.TWITTER)
        self.assertEqual(detect_platform_from_url("https://twitter.com/user/status/789"), Platform.TWITTER)
        self.assertIsNone(detect_platform_from_url("https://facebook.com/post/1"))

    def test_social_comment_model(self):
        comment = SocialComment(
            id="c_123",
            platform=Platform.TIKTOK,
            post_url="https://tiktok.com/@user/video/1",
            author_username="john_doe",
            content="Mantap tutorialnya!",
            likes_count=45,
            reply_count=2
        )
        self.assertEqual(comment.author_username, "john_doe")
        self.assertEqual(comment.likes_count, 45)
        self.assertEqual(comment.reply_count, 2)

if __name__ == "__main__":
    unittest.main()
