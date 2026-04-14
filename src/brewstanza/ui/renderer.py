"""
UI Renderer Module - Format and display output using Rich.
"""

from typing import Any

from rich.console import Console
from rich.table import Table


class UIRenderer:
    """Renderer for terminal output using Rich library."""

    def __init__(self, no_color: bool = False):
        self.console = Console(no_color=no_color)

    def render_package_table(
        self, packages: list[dict[str, Any]], title: str = "Packages"
    ) -> None:
        """
        Render a table of packages.

        Args:
            packages: List of package dictionaries
            title: Table title
        """
        # TODO: Implement in Week 1
        table = Table(title=title)
        table.add_column("Name", style="cyan")
        table.add_column("Version", style="green")
        table.add_column("Size", style="yellow")

        for pkg in packages:
            table.add_row(
                pkg.get("name", ""), pkg.get("version", ""), pkg.get("size", "")
            )

        self.console.print(table)

    def render_app_table(
        self, apps: list[dict[str, Any]], title: str = "Applications"
    ) -> None:
        """
        Render a table of applications with categories.

        Args:
            apps: List of app dictionaries
            title: Table title
        """
        # TODO: Implement in Week 2
        table = Table(title=title)
        table.add_column("Name", style="cyan")
        table.add_column("Category", style="magenta")
        table.add_column("Version", style="green")
        table.add_column("Size", style="yellow")

        self.console.print(table)

    def render_storage_breakdown(self, data: dict[str, Any]) -> None:
        """
        Render storage breakdown with visual bars.

        Args:
            data: Dictionary with category names and sizes
        """
        # TODO: Implement in Week 2
        pass

    def render_package_detail(self, package: dict[str, Any]) -> None:
        """
        Render detailed view of a single package.

        Args:
            package: Package dictionary with all details
        """
        # TODO: Implement in Week 1
        pass

    def render_removal_instructions(self, app: dict[str, Any]) -> None:
        """
        Render removal instructions for an application.

        Args:
            app: Application dictionary
        """
        # TODO: Implement in Week 2
        pass

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
