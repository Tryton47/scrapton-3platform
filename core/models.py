"""
Standardized Pydantic data schemas across Instagram, TikTok, and X (Twitter).
"""
from datetime import datetime
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field

class Platform(str, Enum):
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"

class UserProfile(BaseModel):
    """Standardized user profile schema."""
    platform: Platform
    username: str
    display_name: str | None = None
    bio: str | None = None
    followers_count: int = 0
    following_count: int = 0
    posts_count: int = 0
    is_verified: bool = False
    profile_url: str
    avatar_url: str | None = None
    scraped_at: datetime = Field(default_factory=datetime.utcnow)

class EngagementMetrics(BaseModel):
    """Engagement metrics for a post/tweet/video."""
    likes: int = 0
    comments: int = 0
    shares: int = 0
    views: int = 0
    bookmarks: int = 0

class SocialPost(BaseModel):
    """Standardized post/video/tweet schema."""
    id: str
    platform: Platform
    author_username: str
    content: str = ""
    url: str
    created_at: datetime | None = None
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    metrics: EngagementMetrics = Field(default_factory=EngagementMetrics)
    media_urls: list[str] = Field(default_factory=list)
    hashtags: list[str] = Field(default_factory=list)
    extra_metadata: dict[str, Any] = Field(default_factory=dict)
