"""
Main entry-point CLI for the Multi-Platform Social Media Scraper.
"""
import argparse
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from config.settings import settings
from core.models import Platform
from core.storage import StorageManager

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

    table.add_row("Output Directory", str(settings.output_dir))
    table.add_row("Sessions Directory", str(settings.sessions_dir))
    table.add_row("Default Format", settings.default_output_format.upper())
    table.add_row("Headless Mode", str(settings.headless))
    table.add_row("Supported Platforms", ", ".join(p.value for p in Platform))

    console.print(table)

def main():
    parser = argparse.ArgumentParser(description="Multi-Platform Social Media Scraper CLI")
    parser.add_argument("--status", action="store_true", help="Display configuration and scraper status")
    parser.add_argument("--platform", choices=["instagram", "tiktok", "twitter"], help="Target platform")
    parser.add_argument("--username", type=str, help="Target username to scrape")
    parser.add_argument("--format", choices=["json", "csv", "sqlite"], default=settings.default_output_format, help="Output format")

    args = parser.parse_args()

    display_welcome_banner()

    if args.status or len(sys.argv) == 1:
        show_status()
        console.print("\n[yellow]Tip: Run with --platform and --username to scrape target accounts.[/yellow]")
        return

    console.print(f"[bold green]Starting scraper for platform:[/bold green] {args.platform}")
    console.print(f"[bold green]Target user:[/bold green] {args.username}")
    console.print(f"[bold green]Output format:[/bold green] {args.format}")

if __name__ == "__main__":
    main()
