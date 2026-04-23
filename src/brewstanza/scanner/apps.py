"""
Application Scanner Module - Scan and analyze installed macOS applications.
"""

from pathlib import Path


class AppScanner:
    """Scanner for macOS applications (.app bundles)."""

    def __init__(self) -> None:
        self.system_apps = Path("/Applications")
        self.user_apps = Path.home() / "Applications"

    def collect_app_paths(self) -> list[Path]:
        """
        Glob /Applications and ~/Applications for .app bundles.
        Handles missing directories gracefully.

        Returns:
            List of paths to .app bundles
        """
        app_paths: list[Path] = []

        for base_dir in [self.system_apps, self.user_apps]:
            if not base_dir.exists() or not base_dir.is_dir():
                continue

            for app_dir in base_dir.glob("*.app"):
                app_paths.append(app_dir)

        return app_paths
