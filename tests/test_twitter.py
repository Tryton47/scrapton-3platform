"""
Unit tests for X (Twitter) profile and tweet node parsers.
"""
import unittest
from core.models import Platform
from scrapers.twitter_profile import parse_twitter_profile
from scrapers.twitter_post import parse_twitter_tweet_result

class TestTwitterParsers(unittest.TestCase):

    def test_parse_twitter_profile(self):
        user_graphql_data = {
            "result": {
                "legacy": {
                    "screen_name": "tech_pioneer",
                    "name": "Tech Pioneer",
                    "description": "Building cool open source tools #python #ai",
                    "followers_count": 89000,
                    "friends_count": 350,
                    "statuses_count": 4200,
                    "verified": True,
                    "profile_image_url_https": "https://pbs.twimg.com/profile_images/123_normal.jpg",
                },
                "is_blue_verified": True,
            }
        }
        profile = parse_twitter_profile(user_graphql_data)
        self.assertEqual(profile.platform, Platform.TWITTER)
        self.assertEqual(profile.username, "tech_pioneer")
        self.assertEqual(profile.display_name, "Tech Pioneer")
        self.assertEqual(profile.followers_count, 89000)
        self.assertTrue(profile.is_verified)
        self.assertEqual(profile.profile_url, "https://x.com/tech_pioneer")
        self.assertEqual(profile.avatar_url, "https://pbs.twimg.com/profile_images/123.jpg")

    def test_parse_twitter_tweet(self):
        tweet_result = {
            "rest_id": "1800000000000000000",
            "core": {
                "user_results": {
                    "result": {
                        "legacy": {
                            "screen_name": "tech_pioneer"
                        }
                    }
                }
            },
            "legacy": {
                "id_str": "1800000000000000000",
                "full_text": "Release 2.0 is out now! Check out the repo #opensource #python",
                "created_at": "Mon Nov 16 10:00:00 +0000 2026",
                "favorite_count": 1400,
                "reply_count": 85,
                "retweet_count": 320,
                "bookmark_count": 150,
                "extended_entities": {
                    "media": [
                        {"media_url_https": "https://pbs.twimg.com/media/preview.jpg"}
                    ]
                }
            },
            "views": {
                "count": "45000"
            }
        }
        post = parse_twitter_tweet_result(tweet_result)
        self.assertIsNotNone(post)
        self.assertEqual(post.id, "1800000000000000000")
        self.assertEqual(post.platform, Platform.TWITTER)
        self.assertEqual(post.author_username, "tech_pioneer")
        self.assertEqual(post.metrics.likes, 1400)
        self.assertEqual(post.metrics.comments, 85)
        self.assertEqual(post.metrics.shares, 320)
        self.assertEqual(post.metrics.views, 45000)
        self.assertIn("python", post.hashtags)
        self.assertEqual(len(post.media_urls), 1)

if __name__ == "__main__":
    unittest.main()
