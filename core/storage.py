"""
Storage engine to persist scraped social media data into JSON, CSV, or SQLite.
"""
import csv
import json
import sqlite3
from pathlib import Path
from typing import Sequence
from .models import SocialPost, UserProfile

class StorageManager:
    """Manages serialization and saving of scraped items."""

    def __init__(self, output_dir: Path | str = "data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_to_json(self, items: Sequence[SocialPost | UserProfile], filename: str) -> Path:
        """Export list of items to a nicely formatted JSON file."""
        if not filename.endswith(".json"):
            filename += ".json"
        target_path = self.output_dir / filename
        data = [item.model_dump(mode="json") for item in items]
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return target_path

    def save_to_csv(self, items: Sequence[SocialPost | UserProfile], filename: str) -> Path:
        """Export list of items to CSV file."""
        if not items:
            raise ValueError("No items to export to CSV")
        if not filename.endswith(".csv"):
            filename += ".csv"
        target_path = self.output_dir / filename

        flattened = []
        for item in items:
            raw = item.model_dump(mode="json")
            flat = {}
            for k, v in raw.items():
                if isinstance(v, dict):
                    for sub_k, sub_v in v.items():
                        flat[f"{k}_{sub_k}"] = sub_v
                elif isinstance(v, list):
                    flat[k] = "; ".join(str(x) for x in v)
                else:
                    flat[k] = v
            flattened.append(flat)

        headers = list(flattened[0].keys())
        with open(target_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(flattened)
        return target_path

    def save_to_sqlite(self, posts: Sequence[SocialPost], db_name: str = "scraped_data.db") -> Path:
        """Export posts to an SQLite table."""
        target_path = self.output_dir / db_name
        conn = sqlite3.connect(target_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id TEXT PRIMARY KEY,
                platform TEXT,
                author_username TEXT,
                content TEXT,
                url TEXT,
                created_at TEXT,
                scraped_at TEXT,
                likes INTEGER,
                comments INTEGER,
                shares INTEGER,
                views INTEGER,
                media_urls TEXT,
                hashtags TEXT
            )
        """)

        for post in posts:
            cursor.execute("""
                INSERT OR REPLACE INTO posts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                post.id,
                post.platform.value,
                post.author_username,
                post.content,
                post.url,
                str(post.created_at) if post.created_at else None,
                str(post.scraped_at),
                post.metrics.likes,
                post.metrics.comments,
                post.metrics.shares,
                post.metrics.views,
                json.dumps(post.media_urls),
                json.dumps(post.hashtags)
            ))

        conn.commit()
        conn.close()
        return target_path
