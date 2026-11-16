"""
User profile parser for X (Twitter).
Parses GraphQL UserResultByRestId / UserByScreenName responses into standardized UserProfile.
"""
from typing import Any
from core.models import Platform, UserProfile
from utils.parser import clean_text

def parse_twitter_profile(data: dict[str, Any]) -> UserProfile:
    """
    Extracts profile metadata from Twitter GraphQL user result dictionary.
    """
    user_res = data.get("result", {})
    if not user_res:
        user_res = data.get("data", {}).get("user", {}).get("result", {})

    legacy = user_res.get("legacy", {})
    username = legacy.get("screen_name") or user_res.get("core", {}).get("screen_name", "")
    name = legacy.get("name") or user_res.get("core", {}).get("name", "")
    description = legacy.get("description", "")
    avatar = legacy.get("profile_image_url_https", "")

    # High res avatar replacement
    if avatar:
        avatar = avatar.replace("_normal.", ".")

    is_verified = (
        user_res.get("is_blue_verified", False) or
        legacy.get("verified", False) or
        user_res.get("verification_info", {}).get("is_identity_verified", False)
    )

    return UserProfile(
        platform=Platform.TWITTER,
        username=username,
        display_name=clean_text(name),
        bio=clean_text(description),
        followers_count=legacy.get("followers_count", 0),
        following_count=legacy.get("friends_count", 0),
        posts_count=legacy.get("statuses_count", 0),
        is_verified=is_verified,
        profile_url=f"https://x.com/{username}",
        avatar_url=avatar,
    )
