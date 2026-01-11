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
@async_command
async def tasks(
    status_filter: Optional[str] = typer.Option(
        None, "--status", "-s", help="Filter by status (pending, used, skipped, all)"
    ),
    limit: int = typer.Option(20, "--limit", "-l", help="Max tasks to show"),
) -> None:
    """View pending and completed tasks/keywords."""
    setup_logging(settings.log_level)

    from src.models.database import get_session
    from src.models.keyword import Keyword
    from src.models.generation import Generation
    from sqlalchemy import select, desc

    console.print(
        Panel.fit(
            "📋 [bold blue]Task Queue[/bold blue]",
            border_style="blue",
        )
    )

    async with get_session() as session:
        # Keywords query
        query = select(Keyword).order_by(desc(Keyword.created_at)).limit(limit)
        if status_filter and status_filter != "all":
            query = query.where(Keyword.status == status_filter)
        
        result = await session.execute(query)
        keywords = result.scalars().all()

        if not keywords:
            console.print("\n[yellow]No tasks found.[/yellow]")
            return

        # Keywords table
        kw_table = Table(title="Keywords Queue")
        kw_table.add_column("#", style="dim")
        kw_table.add_column("Keyword", style="cyan")
        kw_table.add_column("Status", style="magenta")
        kw_table.add_column("Source", style="green")
        kw_table.add_column("Score", style="yellow")
        kw_table.add_column("Created", style="dim")

        for i, kw in enumerate(keywords, 1):
            status_style = {
                "pending": "[yellow]pending[/yellow]",
                "used": "[green]used[/green]",
                "skipped": "[red]skipped[/red]",
            }.get(kw.status, kw.status)
            
            created = kw.created_at.strftime("%Y-%m-%d %H:%M") if kw.created_at else "N/A"
            kw_table.add_row(
                str(i),
                kw.keyword,
                status_style,
                kw.source or "manual",
                str(kw.trending_score or 0),
                created,
            )

        console.print(kw_table)

        # Recent generations
        gen_query = select(Generation).order_by(desc(Generation.created_at)).limit(10)
        gen_result = await session.execute(gen_query)
        generations = gen_result.scalars().all()

        if generations:
            gen_table = Table(title="Recent Generations")
            gen_table.add_column("Status", style="magenta")
            gen_table.add_column("File", style="cyan")
            gen_table.add_column("Size", style="yellow")
            gen_table.add_column("Created", style="dim")

            for gen in generations:
                status_style = {
                    "complete": "[green]✓ complete[/green]",
                    "pending": "[yellow]⏳ pending[/yellow]",
                    "failed": "[red]✗ failed[/red]",
                }.get(gen.status, gen.status)
                
                file_name = gen.video_file_path.split("/")[-1] if gen.video_file_path else "N/A"
                size = f"{gen.file_size_bytes:,}" if gen.file_size_bytes else "-"
                created = gen.created_at.strftime("%Y-%m-%d %H:%M") if gen.created_at else "N/A"
                
                gen_table.add_row(status_style, file_name, size, created)

            console.print(gen_table)


@app.command()
@async_command
async def queue(
    keywords: list[str] = typer.Argument(..., help="Keywords to add to queue"),
    score: int = typer.Option(100, "--score", "-s", help="Trending score (1-100)"),
) -> None:
    """Add keywords to the processing queue."""
    setup_logging(settings.log_level)

    from src.models.database import get_session
    from src.models.keyword import Keyword

    console.print(f"\n📥 Adding {len(keywords)} keyword(s) to queue...")

    async with get_session() as session:
        added = 0
        for kw in keywords:
            try:
                keyword_obj = Keyword.create(
                    keyword=kw,
                    source="manual_queue",
                    score=score,
                )
                session.add(keyword_obj)
                added += 1
            except Exception as e:
                console.print(f"  [yellow]⚠ Skipped '{kw}': {e}[/yellow]")

        await session.commit()

    console.print(f"\n✅ Added {added} keyword(s) to queue")
    console.print("   Run 'python main.py service' or 'python main.py run' to process them")


@app.command()
@async_command
async def service(
    interval: int = typer.Option(
        3600, "--interval", "-i", help="Seconds between runs (default: 1 hour)"
    ),
    videos_per_run: int = typer.Option(
        1, "--videos", "-v", help="Videos to generate per run"
    ),
    mock: bool = typer.Option(
        False, "--mock", "-m", help="Use mock services (no API calls)"
    ),
) -> None:
    """Run as a background service with scheduled execution.
    
    This runs the pipeline continuously at specified intervals.
    Press Ctrl+C to stop.
    
    Example:
        python main.py service --interval 3600 --videos 2
        (generates 2 videos every hour)
    """
    setup_logging(settings.log_level, settings.log_dir)

    from src.orchestrator.pipeline import VideoPipeline
    import signal
    import sys
    from datetime import datetime

    running = True

    def signal_handler(sig, frame):
        nonlocal running
        console.print("\n\n🛑 [yellow]Stopping service...[/yellow]")
        running = False

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    console.print(
        Panel.fit(
            "🔄 [bold blue]Video Pipeline Service[/bold blue]\n"
            f"Mode: {'[yellow]MOCK[/yellow]' if mock else '[green]LIVE[/green]'}\n"
            f"Interval: {interval} seconds ({interval // 60} minutes)\n"
            f"Videos per run: {videos_per_run}\n\n"
            "[dim]Press Ctrl+C to stop[/dim]",
            border_style="blue",
        )
    )

    run_count = 0
    total_videos = 0
    total_errors = 0

    while running:
        run_count += 1
        start_time = datetime.now()

        console.print(f"\n▶️  [bold]Run #{run_count}[/bold] - {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

        try:
            pipeline = VideoPipeline(mock=mock)
            await pipeline.initialize()

            with console.status("[bold green]Processing..."):
                result = await pipeline.run(video_count=videos_per_run)

            total_videos += result.videos_generated
            total_errors += len(result.errors)

            if result.success:
                console.print(f"   ✅ Generated {result.videos_generated} video(s)")
            else:
                console.print(f"   ⚠️ Completed with {len(result.errors)} error(s)")

            for detail in result.details[:3]:
                console.print(f"      • {detail.get('keyword', 'N/A')}: {detail.get('video_path', 'failed')}")

        except Exception as e:
            console.print(f"   ❌ Error: {e}")
            total_errors += 1

        # Show summary
        elapsed = (datetime.now() - start_time).total_seconds()
        console.print(f"   ⏱️  Completed in {elapsed:.1f}s")

        # Service stats
        stats_table = Table(show_header=False, box=None)
        stats_table.add_column("", style="dim")
        stats_table.add_column("", style="cyan")
        stats_table.add_row("Total runs:", str(run_count))
        stats_table.add_row("Total videos:", str(total_videos))
        stats_table.add_row("Total errors:", str(total_errors))
        console.print(stats_table)

        if not running:
            break

        # Wait for next run
        next_run = datetime.now().timestamp() + interval
        console.print(f"\n⏳ Next run in {interval} seconds ({interval // 60} min)...")

        while running and datetime.now().timestamp() < next_run:
            await asyncio.sleep(1)

    console.print("\n✅ [bold green]Service stopped gracefully[/bold green]")
    console.print(f"   Total runs: {run_count}")
    console.print(f"   Total videos: {total_videos}")


@app.command()
def version() -> None:
    """Show version information."""
    console.print("\n🎬 [bold blue]Beautelligence Video Pipeline[/bold blue]")
    console.print("   Version: 1.0.0")
    console.print("   Python: 3.11+")
    console.print("   License: MIT\n")


if __name__ == "__main__":
    app()

