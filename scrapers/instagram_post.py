"""
Post and Reel extractor for Instagram.
Parses GraphQL node dictionaries into standardized SocialPost objects.
"""
from datetime import datetime, timezone
from typing import Any
from core.models import EngagementMetrics, Platform, SocialPost
from utils.parser import clean_text, extract_hashtags

def parse_instagram_post_node(node: dict[str, Any], default_author: str = "") -> SocialPost:
    """
    Parses a single post/reel GraphQL node into unified SocialPost model.
    """
    post_id = node.get("id") or node.get("shortcode") or ""
    shortcode = node.get("shortcode", "")
    url = f"https://www.instagram.com/p/{shortcode}/" if shortcode else ""

    # Caption extraction
    edges = node.get("edge_media_to_caption", {}).get("edges", [])
    caption = ""
    if edges:
        caption = clean_text(edges[0].get("node", {}).get("text", ""))

    # Timestamps
    taken_at_timestamp = node.get("taken_at_timestamp")
    created_at = datetime.fromtimestamp(taken_at_timestamp, timezone.utc) if taken_at_timestamp else None

    # Author
    author = node.get("owner", {}).get("username") or default_author

    # Engagement metrics
    likes = node.get("edge_media_preview_like", {}).get("count") or node.get("edge_liked_by", {}).get("count", 0)
    comments = node.get("edge_media_to_comment", {}).get("count", 0)
    views = node.get("video_view_count", 0)

    # Media items (Images/Video URLs)
    media_urls: list[str] = []
    display_url = node.get("display_url")
    if display_url:
        media_urls.append(display_url)

    # Carousel sidecar
    sidecar_edges = node.get("edge_sidecar_to_children", {}).get("edges", [])
    for child in sidecar_edges:
        child_node = child.get("node", {})
        child_display = child_node.get("display_url")
        if child_display and child_display not in media_urls:
            media_urls.append(child_display)

    return SocialPost(
        id=str(post_id),
        platform=Platform.INSTAGRAM,
        author_username=author,
        content=caption,
        url=url,
        created_at=created_at,
        metrics=EngagementMetrics(
            likes=likes,
            comments=comments,
            views=views,
        ),
        media_urls=media_urls,
        hashtags=extract_hashtags(caption),
        extra_metadata={
            "is_video": node.get("is_video", False),
            "shortcode": shortcode,
            "typename": node.get("__typename"),
        }
    )
