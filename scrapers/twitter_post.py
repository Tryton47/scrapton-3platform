"""
Tweet & Media parser for X (Twitter).
Parses GraphQL tweet results into standardized SocialPost objects.
"""
from datetime import datetime, timezone
from typing import Any
from core.models import EngagementMetrics, Platform, SocialPost
from utils.parser import clean_text, extract_hashtags

def parse_twitter_tweet_result(tweet_result: dict[str, Any], default_author: str = "") -> SocialPost | None:
    """
    Parses a tweet node inside GraphQL timeline entries.
    """
    if not tweet_result:
        return None

    # Handle tweet result variants (TweetWithVisibilityResults or Tweet)
    raw_tweet = tweet_result.get("tweet", tweet_result)
    legacy = raw_tweet.get("legacy", {})
    if not legacy:
        return None

    tweet_id = str(raw_tweet.get("rest_id") or legacy.get("id_str", ""))
    full_text = legacy.get("full_text", "")
    author = default_author

    # Try extracting author from core
    core = raw_tweet.get("core", {})
    user_results = core.get("user_results", {}).get("result", {})
    if user_results:
        author = (
            user_results.get("legacy", {}).get("screen_name") or
            user_results.get("core", {}).get("screen_name") or
            default_author
        )

    # Created at: "Mon Nov 16 12:00:00 +0000 2026"
    created_at_str = legacy.get("created_at")
    created_at = None
    if created_at_str:
        try:
            created_at = datetime.strptime(created_at_str, "%a %b %d %H:%M:%S %z %Y")
        except Exception:
            created_at = None

    # Engagement metrics
    likes = legacy.get("favorite_count", 0)
    comments = legacy.get("reply_count", 0)
    retweets = legacy.get("retweet_count", 0)
    bookmarks = legacy.get("bookmark_count", 0)
    views_info = raw_tweet.get("views", {})
    views = int(views_info.get("count", 0)) if views_info.get("count") else 0

    # Media URLs
    media_urls: list[str] = []
    entities_media = legacy.get("extended_entities", {}).get("media", []) or legacy.get("entities", {}).get("media", [])
    for m in entities_media:
        url = m.get("media_url_https") or m.get("media_url")
        if url and url not in media_urls:
            media_urls.append(url)

    url = f"https://x.com/{author}/status/{tweet_id}" if author and tweet_id else ""

    return SocialPost(
        id=tweet_id,
        platform=Platform.TWITTER,
        author_username=author,
        content=clean_text(full_text),
        url=url,
        created_at=created_at,
        metrics=EngagementMetrics(
            likes=likes,
            comments=comments,
            shares=retweets,
            views=views,
            bookmarks=bookmarks,
        ),
        media_urls=media_urls,
        hashtags=extract_hashtags(full_text),
        extra_metadata={
            "retweet_count": retweets,
            "lang": legacy.get("lang"),
            "is_quote_status": legacy.get("is_quote_status", False),
        }
    )
