"""
Constants, GraphQL query hashes, feature flags, and endpoints for X (Twitter).
"""

TWITTER_BASE_URL = "https://x.com"
TWITTER_LOGIN_URL = f"{TWITTER_BASE_URL}/i/flow/login"

# Mobile/Desktop user agents tested with X Web
TWITTER_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]

# Standard GraphQL query endpoints intercepted during browsing
GRAPHQL_ENDPOINTS = {
    "UserByScreenName": "UserByScreenName",
    "UserTweets": "UserTweets",
    "UserTweetsAndReplies": "UserTweetsAndReplies",
    "SearchTimeline": "SearchTimeline",
}

# Standard bearer token extracted from Twitter client web bundle
TWITTER_BEARER_TOKEN = (
    "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D"
    "1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
)

TWITTER_SELECTORS = {
    "tweet_article": "article[data-testid='tweet']",
    "tweet_text": "div[data-testid='tweetText']",
    "user_name": "div[data-testid='UserName']",
    "user_bio": "div[data-testid='UserDescription']",
    "user_location": "span[data-testid='UserLocation']",
    "user_url": "a[data-testid='UserUrl']",
}
