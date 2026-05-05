"""
BrewStanza CLI - Main entry point.
"""

import json
from pathlib import Path

import click
from rich.console import Console

from brewstanza import __version__
from brewstanza.analyzer.storage import StorageAnalyzer
from brewstanza.config import Config
from brewstanza.exporter.export import ExportManager
from brewstanza.exporter.github_sync import GitHubSync, GitHubSyncError
from brewstanza.scanner.apps import AppScanner
from brewstanza.scanner.disk import scan_paths
from brewstanza.scanner.homebrew import HomebrewScanner
from brewstanza.ui.renderer import UIRenderer
from brewstanza.wizard import needs_wizard, run_wizard

# ---------------------------------------------------------------------------
# Default output filenames
# ---------------------------------------------------------------------------
_DEFAULT_JSON_FILE = "brewstanza-snapshot.json"
_DEFAULT_BREWFILE = "Brewfile"


# ---------------------------------------------------------------------------
# Root group
# ---------------------------------------------------------------------------


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
    ctx.obj["renderer"] = UIRenderer(no_color=no_color)
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
@click.option("--formula", "-f", "formula_only", is_flag=True, help="List only formulae")
@click.option("--cask", "-c", "cask_only", is_flag=True, help="List only casks")
@click.option("--size", "-s", is_flag=True, default=True, help="Show package sizes")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.pass_context
def brew_list(
    ctx: click.Context,
    formula_only: bool,
    cask_only: bool,
    size: bool,
    output_json: bool,
) -> None:
    """List installed Homebrew packages with sizes."""
    renderer: UIRenderer = ctx.obj["renderer"]
    scanner = HomebrewScanner()

    info = scanner.get_all_installed_info()
    outdated = set(scanner.get_outdated())

    formulae = info.get("formulae", [])
    casks = info.get("casks", [])

    if formula_only:
        casks = []
    elif cask_only:
        formulae = []

    packages = []
    paths_to_scan = []
    pkg_refs = []

    cellar_base = Path(scanner._run_brew_command(["--cellar"])) if formulae else None
    caskroom_base = Path(scanner._run_brew_command(["--prefix"])) / "Caskroom" if casks else None

    for f in formulae:
        name = f.get("name")
        installed = f.get("installed", [{}])
        version = installed[0].get("version", "unknown") if installed else "unknown"
        pkg = {"name": name, "version": version, "outdated": name in outdated, "size": 0}
        packages.append(pkg)
        if cellar_base and installed:
            path = cellar_base / name / version
            paths_to_scan.append(path)
            pkg_refs.append(pkg)

    for c in casks:
        name = c.get("token")
        version = c.get("installed", "unknown")
        pkg = {"name": name, "version": version, "outdated": name in outdated, "size": 0}
        packages.append(pkg)
        if caskroom_base:
            path = caskroom_base / name
            paths_to_scan.append(path)
            pkg_refs.append(pkg)

    if size and paths_to_scan:
        summary = scan_paths(
            paths_to_scan,
            label="Scanning package sizes...",
            console=ctx.obj["console"],
        )
        for result, pkg in zip(summary.results, pkg_refs):
            pkg["size"] = result.size_bytes

    if output_json:
        print(json.dumps(packages, indent=2))
    else:
        renderer.render_package_table(packages)


@brew.command("info")
@click.argument("package", required=True)
@click.pass_context
def brew_info(ctx: click.Context, package: str) -> None:
    """Show detailed information about a package."""
    renderer: UIRenderer = ctx.obj["renderer"]
    scanner = HomebrewScanner()

    try:
        info = scanner.get_info(package)
    except RuntimeError as e:
        renderer.print_error(str(e))
        return

    is_cask = False
    f_info = info.get("formulae", [])
    c_info = info.get("casks", [])

    if f_info:
        data = f_info[0]
    elif c_info:
        data = c_info[0]
        is_cask = True
    else:
        renderer.print_error("Package not found.")
        return

    name = data.get("name") or data.get("token")
    desc = data.get("desc", "No description")

    if is_cask:
        version = data.get("version", "unknown")
        caskroom_base = Path(scanner._run_brew_command(["--prefix"])) / "Caskroom"
        path = caskroom_base / name
    else:
        installed = data.get("installed", [{}])
        version = installed[0].get("version", "unknown") if installed else "unknown"
        cellar_base = Path(scanner._run_brew_command(["--cellar"]))
        path = cellar_base / name / version

    summary = scan_paths([path], label=f"Scanning {name}...", console=ctx.obj["console"])
    size_bytes = summary.total_bytes

    pkg = {
        "name": name,
        "desc": desc,
        "version": version,
        "size": size_bytes,
        "path": str(path),
    }

    renderer.render_package_detail(pkg)


@brew.command("outdated")
@click.pass_context
def brew_outdated(ctx: click.Context) -> None:
    """List outdated packages."""
    renderer: UIRenderer = ctx.obj["renderer"]
    scanner = HomebrewScanner()
    outdated = scanner.get_outdated()
    if outdated:
        for pkg in outdated:
            renderer.console.print(f"[yellow]{pkg}[/yellow]")
    else:
        renderer.print_success("All packages are up to date.")


# =============================================================================
# APPS COMMANDS
# =============================================================================


@main.group()
@click.pass_context
def apps(ctx: click.Context) -> None:
    """Scan and manage installed applications."""
    pass


@apps.command("list")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.pass_context
def apps_list(ctx: click.Context, output_json: bool) -> None:
    """List installed applications."""
    renderer: UIRenderer = ctx.obj["renderer"]
    scanner = AppScanner()

    paths = scanner.collect_app_paths()
    summary = scan_paths(paths, label="Scanning applications...", console=ctx.obj["console"])

    app_data = []
    for result in summary.results:
        app_data.append(
            {"name": result.path.stem, "path": str(result.path), "size": result.size_bytes}
        )

    app_data.sort(key=lambda x: str(x["name"]).lower())

    if output_json:
        print(json.dumps(app_data, indent=2))
    else:
        renderer.render_app_table(app_data)


@apps.command("info")
@click.argument("app_name", required=True)
@click.pass_context
def apps_info(ctx: click.Context, app_name: str) -> None:
    """Show app details with removal instructions."""
    renderer: UIRenderer = ctx.obj["renderer"]
    scanner = AppScanner()

    paths = scanner.collect_app_paths()
    app_path = next((p for p in paths if p.stem.lower() == app_name.lower()), None)

    if not app_path:
        renderer.print_error(f"Application '{app_name}' not found in standard locations.")
        return

    renderer.render_removal_instructions({"name": app_path.stem, "path": str(app_path)})


# =============================================================================
# STORAGE COMMANDS
# =============================================================================


@main.command()
@click.option("--top", "-t", default=10, help="Show top N storage consumers")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.pass_context
def storage(ctx: click.Context, top: int, output_json: bool) -> None:
    """Display storage analytics and breakdown."""
    renderer: UIRenderer = ctx.obj["renderer"]

    brew_scanner = HomebrewScanner()
    app_scanner = AppScanner()

    info = brew_scanner.get_all_installed_info()
    formulae = info.get("formulae", [])
    casks = info.get("casks", [])

    paths_to_scan = []

    # Homebrew paths
    cellar_base = Path(brew_scanner._run_brew_command(["--cellar"])) if formulae else None
    caskroom_base = (
        Path(brew_scanner._run_brew_command(["--prefix"])) / "Caskroom" if casks else None
    )

    for f in formulae:
        name = f.get("name")
        installed = f.get("installed", [{}])
        version = installed[0].get("version", "unknown") if installed else "unknown"
        if cellar_base and installed:
            paths_to_scan.append(cellar_base / name / version)

    for c in casks:
        name = c.get("token")
        if caskroom_base:
            paths_to_scan.append(caskroom_base / name)

    # App paths
    paths_to_scan.extend(app_scanner.collect_app_paths())

    summary = scan_paths(
        paths_to_scan,
        label="Scanning entire system storage...",
        console=ctx.obj["console"],
    )

    analyzer = StorageAnalyzer()
    report = analyzer.aggregate(summary, top_n=top)

    if output_json:
        print(json.dumps(report, indent=2))
    else:
        renderer.render_storage_breakdown(report)


# =============================================================================
# EXPORT COMMANDS
# =============================================================================


@main.group()
@click.pass_context
def export(ctx: click.Context) -> None:
    """Export your environment inventory to a file."""
    pass


@export.command("json")
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default=_DEFAULT_JSON_FILE,
    show_default=True,
    help="Destination file path",
)
@click.option("--top", "-t", default=10, show_default=True, help="Top N consumers to include")
@click.pass_context
def export_json(ctx: click.Context, output: str, top: int) -> None:
    """Export a full inventory snapshot to JSON format."""
    console: Console = ctx.obj["console"]
    renderer: UIRenderer = ctx.obj["renderer"]

    console.print("[cyan]Collecting inventory…[/cyan]")

    brew_scanner = HomebrewScanner()
    app_scanner = AppScanner()

    info = brew_scanner.get_all_installed_info()
    formulae = info.get("formulae", [])
    casks = info.get("casks", [])

    paths_to_scan: list[Path] = []

    cellar_base = Path(brew_scanner._run_brew_command(["--cellar"])) if formulae else None
    caskroom_base = (
        Path(brew_scanner._run_brew_command(["--prefix"])) / "Caskroom" if casks else None
    )
    for f in formulae:
        installed = f.get("installed", [{}])
        version = installed[0].get("version", "unknown") if installed else "unknown"
        if cellar_base and installed:
            paths_to_scan.append(cellar_base / f["name"] / version)

    for c in casks:
        if caskroom_base:
            paths_to_scan.append(caskroom_base / c["token"])

    paths_to_scan.extend(app_scanner.collect_app_paths())

    disk_summary = scan_paths(paths_to_scan, label="Scanning disk…", console=console)
    analyzer = StorageAnalyzer()
    report = analyzer.aggregate(disk_summary, top_n=top)

    content = ExportManager.to_json(report)
    dest = Path(output)
    ExportManager.write_file(content, dest)
    renderer.print_success(f"Snapshot written to [cyan]{dest.resolve()}[/cyan]")


@export.command("brewfile")
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default=_DEFAULT_BREWFILE,
    show_default=True,
    help="Destination file path",
)
@click.pass_context
def export_brewfile(ctx: click.Context, output: str) -> None:
    """Export installed Homebrew packages to Brewfile format."""
    console: Console = ctx.obj["console"]
    renderer: UIRenderer = ctx.obj["renderer"]

    console.print("[cyan]Collecting Homebrew packages…[/cyan]")
    scanner = HomebrewScanner()
    info = scanner.get_all_installed_info()

    packages = []
    for f in info.get("formulae", []):
        installed = f.get("installed", [{}])
        version = installed[0].get("version", "unknown") if installed else "unknown"
        packages.append({"name": f["name"], "version": version, "type": "formula"})
    for c in info.get("casks", []):
        packages.append({"name": c["token"], "version": c.get("installed", ""), "type": "cask"})

    content = ExportManager.to_brewfile(packages)
    dest = Path(output)
    ExportManager.write_file(content, dest)
    renderer.print_success(f"Brewfile written to [cyan]{dest.resolve()}[/cyan]")


# =============================================================================
# SYNC COMMAND
# =============================================================================


@main.command()
@click.option("--dry-run", is_flag=True, help="Show what would be committed without pushing")
@click.option("--top", "-t", default=10, show_default=True, help="Top N consumers in JSON")
@click.pass_context
def sync(ctx: click.Context, dry_run: bool, top: int) -> None:
    """Commit a Brewfile + JSON snapshot to your GitHub repository."""
    console: Console = ctx.obj["console"]
    renderer: UIRenderer = ctx.obj["renderer"]

    # First-run wizard if config is missing or incomplete
    if needs_wizard():
        console.print(
            "[yellow]⚠[/yellow]  GitHub config is not set up. "
            "Let's configure it now.\n"
        )
        if not run_wizard(console=console):
            console.print("[red]✗[/red] Setup cancelled. Run [bold]brewstanza sync[/bold] again.")
            return

    config = Config.load()
    github_sync = GitHubSync(config)

    console.print("[cyan]Collecting inventory for sync…[/cyan]")

    # --- Build JSON snapshot ---
    brew_scanner = HomebrewScanner()
    app_scanner = AppScanner()

    info = brew_scanner.get_all_installed_info()
    formulae = info.get("formulae", [])
    casks = info.get("casks", [])

    paths_to_scan: list[Path] = []
    cellar_base = Path(brew_scanner._run_brew_command(["--cellar"])) if formulae else None
    caskroom_base = (
        Path(brew_scanner._run_brew_command(["--prefix"])) / "Caskroom" if casks else None
    )
    for f in formulae:
        installed = f.get("installed", [{}])
        version = installed[0].get("version", "unknown") if installed else "unknown"
        if cellar_base and installed:
            paths_to_scan.append(cellar_base / f["name"] / version)
    for c in casks:
        if caskroom_base:
            paths_to_scan.append(caskroom_base / c["token"])
    paths_to_scan.extend(app_scanner.collect_app_paths())

    disk_summary = scan_paths(paths_to_scan, label="Scanning disk…", console=console)
    analyzer = StorageAnalyzer()
    report = analyzer.aggregate(disk_summary, top_n=top)
    json_content = ExportManager.to_json(report)

    # --- Build Brewfile ---
    packages = []
    for f in formulae:
        installed = f.get("installed", [{}])
        version = installed[0].get("version", "unknown") if installed else "unknown"
        packages.append({"name": f["name"], "version": version, "type": "formula"})
    for c in casks:
        packages.append({"name": c["token"], "version": c.get("installed", ""), "type": "cask"})
    brewfile_content = ExportManager.to_brewfile(packages)

    files = {
        _DEFAULT_JSON_FILE: json_content,
        _DEFAULT_BREWFILE: brewfile_content,
    }

    try:
        result = github_sync.sync(files, dry_run=dry_run)
        renderer.print_success(result) if not dry_run else console.print(result)
    except GitHubSyncError as exc:
        renderer.print_error(str(exc))


# =============================================================================
# AI COMMANDS (Phase 2)
# =============================================================================


@main.group(hidden=True)
@click.pass_context
def ai(ctx: click.Context) -> None:
    pass


@ai.command("list", hidden=True)
@click.pass_context
def ai_list(ctx: click.Context) -> None:
    ctx.obj["console"].print("[dim]AI Configuration Scanner coming in Phase 2[/dim]")


@ai.command("info", hidden=True)
@click.argument("tool", required=True)
@click.pass_context
def ai_info(ctx: click.Context, tool: str) -> None:
    ctx.obj["console"].print(f"[dim]AI info for '{tool}' coming in Phase 2[/dim]")


@ai.command("backup", hidden=True)
@click.pass_context
def ai_backup(ctx: click.Context) -> None:
    ctx.obj["console"].print("[dim]AI backup coming in Phase 2[/dim]")


if __name__ == "__main__":
    main()
