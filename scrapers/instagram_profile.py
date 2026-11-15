"""
Profile parser and extractor for Instagram.
Extracts user stats, bio, followers count, verification status, and avatar.
"""
from typing import Any
from core.models import Platform, UserProfile
from utils.parser import clean_text

def parse_profile_from_api_json(data: dict[str, Any]) -> UserProfile:
    """Parse profile directly from web_profile_info response."""
    user = data.get("data", {}).get("user", {})
    if not user:
        raise ValueError("Invalid profile response from Instagram API")

    return UserProfile(
        platform=Platform.INSTAGRAM,
        username=user.get("username", ""),
        display_name=clean_text(user.get("full_name")),
        bio=clean_text(user.get("biography")),
        followers_count=user.get("edge_followed_by", {}).get("count", 0),
        following_count=user.get("edge_follow", {}).get("count", 0),
        posts_count=user.get("edge_owner_to_timeline_media", {}).get("count", 0),
        is_verified=user.get("is_verified", False),
        profile_url=f"https://www.instagram.com/{user.get('username')}/",
        avatar_url=user.get("profile_pic_url_hd") or user.get("profile_pic_url"),
    )
