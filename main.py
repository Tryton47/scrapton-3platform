"""
Main entry-point CLI for the Multi-Platform Social Media Scraper.
Supports Instagram, TikTok, and X with interactive logins and multi-format exports.
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
from scrapers.instagram import InstagramScraper
from scrapers.instagram_auth import InstagramAuth

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
    table.add_row("Output Directory", str(settings.output_dir))
    table.add_row("Sessions Directory", str(settings.sessions_dir))
    table.add_row("Default Format", settings.default_output_format.upper())
    table.add_row("Headless Mode", str(settings.headless))
    table.add_row("Instagram Session Saved", "Yes" if ig_auth.has_saved_session() else "No (Run --login-instagram)")
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

    # Print Summary Table
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

    # Save outputs
    base_name = f"instagram_{username}"
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
    parser.add_argument("--platform", choices=["instagram", "tiktok", "twitter"], help="Target platform")
    parser.add_argument("--username", type=str, help="Target username to scrape")
    parser.add_argument("--limit", type=int, default=12, help="Number of posts to fetch")
    parser.add_argument("--format", choices=["json", "csv", "sqlite"], default=settings.default_output_format, help="Output format")

    args = parser.parse_args()

    display_welcome_banner()

    if args.login_instagram:
        auth = InstagramAuth()
        asyncio.run(auth.login_interactive())
        return

    if args.status or len(sys.argv) == 1:
        show_status()
        console.print("\n[yellow]Tip: Run with --platform instagram --username <target> to scrape posts.[/yellow]")
        return

    if args.platform == "instagram":
        if not args.username:
            console.print("[bold red]Error: --username is required for scraping.[/bold red]")
            return
        asyncio.run(run_instagram_scraper(args.username, args.limit, args.format))
    else:
        console.print(f"[yellow]Platform {args.platform} scraper is scheduled for upcoming modules![/yellow]")

if __name__ == "__main__":
    main()
