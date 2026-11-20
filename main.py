"""
Main entry-point CLI for the Multi-Platform Social Media Scraper.
Supports Instagram, TikTok, and X (Twitter) with interactive logins and multi-format exports.
"""
import argparse
import asyncio
import sys
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from config.settings import settings
from core.models import Platform
from core.storage import StorageManager
from scrapers.comment_scraper import CommentScraper, detect_platform_from_url
from utils.comment_analyzer import analyze_comment
from utils.filter_engine import CommentFilterCriteria, filter_comments
from scrapers.instagram import InstagramScraper
from scrapers.instagram_auth import InstagramAuth
from scrapers.tiktok import TikTokScraper
from scrapers.tiktok_auth import TikTokAuth
from scrapers.twitter import TwitterScraper
from scrapers.twitter_auth import TwitterAuth

console = Console()

def display_welcome_banner():
    """Print project banner."""
    console.print(
        Panel.fit(
            "[bold cyan]Social Media Scraper Suite[/bold cyan]\n"
            "[dim]Instagram | TikTok | X (Twitter)[/dim]\n"
            "Unified modular scraper with anti-bot detection & multi-format export",
            border_style="cyan"
        )
    )

def show_status():
    """Display current system and storage status."""
    table = Table(title="System & Configuration Status")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    ig_auth = InstagramAuth()
    tt_auth = TikTokAuth()
    tw_auth = TwitterAuth()

    table.add_row("Output Directory", str(settings.output_dir))
    table.add_row("Sessions Directory", str(settings.sessions_dir))
    table.add_row("Default Format", settings.default_output_format.upper())
    table.add_row("Headless Mode", str(settings.headless))
    table.add_row("Instagram Session Saved", "Yes" if ig_auth.has_saved_session() else "No (Run --login-instagram)")
    table.add_row("TikTok Session Saved", "Yes" if tt_auth.has_saved_session() else "No (Run --login-tiktok)")
    table.add_row("X (Twitter) Session Saved", "Yes" if tw_auth.has_saved_session() else "No (Run --login-twitter)")
    table.add_row("Supported Platforms", ", ".join(p.value for p in Platform))

    console.print(table)

async def run_instagram_scraper(username: str, limit: int, export_format: str):
    """Execute Instagram scrape flow."""
    scraper = InstagramScraper()
    storage = StorageManager()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(description=f"Fetching @{username} profile info...", total=None)
        profile = await scraper.get_profile(username)

        progress.update(task, description=f"Collecting posts from @{username}...")
        posts = []
        async for post in scraper.get_user_posts(username, limit=limit):
            posts.append(post)

    table = Table(title=f"Results for Instagram: @{username}")
    table.add_column("Display Name", style="cyan")
    table.add_column("Followers", style="green")
    table.add_column("Following", style="magenta")
    table.add_column("Posts Scraped", style="yellow")

    table.add_row(
        profile.display_name or "-",
        str(profile.followers_count),
        str(profile.following_count),
        str(len(posts))
    )
    console.print(table)

    base_name = f"instagram_{username}"
    save_scraped_items(storage, posts, base_name, export_format)

async def run_tiktok_scraper(username: str, limit: int, export_format: str):
    """Execute TikTok scrape flow."""
    cleaned_username = username.lstrip("@")
    scraper = TikTokScraper()
    storage = StorageManager()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(description=f"Fetching TikTok @{cleaned_username} profile info...", total=None)
        profile = await scraper.get_profile(cleaned_username)

        progress.update(task, description=f"Collecting TikTok videos from @{cleaned_username}...")
        posts = []
        async for post in scraper.get_user_posts(cleaned_username, limit=limit):
            posts.append(post)

    table = Table(title=f"Results for TikTok: @{cleaned_username}")
    table.add_column("Nickname", style="cyan")
    table.add_column("Followers", style="green")
    table.add_column("Following", style="magenta")
    table.add_column("Videos Scraped", style="yellow")

    table.add_row(
        profile.display_name or "-",
        str(profile.followers_count),
        str(profile.following_count),
        str(len(posts))
    )
    console.print(table)

    base_name = f"tiktok_{cleaned_username}"
    save_scraped_items(storage, posts, base_name, export_format)

async def run_twitter_scraper(username: str, limit: int, export_format: str):
    """Execute X / Twitter scrape flow."""
    cleaned_username = username.lstrip("@")
    scraper = TwitterScraper()
    storage = StorageManager()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(description=f"Fetching X @{cleaned_username} profile info...", total=None)
        profile = await scraper.get_profile(cleaned_username)

        progress.update(task, description=f"Collecting tweets from @{cleaned_username}...")
        posts = []
        async for post in scraper.get_user_posts(cleaned_username, limit=limit):
            posts.append(post)

    table = Table(title=f"Results for X (Twitter): @{cleaned_username}")
    table.add_column("Name", style="cyan")
    table.add_column("Followers", style="green")
    table.add_column("Following", style="magenta")
    table.add_column("Tweets Scraped", style="yellow")

    table.add_row(
        profile.display_name or "-",
        str(profile.followers_count),
        str(profile.following_count),
        str(len(posts))
    )
    console.print(table)

    base_name = f"twitter_{cleaned_username}"
    save_scraped_items(storage, posts, base_name, export_format)

async def run_comment_cli(
    urls: list[str],
    max_comments: int,
    export_format: str,
    keyword: str | None = None,
    min_likes: int = 0,
    exclude_spam: bool = False,
):
    """Execute multi-link comment scraping from CLI with optional filtering."""
    scraper = CommentScraper()
    storage = StorageManager()
    all_comments = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(description=f"Starting comment extraction across {len(urls)} link(s)...", total=len(urls))
        for idx, url in enumerate(urls, 1):
            plat = detect_platform_from_url(url)
            tag = plat.value.upper() if plat else "UNKNOWN"
            progress.update(task, description=f"[{idx}/{len(urls)}] Scraping comments from {tag}...", completed=idx)
            try:
                comments = await scraper.scrape_comments_from_url(url, max_comments=max_comments)
                all_comments.extend(comments)
                console.print(f"[green]✓[/green] Scraped {len(comments)} comment(s) from: [cyan]{url[:70]}[/cyan]")
            except Exception as e:
                console.print(f"[red]✗[/red] Failed {url[:50]}: {e}")

    if not all_comments:
        console.print("[yellow]No comments were extracted. Ensure URLs are accessible and valid.[/yellow]")
        return

    # Apply filtering criteria if requested
    if keyword or min_likes > 0 or exclude_spam:
        criteria = CommentFilterCriteria(
            keyword=keyword,
            min_likes=min_likes,
            exclude_spam=exclude_spam,
        )
        before_count = len(all_comments)
        # Enrich with spam analysis if spam filter is on
        if exclude_spam:
            analyzed = [analyze_comment(c.model_dump(mode="json")) for c in all_comments]
            filtered_dicts = filter_comments(analyzed, criteria)
            # Reconstruct or match
            surviving_ids = {d["id"] for d in filtered_dicts}
            all_comments = [c for c in all_comments if c.id in surviving_ids]
        else:
            all_comments = filter_comments(all_comments, criteria)
        console.print(f"[dim]Filtered: {len(all_comments)} of {before_count} comments match criteria.[/dim]")

    table = Table(title=f"Comment Scrape Summary ({len(all_comments)} items)")
    table.add_column("Author", style="cyan")
    table.add_column("Comment Preview", style="white")
    table.add_column("Likes", style="yellow")
    table.add_column("Platform", style="green")

    for c in all_comments[:5]:
        preview = (c.content[:45] + "...") if len(c.content) > 45 else c.content
        table.add_row(c.author_username, preview, str(c.likes_count), c.platform.value)

    if len(all_comments) > 5:
        table.add_row("...", f"... and {len(all_comments) - 5} more comments", "...", "...")
    console.print(table)

    base_name = f"comments_{len(all_comments)}_items"
    if export_format == "csv":
        path = storage.save_to_csv(all_comments, base_name)
    elif export_format == "excel":
        path = storage.save_to_excel(all_comments, base_name)
    elif export_format == "jsonl":
        path = storage.save_to_jsonl(all_comments, base_name)
    else:
        path = storage.save_to_json(all_comments, base_name)

    console.print(f"[bold green]Data exported successfully to:[/bold green] {path}")

def save_scraped_items(storage: StorageManager, posts: list, base_name: str, export_format: str):
    """Save posts to target format."""
    if export_format == "json":
        path = storage.save_to_json(posts, base_name)
    elif export_format == "csv":
        path = storage.save_to_csv(posts, base_name)
    elif export_format == "sqlite":
        path = storage.save_to_sqlite(posts)
    else:
        path = storage.save_to_json(posts, base_name)

    console.print(f"[bold green]Data exported successfully to:[/bold green] {path}")

def main():
    parser = argparse.ArgumentParser(description="Multi-Platform Social Media Scraper CLI")
    parser.add_argument("--status", action="store_true", help="Display configuration and scraper status")
    parser.add_argument("--login-instagram", action="store_true", help="Open browser to login and save Instagram cookies")
    parser.add_argument("--login-tiktok", action="store_true", help="Open browser to login and save TikTok cookies")
    parser.add_argument("--login-twitter", action="store_true", help="Open browser to login and save X (Twitter) cookies")
    parser.add_argument("--platform", choices=["instagram", "tiktok", "twitter"], help="Target platform")
    parser.add_argument("--username", type=str, help="Target username to scrape")
    parser.add_argument("--comments", nargs="+", help="One or more post/video URLs to scrape comments from")
    parser.add_argument("--comments-file", type=str, help="Path to text file containing target URLs (one per line)")
    parser.add_argument("--limit", type=int, default=12, help="Number of items to fetch")
    parser.add_argument("--max-comments", type=int, default=25, help="Max comments per URL (default: 25)")
    parser.add_argument("--keyword", type=str, help="Filter comments by matching keyword or phrase")
    parser.add_argument("--min-likes", type=int, default=0, help="Minimum likes count threshold")
    parser.add_argument("--exclude-spam", action="store_true", help="Filter out likely promotional/bot comments")
    parser.add_argument("--format", choices=["json", "jsonl", "csv", "excel", "sqlite"], default=settings.default_output_format, help="Output format")

    args = parser.parse_args()

    display_welcome_banner()

    if args.login_instagram:
        asyncio.run(InstagramAuth().login_interactive())
        return

    if args.login_tiktok:
        asyncio.run(TikTokAuth().login_interactive())
        return

    if args.login_twitter:
        asyncio.run(TwitterAuth().login_interactive())
        return

    if args.status or len(sys.argv) == 1:
        show_status()
        console.print("\n[yellow]Tip: Run with --platform <instagram|tiktok|twitter> --username <target> to scrape.[/yellow]")
        return

    if args.comments or args.comments_file:
        urls: list[str] = []
        if args.comments:
            urls.extend(args.comments)
        if args.comments_file:
            try:
                with open(args.comments_file, "r", encoding="utf-8") as f:
                    for line in f:
                        cleaned = line.strip()
                        if cleaned.startswith("http"):
                            urls.append(cleaned)
            except Exception as e:
                console.print(f"[bold red]Failed to read comments file:[/bold red] {e}")
                return
        if not urls:
            console.print("[bold red]No valid URLs found for comment extraction.[/bold red]")
            return
        asyncio.run(run_comment_cli(
            urls,
            args.max_comments,
            args.format,
            keyword=args.keyword,
            min_likes=args.min_likes,
            exclude_spam=args.exclude_spam,
        ))
        return

    if not args.username:
        console.print("[bold red]Error: either --username or --comments is required for scraping.[/bold red]")
        return

    if args.platform == "instagram":
        asyncio.run(run_instagram_scraper(args.username, args.limit, args.format))
    elif args.platform == "tiktok":
        asyncio.run(run_tiktok_scraper(args.username, args.limit, args.format))
    elif args.platform == "twitter":
        asyncio.run(run_twitter_scraper(args.username, args.limit, args.format))

if __name__ == "__main__":
    main()
