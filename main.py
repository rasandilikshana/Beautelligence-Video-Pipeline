#!/usr/bin/env python3
"""
Beautelligence Video Pipeline - CLI Entry Point

Usage:
    python main.py run [--videos N] [--mock]
    python main.py single "keyword" [--force] [--mock]
    python main.py test
    python main.py init
    python main.py status
    python main.py config
"""

import asyncio
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from config.logging import setup_logging
from config.settings import settings

app = typer.Typer(
    name="beautelligence",
    help="🎬 Beautelligence Video Pipeline - Generate cute AI videos automatically",
    add_completion=False,
)
console = Console()


def async_command(func):
    """Decorator to run async functions with typer."""
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return wrapper


@app.command()
@async_command
async def run(
    videos: int = typer.Option(
        None, "--videos", "-v", help="Number of videos to generate"
    ),
    mock: bool = typer.Option(
        False, "--mock", "-m", help="Use mock services (no API calls)"
    ),
) -> None:
    """Run the daily video generation pipeline."""
    setup_logging(settings.log_level, settings.log_dir)

    from src.orchestrator.pipeline import VideoPipeline

    console.print(
        Panel.fit(
            "🎬 [bold blue]Beautelligence Video Pipeline[/bold blue]\n"
            f"Mode: {'[yellow]MOCK[/yellow]' if mock else '[green]LIVE[/green]'}",
            border_style="blue",
        )
    )

    pipeline = VideoPipeline(mock=mock)
    await pipeline.initialize()

    with console.status("[bold green]Running pipeline..."):
        result = await pipeline.run(video_count=videos)

    # Display results
    if result.success:
        console.print(
            f"\n✅ [bold green]Pipeline completed successfully![/bold green]"
        )
    else:
        console.print(f"\n⚠️ [bold yellow]Pipeline completed with issues[/bold yellow]")

    table = Table(title="Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    table.add_row("Videos Generated", str(result.videos_generated))
    table.add_row("Videos Failed", str(result.videos_failed))
    table.add_row("Errors", str(len(result.errors)))
    console.print(table)

    if result.errors:
        console.print("\n[bold red]Errors:[/bold red]")
        for error in result.errors[:5]:
            console.print(f"  • {error}")


@app.command()
@async_command
async def single(
    keyword: str = typer.Argument(..., help="Keyword to generate video for"),
    force: bool = typer.Option(
        False, "--force", "-f", help="Force generation (skip duplicate check)"
    ),
    mock: bool = typer.Option(
        False, "--mock", "-m", help="Use mock services (no API calls)"
    ),
) -> None:
    """Generate a video for a specific keyword."""
    setup_logging(settings.log_level, settings.log_dir)

    from src.orchestrator.pipeline import VideoPipeline

    console.print(
        f"\n🎯 Generating video for: [bold cyan]{keyword}[/bold cyan]"
        f"{' (forced)' if force else ''}"
    )

    pipeline = VideoPipeline(mock=mock)
    await pipeline.initialize()

    with console.status(f"[bold green]Processing '{keyword}'..."):
        result = await pipeline.run_single(keyword=keyword, force=force)

    if result["success"]:
        console.print(f"\n✅ [bold green]Video generated successfully![/bold green]")
        console.print(f"   📁 Path: {result.get('video_path', 'N/A')}")
        console.print(f"   📊 Size: {result.get('file_size', 0):,} bytes")
    else:
        console.print(f"\n❌ [bold red]Generation failed[/bold red]")
        console.print(f"   Error: {result.get('error', 'Unknown')}")


@app.command()
@async_command
async def test() -> None:
    """Run pipeline with mock services (no API calls)."""
    setup_logging(settings.log_level, settings.log_dir)

    from src.orchestrator.pipeline import VideoPipeline

    console.print(
        Panel.fit(
            "🧪 [bold yellow]Test Mode[/bold yellow]\n"
            "Running with mock services - no API calls will be made",
            border_style="yellow",
        )
    )

    pipeline = VideoPipeline(mock=True)
    await pipeline.initialize()

    with console.status("[bold green]Running test pipeline..."):
        result = await pipeline.run(video_count=1)

    if result.success and result.videos_generated > 0:
        console.print("\n✅ [bold green]Test completed successfully![/bold green]")
        for detail in result.details:
            console.print(f"   Keyword: {detail.get('keyword', 'N/A')}")
            console.print(f"   Video: {detail.get('video_path', 'N/A')}")
    else:
        console.print(f"\n⚠️ [bold yellow]Test completed with issues[/bold yellow]")
        for error in result.errors:
            console.print(f"   • {error}")


@app.command()
@async_command
async def init() -> None:
    """Initialize database and create required directories."""
    setup_logging(settings.log_level)

    console.print("\n🔧 [bold]Initializing pipeline...[/bold]")

    # Create directories
    settings.ensure_directories()
    console.print("  ✅ Created data directories")

    # Initialize database
    from src.models.database import init_db

    await init_db()
    console.print("  ✅ Initialized database tables")

    console.print("\n✅ [bold green]Initialization complete![/bold green]")


@app.command()
@async_command
async def status() -> None:
    """Show current pipeline status and quotas."""
    setup_logging(settings.log_level)

    from src.orchestrator.pipeline import VideoPipeline

    pipeline = VideoPipeline()

    try:
        status_data = await pipeline.get_status()

        console.print(
            Panel.fit(
                "📊 [bold blue]Pipeline Status[/bold blue]",
                border_style="blue",
            )
        )

        # Quota table
        quota = status_data.get("quota", {})
        quota_table = Table(title="Today's Quota")
        quota_table.add_column("Metric", style="cyan")
        quota_table.add_column("Value", style="magenta")
        quota_table.add_row("Videos Generated", str(quota.get("videos_generated", 0)))
        quota_table.add_row("Videos Limit", str(quota.get("videos_limit", 0)))
        quota_table.add_row("Remaining", str(quota.get("videos_remaining", 0)))
        quota_table.add_row(
            "Can Generate",
            "[green]Yes[/green]" if quota.get("can_generate") else "[red]No[/red]",
        )
        console.print(quota_table)

        # Generation stats
        gen_stats = status_data.get("generations", {})
        gen_table = Table(title="Generation Statistics")
        gen_table.add_column("Status", style="cyan")
        gen_table.add_column("Count", style="magenta")
        gen_table.add_row("Total", str(gen_stats.get("total", 0)))
        gen_table.add_row("Completed", str(gen_stats.get("complete", 0)))
        gen_table.add_row("Failed", str(gen_stats.get("failed", 0)))
        gen_table.add_row("Pending", str(gen_stats.get("pending", 0)))
        console.print(gen_table)

        # Config
        config = status_data.get("config", {})
        config_table = Table(title="Configuration")
        config_table.add_column("Setting", style="cyan")
        config_table.add_column("Value", style="magenta")
        config_table.add_row("Daily Limit", str(config.get("daily_limit", "N/A")))
        config_table.add_row("Veo Model", config.get("veo_model", "N/A"))
        config_table.add_row("Gemini Model", config.get("gemini_model", "N/A"))
        config_table.add_row(
            "API Key",
            "[green]Configured[/green]"
            if config.get("has_api_key")
            else "[red]Missing[/red]",
        )
        console.print(config_table)

    except Exception as e:
        console.print(f"\n⚠️ [yellow]Could not get status: {e}[/yellow]")
        console.print("  Run 'python main.py init' first to initialize the database.")


@app.command()
def config() -> None:
    """Display current configuration."""
    console.print(
        Panel.fit(
            "⚙️ [bold blue]Configuration[/bold blue]",
            border_style="blue",
        )
    )

    table = Table(title="Settings")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="magenta")

    # Core settings
    table.add_row("Environment", settings.app_env)
    table.add_row("Debug", str(settings.app_debug))
    table.add_row("Log Level", settings.log_level)

    table.add_row("", "")  # Separator

    # API settings
    table.add_row(
        "Google API Key",
        "[green]Configured[/green]" if settings.has_api_key else "[red]Not set[/red]",
    )
    table.add_row("Gemini Model", settings.gemini_model)
    table.add_row("Veo Model", settings.veo_model)

    table.add_row("", "")  # Separator

    # Video settings
    table.add_row("Aspect Ratio", settings.veo_aspect_ratio)
    table.add_row("Resolution", settings.veo_resolution)
    table.add_row("Duration", f"{settings.veo_duration_seconds}s")

    table.add_row("", "")  # Separator

    # Limits
    table.add_row("Daily Video Limit", str(settings.daily_video_limit))
    table.add_row("Gemini RPM Limit", str(settings.gemini_rpm_limit))
    table.add_row("Keyword Expiry", f"{settings.keyword_expiry_days} days")

    table.add_row("", "")  # Separator

    # Paths
    table.add_row("Video Output", str(settings.video_output_dir))
    table.add_row("Prompt Logs", str(settings.prompt_log_dir))
    table.add_row("Log Directory", str(settings.log_dir))

    console.print(table)


@app.command()
def version() -> None:
    """Show version information."""
    console.print("\n🎬 [bold blue]Beautelligence Video Pipeline[/bold blue]")
    console.print("   Version: 1.0.0")
    console.print("   Python: 3.11+")
    console.print("   License: MIT\n")


if __name__ == "__main__":
    app()
