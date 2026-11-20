# Changelog

All notable changes to the Scrapton multi-platform social media and comment scraper project are documented here.

## [v2.3.0] - 2026-11-20

### Added
- **Multi-Criteria Filter Engine**: Added `utils/filter_engine.py` for keyword filtering, minimum likes threshold, sentiment polarity, and spam exclusion.
- **Social Media URL Parser**: Added `utils/url_parser.py` with shortlink support (`vm.tiktok.com`, `vt.tiktok.com`, `t.co`, `instagr.am`) and post ID extractor.
- **Enhanced SocialComment Schema**: Added `reply_to_id` and `language` fields in `core/models.py`.
- **Advanced CLI Comment Flags**: Added `--keyword`, `--min-likes`, and `--exclude-spam` to `main.py`.
- **Preset Loaders and UI Filters**: Added one-click sample loaders (TikTok, Instagram) and multi-field interactive dataset filters in `app.py`.
- **Unit Test Coverage**: Added `tests/test_filter_engine.py` and `tests/test_url_parser.py` (37 total passing tests).

---

## [v2.2.0] - 2026-11-19

### Added
- **Apify Actor Console Web UI**: High-density Zinc dark developer dashboard with 3 distinct tabs (Input Configuration, Live Console, and Storage Dataset).
- **Sentiment & Spam Heuristics**: Added `utils/comment_analyzer.py` for rule-based polarity scoring and bot detection.
- **Dataset Multi-Format Export**: Storage manager support for Excel (.xlsx), CSV, JSON, and JSONL formats.
- **CLI Comment Runner**: Added `--comments` and `--comments-file` flags to `main.py`.
- **Automated CI Workflow**: GitHub Actions pipeline matrix for Python 3.11, 3.12, and 3.13.

### Fixed
- Migrated legacy `utcfromtimestamp` to timezone-aware UTC datetime across models and post extractors.

---

## [v2.1.0] - 2026-11-18

### Added
- Multi-link comment scraper engine (`scrapers/comment_scraper.py`) with network interception and DOM fallback.
- Streamlit batch URL input editor and visual CSV/Excel download capabilities.

---

## [v2.0.0] - 2026-11-17

### Added
- Multi-platform scrapers for Instagram, TikTok, and X (Twitter).
- Modular architecture with unified Pydantic data schemas.
- Interactive login and session cookie preservation workflows.
