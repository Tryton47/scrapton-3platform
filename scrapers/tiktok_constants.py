"""
Constants, API endpoints, and headers used for TikTok scraping.
"""

TIKTOK_BASE_URL = "https://www.tiktok.com"
TIKTOK_LOGIN_URL = f"{TIKTOK_BASE_URL}/login"

TIKTOK_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]

TIKTOK_HEADERS = {
    "Referer": "https://www.tiktok.com/",
    "Accept": "*/*",
}

SELECTORS = {
    "user_title": "h1[data-e2e='user-title']",
    "user_subtitle": "h2[data-e2e='user-subtitle']",
    "user_bio": "h2[data-e2e='user-bio']",
    "following_count": "strong[data-e2e='following-count']",
    "followers_count": "strong[data-e2e='followers-count']",
    "likes_count": "strong[data-e2e='likes-count']",
    "video_item": "div[data-e2e='user-post-item']",
    "video_link": "div[data-e2e='user-post-item'] a",
}
