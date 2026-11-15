"""
Parsing and formatting utilities for social media text and metrics.
"""
import re
from datetime import datetime

def parse_abbreviated_number(value: str | int | float | None) -> int:
    """
    Parse social media metrics like '10.5K', '2.3M', '1.1B', or '1,234' into an integer.
    """
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        return int(value)

    cleaned = str(value).strip().upper().replace(",", "").replace(" ", "")
    if not cleaned:
        return 0

    match = re.search(r"([\d.]+)([KMB]?)", cleaned)
    if not match:
        return 0

    number_str, unit = match.groups()
    try:
        number = float(number_str)
    except ValueError:
        return 0

    multipliers = {
        "K": 1_000,
        "M": 1_000_000,
        "B": 1_000_000_000,
    }

    return int(number * multipliers.get(unit, 1))

def extract_hashtags(text: str | None) -> list[str]:
    """Extract all hashtags from caption or post body."""
    if not text:
        return []
    return re.findall(r"#([a-zA-Z0-9_\u00c0-\u00ff]+)", text)

def clean_text(text: str | None) -> str:
    """Normalize whitespace and strip unneeded trailing characters."""
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    return text.strip()
