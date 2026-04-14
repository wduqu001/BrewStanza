"""
BrewStanza CLI - Main entry point.
"""

import click
from rich.console import Console

from brewstanza import __version__

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="brewstanza")
@click.option("--no-color", is_flag=True, help="Disable colored output")
@click.pass_context
def main(ctx: click.Context, no_color: bool) -> None:
    """
    🍺 BrewStanza - macOS Homebrew & Application Manager
    
    A minimalist CLI tool for managing Homebrew packages,
    installed applications, and storage analytics.
    """
    ctx.ensure_object(dict)
    ctx.obj["no_color"] = no_color
    ctx.obj["console"] = Console(no_color=no_color)


# =============================================================================
# BREW COMMANDS
# =============================================================================

@main.group()
@click.pass_context
def brew(ctx: click.Context) -> None:
    """Manage Homebrew packages (formulae and casks)."""
    pass


@brew.command("list")
@click.option("--formula", "-f", "formula_only", is_flag=True,
              help="List only formulae")
@click.option("--cask", "-c", "cask_only", is_flag=True,
              help="List only casks")
@click.option("--size", "-s", is_flag=True, default=True,
              help="Show package sizes (default: True)")
@click.pass_context
def brew_list(ctx: click.Context, formula_only: bool, cask_only: bool, size: bool) -> None:
    """List installed Homebrew packages with sizes."""
    console = ctx.obj["console"]

    # TODO: Implement in Week 1
    console.print("[yellow]⚠️  Homebrew scanner not yet implemented[/yellow]")
    console.print("[dim]This feature will be available after Week 1[/dim]")

    if formula_only:
        console.print("[dim]Filter: formulae only[/dim]")
    elif cask_only:
        console.print("[dim]Filter: casks only[/dim]")


@brew.command("info")
@click.argument("package", required=True)
@click.pass_context
def brew_info(ctx: click.Context, package: str) -> None:
    """Show detailed information about a package."""
    console = ctx.obj["console"]

    # TODO: Implement in Week 1
    console.print(f"[yellow]⚠️  Package info for '{package}' not yet implemented[/yellow]")
    console.print("[dim]This feature will be available after Week 1[/dim]")


@brew.command("outdated")
@click.pass_context
def brew_outdated(ctx: click.Context) -> None:
    """List outdated packages."""
    console = ctx.obj["console"]

    # TODO: Implement in Week 1
    console.print("[yellow]⚠️  Outdated packages check not yet implemented[/yellow]")
    console.print("[dim]This feature will be available after Week 1[/dim]")


# =============================================================================
# APPS COMMANDS
# =============================================================================

@main.group()
@click.pass_context
def apps(ctx: click.Context) -> None:
    """Scan and manage installed applications."""
    pass


@apps.command("list")
@click.option("--category", "-c", is_flag=True,
              help="Group apps by category")
@click.option("--size", "-s", is_flag=True, default=True,
              help="Show app sizes (default: True)")
@click.pass_context
def apps_list(ctx: click.Context, category: bool, size: bool) -> None:
    """List installed applications."""
    console = ctx.obj["console"]

    # TODO: Implement in Week 2
    console.print("[yellow]⚠️  Application scanner not yet implemented[/yellow]")
    console.print("[dim]This feature will be available after Week 2[/dim]")

    if category:
        console.print("[dim]Grouping: by category[/dim]")


@apps.command("info")
@click.argument("app_name", required=True)
@click.pass_context
def apps_info(ctx: click.Context, app_name: str) -> None:
    """Show app details with removal instructions."""
    console = ctx.obj["console"]

    # TODO: Implement in Week 2
    console.print(f"[yellow]⚠️  App info for '{app_name}' not yet implemented[/yellow]")
    console.print("[dim]This feature will be available after Week 2[/dim]")


# =============================================================================
# STORAGE COMMANDS
# =============================================================================

@main.command()
@click.option("--top", "-t", default=10, help="Show top N storage consumers")
@click.option("--category", "-c", is_flag=True, help="Show only category breakdown")
@click.pass_context
def storage(ctx: click.Context, top: int, category: bool) -> None:
    """Display storage analytics and breakdown."""
    console = ctx.obj["console"]

    # TODO: Implement in Week 2
    console.print("[yellow]⚠️  Storage analyzer not yet implemented[/yellow]")
    console.print("[dim]This feature will be available after Week 2[/dim]")

    console.print(f"[dim]Top consumers: {top}[/dim]")
    if category:
        console.print("[dim]View: category breakdown only[/dim]")


# =============================================================================
# EXPORT COMMANDS
# =============================================================================

@main.group()
@click.pass_context
def export(ctx: click.Context) -> None:
    """Export configuration to various formats."""
    pass


@export.command("json")
@click.option("--output", "-o", type=click.Path(), default=None,
              help="Output file path (default: ./brewstanza.json)")
@click.pass_context
def export_json(ctx: click.Context, output: str) -> None:
    """Export configuration to JSON format."""
    console = ctx.obj["console"]

    # TODO: Implement in Week 3
    console.print("[yellow]⚠️  JSON export not yet implemented[/yellow]")
    console.print("[dim]This feature will be available after Week 3[/dim]")


@export.command("markdown")
@click.option("--output", "-o", type=click.Path(), default=None,
              help="Output file path (default: ./BREWSTANZA.md)")
@click.pass_context
def export_markdown(ctx: click.Context, output: str) -> None:
    """Export configuration to Markdown format."""
    console = ctx.obj["console"]

    # TODO: Implement in Week 3
    console.print("[yellow]⚠️  Markdown export not yet implemented[/yellow]")
    console.print("[dim]This feature will be available after Week 3[/dim]")


@export.command("brewfile")
@click.option("--output", "-o", type=click.Path(), default=None,
              help="Output file path (default: ./Brewfile)")
@click.pass_context
def export_brewfile(ctx: click.Context, output: str) -> None:
    """Export configuration to Brewfile format."""
    console = ctx.obj["console"]

    # TODO: Implement in Week 3
    console.print("[yellow]⚠️  Brewfile export not yet implemented[/yellow]")
    console.print("[dim]This feature will be available after Week 3[/dim]")


# =============================================================================
# SYNC COMMANDS
# =============================================================================

@main.command()
@click.option("--repo", "-r", required=False, help="GitHub repository (format: owner/repo)")
@click.option("--token", "-t", required=False, help="GitHub personal access token")
@click.option("--message", "-m", default=None, help="Custom commit message")
@click.pass_context
def sync(ctx: click.Context, repo: str, token: str, message: str) -> None:
    """Sync configuration to GitHub repository."""
    console = ctx.obj["console"]

    # TODO: Implement in Week 3
    console.print("[yellow]⚠️  GitHub sync not yet implemented[/yellow]")
    console.print("[dim]This feature will be available after Week 3[/dim]")

    if repo:
        console.print(f"[dim]Target repo: {repo}[/dim]")


# =============================================================================
# AI COMMANDS (Phase 2)
# =============================================================================

@main.group(hidden=True)
@click.pass_context
def ai(ctx: click.Context) -> None:
    """Scan and manage AI tool configurations (Phase 2)."""
    pass


@ai.command("list", hidden=True)
@click.pass_context
def ai_list(ctx: click.Context) -> None:
    """List detected AI tool configurations."""
    console = ctx.obj["console"]
    console.print("[dim]AI Configuration Scanner coming in Phase 2[/dim]")


@ai.command("info", hidden=True)
@click.argument("tool", required=True)
@click.pass_context
def ai_info(ctx: click.Context, tool: str) -> None:
    """Show AI tool configuration details."""
    console = ctx.obj["console"]
    console.print(f"[dim]AI info for '{tool}' coming in Phase 2[/dim]")


@ai.command("backup", hidden=True)
@click.pass_context
def ai_backup(ctx: click.Context) -> None:
    """Backup all AI configurations."""
    console = ctx.obj["console"]
    console.print("[dim]AI backup coming in Phase 2[/dim]")


if __name__ == "__main__":
    main()
