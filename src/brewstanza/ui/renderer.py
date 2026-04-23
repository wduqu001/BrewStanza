"""
UI Renderer Module - Format and display output using Rich.
"""

from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from brewstanza.analyzer.storage import StorageAnalyzer, StorageReport


class UIRenderer:
    """Renderer for terminal output using Rich library."""

    def __init__(self, no_color: bool = False):
        self.console = Console(no_color=no_color)

    def render_package_table(self, packages: list[dict[str, Any]], title: str = "Packages") -> None:
        """
        Render a table of packages.

        Args:
            packages: List of package dictionaries (name, version, size, outdated)
            title: Table title
        """
        table = Table(title=title)
        table.add_column("Name", style="cyan")
        table.add_column("Version", style="green")
        table.add_column("Size", style="yellow", justify="right")
        table.add_column("Outdated", style="red", justify="center")

        for pkg in packages:
            outdated_marker = "⚠️" if pkg.get("outdated") else ""
            size_str = StorageAnalyzer.format_size(pkg.get("size", 0))
            table.add_row(
                pkg.get("name", ""),
                pkg.get("version", ""),
                size_str,
                outdated_marker,
            )

        self.console.print(table)

    def render_app_table(self, apps: list[dict[str, Any]], title: str = "Applications") -> None:
        """
        Render a table of applications.

        Args:
            apps: List of app dictionaries
            title: Table title
        """
        table = Table(title=title)
        table.add_column("Name", style="cyan")
        table.add_column("Path", style="magenta")
        table.add_column("Size", style="yellow", justify="right")

        for app in apps:
            size_str = StorageAnalyzer.format_size(app.get("size", 0))
            table.add_row(
                app.get("name", ""),
                str(app.get("path", "")),
                size_str,
            )

        self.console.print(table)

    def render_storage_breakdown(self, report: StorageReport) -> None:
        """
        Render storage breakdown with visual bars.

        Args:
            report: StorageReport dictionary
        """
        self.console.print("\n[bold]Storage Breakdown[/bold]")

        homebrew_total = report.get("homebrew_total", 0)
        apps_total = report.get("apps_total", 0)
        combined_total = report.get("combined_total", 0)

        table = Table(show_header=False, box=None)
        table.add_column("Category", style="cyan")
        table.add_column("Size", style="yellow", justify="right")
        table.add_row("Homebrew", StorageAnalyzer.format_size(homebrew_total))
        table.add_row("Applications", StorageAnalyzer.format_size(apps_total))
        table.add_row(
            "[bold]Total[/bold]", f"[bold]{StorageAnalyzer.format_size(combined_total)}[/bold]"
        )

        self.console.print(Panel(table, title="Summary", expand=False))

        items = report.get("items", [])
        if items:
            self.console.print("\n[bold]Top Consumers[/bold]")
            top_table = Table(box=None)
            top_table.add_column("Name", style="cyan")
            top_table.add_column("Type", style="magenta")
            top_table.add_column("Size", style="yellow", justify="right")
            top_table.add_column("Share", justify="right")

            for item in items:
                size_str = StorageAnalyzer.format_size(item.get("size", 0))
                pct = item.get("percentage", 0.0)
                bars = "█" * int(pct / 5)
                top_table.add_row(
                    item.get("name", ""),
                    item.get("type", ""),
                    size_str,
                    f"{pct:.1f}% [cyan]{bars}[/cyan]",
                )
            self.console.print(top_table)

    def render_package_detail(self, package: dict[str, Any]) -> None:
        """
        Render detailed view of a single package.

        Args:
            package: Package dictionary with all details
        """
        content = Text()
        content.append("Name: ", style="bold")
        content.append(f"{package.get('name', 'Unknown')}\n")

        content.append("Description: ", style="bold")
        content.append(f"{package.get('desc', 'No description')}\n")

        content.append("Version: ", style="bold")
        content.append(f"{package.get('version', 'Unknown')}\n")

        content.append("Size: ", style="bold")
        content.append(f"{StorageAnalyzer.format_size(package.get('size', 0))}\n")

        content.append("Cellar Path: ", style="bold")
        content.append(f"{package.get('path', 'Unknown')}\n\n")

        content.append("To uninstall, run:\n", style="bold yellow")
        content.append(f"  brew uninstall {package.get('name')}", style="cyan")

        panel = Panel(content, title="Package Info", expand=False)
        self.console.print(panel)

    def render_removal_instructions(self, app: dict[str, Any]) -> None:
        """
        Render removal instructions for an application.

        Args:
            app: Application dictionary
        """
        content = Text()
        content.append(
            "To uninstall this application, you can usually delete it from the "
            "Applications folder:\n\n"
        )
        content.append(f'  rm -rf "{app.get("path")}"', style="bold red")

        panel = Panel(content, title="Uninstall Instructions", border_style="red", expand=False)
        self.console.print(panel)

    def print_success(self, message: str) -> None:
        """Print a success message."""
        self.console.print(f"[green]✓[/green] {message}")

    def print_error(self, message: str) -> None:
        """Print an error message."""
        self.console.print(f"[red]✗[/red] {message}")

    def print_warning(self, message: str) -> None:
        """Print a warning message."""
        self.console.print(f"[yellow]⚠[/yellow] {message}")

    def print_info(self, message: str) -> None:
        """Print an info message."""
        self.console.print(f"[blue]ℹ[/blue] {message}")
