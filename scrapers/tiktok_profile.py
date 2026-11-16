"""
Profile parser for TikTok user accounts.
Parses structured JSON payloads (SIGI_STATE / UniversalData) or DOM elements into UserProfile.
"""
from typing import Any
from core.models import Platform, UserProfile
from utils.parser import clean_text

def parse_tiktok_profile_from_api(user_data: dict[str, Any], stats_data: dict[str, Any] | None = None) -> UserProfile:
    """
    Parse TikTok profile data from internal JSON structures.
    """
    stats = stats_data or user_data.get("stats", {})
    username = user_data.get("uniqueId") or user_data.get("unique_id", "")
    nickname = user_data.get("nickname", "")
    signature = user_data.get("signature", "")

    return UserProfile(
        platform=Platform.TIKTOK,
        username=username,
        display_name=clean_text(nickname),
        bio=clean_text(signature),
        followers_count=stats.get("followerCount", 0),
        following_count=stats.get("followingCount", 0),
        posts_count=stats.get("videoCount", 0),
        is_verified=user_data.get("verified", False),
        profile_url=f"https://www.tiktok.com/@{username}",
        avatar_url=user_data.get("avatarLarger") or user_data.get("avatarMedium"),
    )
