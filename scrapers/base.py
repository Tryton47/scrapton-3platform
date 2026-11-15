"""
Base abstract class for all social media platform scrapers.
Provides unified interface, random human-like delays, and logging.
"""
import abc
import asyncio
import random
from typing import AsyncGenerator
from config.settings import settings
from core.models import Platform, SocialPost, UserProfile

class BaseScraper(abc.ABC):
    """Abstract Base Class for Instagram, TikTok, and Twitter scrapers."""

    def __init__(self, platform: Platform):
        self.platform = platform
        self.min_delay = settings.min_delay
        self.max_delay = settings.max_delay

    async def human_delay(self, multiplier: float = 1.0) -> None:
        """Introduce randomized delay to emulate human browsing behavior."""
        delay = random.uniform(self.min_delay, self.max_delay) * multiplier
        await asyncio.sleep(delay)

    @abc.abstractmethod
    async def get_profile(self, username: str) -> UserProfile:
        """Fetch user profile details."""
        pass

    @abc.abstractmethod
    async def get_user_posts(self, username: str, limit: int = 20) -> AsyncGenerator[SocialPost, None]:
        """Stream recent posts by a user."""
        pass

    @abc.abstractmethod
    async def search_posts(self, query: str, limit: int = 20) -> AsyncGenerator[SocialPost, None]:
        """Search posts by keyword or hashtag."""
        pass
