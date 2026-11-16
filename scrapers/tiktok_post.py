"""
Video post parser for TikTok items.
Extracts video metadata, metrics (likes, views, comments, shares), and sounds.
"""
from datetime import datetime, timezone
from typing import Any
from core.models import EngagementMetrics, Platform, SocialPost
from utils.parser import clean_text, extract_hashtags

def parse_tiktok_video_item(item: dict[str, Any], default_author: str = "") -> SocialPost:
    """
    Parses a single TikTok item dictionary into standardized SocialPost.
    """
    video_id = str(item.get("id") or item.get("aweme_id") or "")
    author_info = item.get("author", {})
    author = author_info.get("uniqueId") or author_info.get("unique_id") or default_author

    desc = item.get("desc") or ""
    clean_desc = clean_text(desc)

    # Timestamps
    create_time = item.get("createTime") or item.get("create_time")
    created_at = None
    if create_time:
        try:
            created_at = datetime.fromtimestamp(int(create_time), timezone.utc)
        except Exception:
            created_at = None

    # Stats
    stats = item.get("stats", {}) or item.get("statistics", {})
    likes = stats.get("diggCount") or stats.get("digg_count", 0)
    comments = stats.get("commentCount") or stats.get("comment_count", 0)
    shares = stats.get("shareCount") or stats.get("share_count", 0)
    views = stats.get("playCount") or stats.get("play_count", 0)
    bookmarks = stats.get("collectCount") or stats.get("collect_count", 0)

    # Media & Video URLs
    media_urls: list[str] = []
    video_info = item.get("video", {})
    cover = video_info.get("cover") or video_info.get("originCover")
    if cover:
        media_urls.append(cover)

    # Music / Audio
    music = item.get("music", {})
    music_title = music.get("title")

    url = f"https://www.tiktok.com/@{author}/video/{video_id}" if author and video_id else ""

    return SocialPost(
        id=video_id,
        platform=Platform.TIKTOK,
        author_username=author,
        content=clean_desc,
        url=url,
        created_at=created_at,
        metrics=EngagementMetrics(
            likes=likes,
            comments=comments,
            shares=shares,
            views=views,
            bookmarks=bookmarks,
        ),
        media_urls=media_urls,
        hashtags=extract_hashtags(desc),
        extra_metadata={
            "music_title": music_title,
            "duration": video_info.get("duration", 0),
        }
    )
