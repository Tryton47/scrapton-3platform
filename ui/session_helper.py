"""
Session and state helpers for the Streamlit web dashboard.
"""
from scrapers.instagram_auth import InstagramAuth
from scrapers.tiktok_auth import TikTokAuth
from scrapers.twitter_auth import TwitterAuth

def get_session_status() -> dict[str, bool]:
    """Check persistence status of session cookies for all three platforms."""
    return {
        "instagram": InstagramAuth().has_saved_session(),
        "tiktok": TikTokAuth().has_saved_session(),
        "twitter": TwitterAuth().has_saved_session(),
    }
