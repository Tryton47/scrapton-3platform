"""
Constants, GraphQL query hashes, and endpoints used for Instagram scraping.
"""

INSTAGRAM_BASE_URL = "https://www.instagram.com"
INSTAGRAM_LOGIN_URL = f"{INSTAGRAM_BASE_URL}/accounts/login/"
INSTAGRAM_PROFILE_API = f"{INSTAGRAM_BASE_URL}/api/v1/users/web_profile_info/?username="

# Common User Agents specifically tested with Instagram Web
INSTAGRAM_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]

# Standard Instagram web request headers
INSTAGRAM_HEADERS = {
    "X-IG-App-ID": "936619743392459",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.instagram.com/",
    "Accept": "*/*",
}

# Selectors fallback for DOM inspection
SELECTORS = {
    "profile_header": "header section",
    "profile_bio": "header section div.-vDIg span, header section h1 + div",
    "post_article": "article",
    "posts_grid": "article a[href^='/p/'], article a[href^='/reel/']",
}
