"""
Comment text processing, spam detection, and sentiment polarity analyzer.
Provides lightweight heuristics for social media comment analysis.
"""
import re
from typing import Any

POSITIVE_WORDS = {
    "bagus", "keren", "mantap", "suka", "love", "good", "great", "awesome",
    "terbaik", "salut", "top", "lucu", "setuju", "bermanfaat", "insightful",
    "makasih", "terima kasih", "thanks", "thank you", "kreatif", "cantik",
    "ganteng", "semangat", "hebat", "proud", "respect", "indah", "puas",
    "rekomendasi", "recommended", "gokil", "juara", "epic", "brilliant"
}

NEGATIVE_WORDS = {
    "jelek", "buruk", "kecewa", "payah", "bohong", "hoax", "hate", "bad",
    "worst", "scam", "penipu", "rugi", "rusak", "sampah", "hujat", "toxic",
    "kesal", "muak", "parah", "aneh", "cacat", "kapok", "gak guna", "ga guna",
    "menyesal", "zonk", "gagal", "rugi", "benci", "menipu", "pembodohan"
}

SPAM_PATTERNS = [
    r"\b(wa\.me|api\.whatsapp\.com)\b",
    r"\b(check\s+(my\s+)?bio|cek\s+bio)\b",
    r"\b(dm\s+(me|for)|inbox\s+me)\b",
    r"\b(crypto|bitcoin|investasi|slot|gacor|link\s+di\s+bio)\b",
    r"\b(follow\s+back|follback|bantu\s+follow)\b",
]

def clean_comment_text(text: str) -> str:
    """Removes irregular spacing, normalized line breaks, and excessive blank lines."""
    if not text:
        return ""
    normalized = re.sub(r"[\r\n]+", " ", text)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized

def extract_mentions(text: str) -> list[str]:
    """Extracts unique @mentions from comment body."""
    if not text:
        return []
    matches = re.findall(r"@([a-zA-Z0-9_\.]+)", text)
    return list(dict.fromkeys(matches))

def is_likely_spam(text: str) -> bool:
    """Detects common social media bot and promotional comment patterns."""
    if not text:
        return False
    lower = text.lower()
    for pattern in SPAM_PATTERNS:
        if re.search(pattern, lower):
            return True
    # Repetitive characters pattern (e.g. "aaaaaaa", "!!!!!!!!!!")
    if re.search(r"(.)\1{9,}", text):
        return True
    return False

def detect_sentiment_polarity(text: str) -> tuple[str, float]:
    """
    Computes a normalized polarity score between -1.0 and 1.0.
    Returns (label, score) where label is 'positive', 'neutral', or 'negative'.
    """
    if not text:
        return ("neutral", 0.0)

    words = re.findall(r"\b[a-zA-Z0-9_]+\b", text.lower())
    if not words:
        return ("neutral", 0.0)

    pos_count = sum(1 for w in words if w in POSITIVE_WORDS)
    neg_count = sum(1 for w in words if w in NEGATIVE_WORDS)

    diff = pos_count - neg_count
    total = pos_count + neg_count

    if total == 0:
        return ("neutral", 0.0)

    score = round(diff / total, 2)
    if score > 0.15:
        label = "positive"
    elif score < -0.15:
        label = "negative"
    else:
        label = "neutral"

    return (label, score)

def analyze_comment(comment_data: dict[str, Any]) -> dict[str, Any]:
    """Enriches comment dictionary with analytical attributes."""
    content = comment_data.get("content", "")
    sentiment, polarity = detect_sentiment_polarity(content)
    mentions = extract_mentions(content)
    spam = is_likely_spam(content)

    enriched = dict(comment_data)
    enriched["sentiment"] = sentiment
    enriched["polarity_score"] = polarity
    enriched["mentions_count"] = len(mentions)
    enriched["is_spam"] = spam
    return enriched
