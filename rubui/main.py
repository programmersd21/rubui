"""
rubui.main
~~~~~~~~~~
CLI entry point for rubui — built with Typer.

Commands:
    rubui           Run the TUI (default: manual mode)
    rubui init      Generate a default configuration file

Flags:
    --mode / -m     manual | auto
    --scramble      Start scrambled
    --solve         Auto-solve the cube using kociemba
    --speed         Auto‑mode move delay (seconds)
    --fps           Frame‑rate control
    --theme         dark | light | monochrome
    --seed          Deterministic scramble seed
    --no-color      Disable ANSI colours
"""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console

from rubui import __version__
from rubui.config import generate_default_config, load_config

app = typer.Typer(
    name="rubui",
    help="rubui — A colorful 3D Rubik's Cube terminal UI with manual and auto modes.",
    add_completion=False,
    rich_markup_mode="rich",
    no_args_is_help=False,
)

console = Console()


# ── rubui init ─────────────────────────────────────────────────────────────


@app.command()
def init(
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing config file.",
    ),
) -> None:
    """Generate a default rubui.toml configuration file."""
    path, created = generate_default_config(force=force)
    if created:
        console.print(f"[green]✓[/green] Config created at [bold]{path}[/bold]")
    else:
        console.print(
            f"[yellow]⚠[/yellow] Config already exists at [bold]{path}[/bold]\n"
            "  Use [bold]--force[/bold] to overwrite."
        )


# ── rubui (main run) ──────────────────────────────────────────────────────


@app.callback(invoke_without_command=True)
def run(
    ctx: typer.Context,
    mode: Optional[str] = typer.Option(
        None,
        "--mode",
        "-m",
        help="Choose mode: [bold]manual[/bold] or [bold]auto[/bold].",
    ),
    scramble: bool = typer.Option(
        False,
        "--scramble",
        help="Start with a scrambled cube.",
    ),
    solve: bool = typer.Option(
        False,
        "--solve",
        help="Auto-solve the cube using kociemba.",
    ),
    speed: Optional[float] = typer.Option(
        None,
        "--speed",
        help="Animation speed in auto mode (seconds between moves).",
    ),
    fps: Optional[int] = typer.Option(
        None,
        "--fps",
        help="Frame-based animation control (frames per second).",
    ),
    theme: Optional[str] = typer.Option(
        None,
        "--theme",
        help="Choose theme: [bold]dark[/bold], [bold]light[/bold], or [bold]monochrome[/bold].",
    ),
    seed: Optional[int] = typer.Option(
        None,
        "--seed",
        help="Deterministic scramble seed for reproducible scrambles.",
    ),
    no_color: bool = typer.Option(
        False,
        "--no-color",
        help="Disable ANSI colours — render with plain characters.",
    ),
    size: Optional[int] = typer.Option(
        None,
        "--size",
        "-z",
        help="Control the cube render size.",
    ),
    version: bool = typer.Option(
        False,
        "--version",
        help="Show version and exit.",
    ),
) -> None:
    """Run the Rubik's Cube TUI."""
    if ctx.invoked_subcommand is not None:
        return

    if version:
        console.print(f"rubui [bold]{__version__}[/bold]")
        raise typer.Exit()

    # Validate mode
    if mode is not None and mode not in ("manual", "auto"):
        console.print(
            f"[red]Error:[/red] Unknown mode [bold]{mode!r}[/bold]. Use 'manual' or 'auto'."
        )
        raise typer.Exit(code=1)

    # Validate theme
    if theme is not None and theme not in ("dark", "light", "monochrome"):
        console.print(
            f"[red]Error:[/red] Unknown theme [bold]{theme!r}[/bold]. Use 'dark', 'light', or 'monochrome'."
        )
        raise typer.Exit(code=1)

    # Build config
    cfg = load_config(
        cli_mode=mode,
        cli_theme=theme,
        cli_scramble=scramble,
        cli_solve=solve,
        cli_speed=speed,
        cli_fps=fps,
        cli_seed=seed,
        cli_no_color=no_color,
        cli_size=size,
    )

    # Monochrome theme → disable colour
    if cfg.theme == "monochrome":
        cfg.color = False

    # Launch appropriate mode
    if cfg.mode == "auto":
        from rubui.auto_mode import run as auto_run

        auto_run(cfg)
    else:
        from rubui.manual_mode import run as manual_run

        manual_run(cfg)


def main() -> None:
    """Package entry point."""
    app()


if __name__ == "__main__":
    main()
