"""
URL Parser and Identifier Extractor for Social Media Platforms.
Extracts post IDs, handles shortlinks, and normalizes URLs across TikTok, Instagram, and X.
"""
import re
from urllib.parse import urlparse
from core.models import Platform

TIKTOK_PATTERNS = [
    r"/video/(\d+)",
    r"/v/(\d+)",
    r"photo/(\d+)",
]

INSTAGRAM_PATTERNS = [
    r"/(?:p|reel|tv)/([A-Za-z0-9_-]+)",
]

TWITTER_PATTERNS = [
    r"/status/(\d+)",
]

def normalize_url(raw_url: str) -> str:
    """Cleans tracking parameters (e.g. ?utm_source, ?is_from_webapp) from URL."""
    if not raw_url:
        return ""
    clean = raw_url.strip()
    if not clean.startswith("http"):
        clean = "https://" + clean
    parsed = urlparse(clean)
    normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    return normalized.rstrip("/")

def is_shortlink(url: str) -> bool:
    """Checks if the URL is a known shortlink domain."""
    lowered = url.lower()
    shortlink_domains = [
        "vm.tiktok.com",
        "vt.tiktok.com",
        "t.co",
        "instagr.am",
        "x.com/i/",
    ]
    return any(domain in lowered for domain in shortlink_domains)

def extract_post_id(url: str) -> str | None:
    """Extracts unique content identifier from post URL."""
    if not url:
        return None

    cleaned = normalize_url(url)

    # TikTok ID
    for pattern in TIKTOK_PATTERNS:
        match = re.search(pattern, cleaned)
        if match:
            return match.group(1)

    # Instagram Shortcode
    for pattern in INSTAGRAM_PATTERNS:
        match = re.search(pattern, cleaned)
        if match:
            return match.group(1)

    # Twitter / X Status ID
    for pattern in TWITTER_PATTERNS:
        match = re.search(pattern, cleaned)
        if match:
            return match.group(1)

    return None

def parse_social_url(url: str) -> dict[str, str | None]:
    """Returns parsed metadata: platform, post_id, normalized_url."""
    normalized = normalize_url(url)
    post_id = extract_post_id(normalized)
    lowered = normalized.lower()

    platform = None
    if "tiktok.com" in lowered:
        platform = Platform.TIKTOK.value
    elif "instagram.com" in lowered or "instagr.am" in lowered:
        platform = Platform.INSTAGRAM.value
    elif "twitter.com" in lowered or "x.com" in lowered:
        platform = Platform.TWITTER.value

    return {
        "raw_url": url,
        "normalized_url": normalized,
        "platform": platform,
        "post_id": post_id,
        "is_shortlink": is_shortlink(url),
    }
