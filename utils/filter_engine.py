"""
Multi-criteria filter and query engine for SocialComment records and datasets.
Provides fast filtering by keyword, minimum likes, sentiment, spam exclusion, and platform.
"""
from typing import Any, Sequence
from pydantic import BaseModel, Field

class CommentFilterCriteria(BaseModel):
    """Filter configuration schema."""
    keyword: str | None = None
    min_likes: int = Field(default=0, ge=0)
    sentiment: str | None = None  # "positive", "neutral", "negative", or None
    exclude_spam: bool = False
    author: str | None = None
    platform: str | None = None
    only_replies: bool | None = None  # True: only replies, False: only top-level, None: all

def _get_val(item: Any, key: str, default: Any = None) -> Any:
    if isinstance(item, dict):
        return item.get(key, default)
    return getattr(item, key, default)

def filter_comments(
    items: Sequence[Any],
    criteria: CommentFilterCriteria
) -> list[Any]:
    """Filters a collection of SocialComment models or dictionaries against criteria."""
    filtered = []

    keyword_clean = criteria.keyword.strip().lower() if criteria.keyword else None
    author_clean = criteria.author.strip().lower() if criteria.author else None

    for item in items:
        # Keyword filter
        if keyword_clean:
            content = str(_get_val(item, "content", "")).lower()
            if keyword_clean not in content:
                continue

        # Min likes filter
        likes = int(_get_val(item, "likes_count", 0) or 0)
        if likes < criteria.min_likes:
            continue

        # Platform filter
        if criteria.platform and criteria.platform.lower() != "all":
            plat = str(_get_val(item, "platform", "")).lower()
            if criteria.platform.lower() not in plat:
                continue

        # Author filter
        if author_clean:
            author = str(_get_val(item, "author_username", "")).lower()
            if author_clean not in author:
                continue

        # Spam exclusion
        if criteria.exclude_spam:
            is_spam = bool(_get_val(item, "is_spam", False))
            if is_spam:
                continue

        # Sentiment filter
        if criteria.sentiment and criteria.sentiment.lower() != "all":
            sent = str(_get_val(item, "sentiment", "")).lower()
            if sent != criteria.sentiment.lower():
                continue

        # Reply filter
        if criteria.only_replies is not None:
            reply_to = _get_val(item, "reply_to_id", None)
            is_reply = reply_to is not None
            if criteria.only_replies != is_reply:
                continue

        filtered.append(item)

    return filtered

def sort_comments(
    items: Sequence[Any],
    by: str = "likes",
    descending: bool = True
) -> list[Any]:
    """Sorts comments by likes_count, reply_count, or content length."""
    key_map = {
        "likes": lambda x: int(_get_val(x, "likes_count", 0) or 0),
        "replies": lambda x: int(_get_val(x, "reply_count", 0) or 0),
        "length": lambda x: len(str(_get_val(x, "content", ""))),
    }
    sort_key = key_map.get(by, key_map["likes"])
    return sorted(items, key=sort_key, reverse=descending)
