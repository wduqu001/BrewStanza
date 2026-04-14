"""
Storage Analyzer Module - Calculate and aggregate storage metrics.
"""

from typing import Any, Optional, TypedDict


class StorageItem(TypedDict, total=False):
    """Single storage item entry in a report."""

    name: str
    size: int
    type: str
    percentage: float


class StorageReport(TypedDict):
    """Top-level storage report structure for exporters."""

    homebrew_total: int
    apps_total: int
    combined_total: int
    items: list[StorageItem]


class StorageAnalyzer:
    """Analyzer for storage consumption metrics."""

    def __init__(self) -> None:
        self._homebrew_total: Optional[int] = None
        self._apps_total: Optional[int] = None

    def calculate_total_homebrew_storage(self) -> int:
        """
        Calculate total storage used by Homebrew.

        Includes:
        - Cellar (formulae)
        - Caskroom (casks)
        - Cache
        - Logs

        Returns:
            Total size in bytes
        """
        # Note: this function is a placeholder until actual scanning logic is added.
        return self._homebrew_total or 0

    def calculate_total_app_storage(self, apps: list[dict[str, Any]]) -> int:
        """
        Calculate total storage used by applications.

        Args:
            apps: List of app dictionaries from AppScanner

        Returns:
            Total size in bytes
        """
        total = 0
        for app in apps:
            size = app.get("size", 0)
            if not isinstance(size, int):
                try:
                    size = int(size)
                except (TypeError, ValueError):
                    size = 0
            total += size
        self._apps_total = total
        return total

    def get_top_consumers(
        self, items: list[dict[str, Any]], n: int = 10
    ) -> list[dict[str, Any]]:
        """
        Get top N largest items by size.

        Args:
            items: List of item dictionaries with 'size' key
            n: Number of top items to return

        Returns:
            Sorted list of top N items
        """
        sorted_items = sorted(
            items,
            key=lambda item: (
                item.get("size", 0)
                if isinstance(item.get("size", 0), (int, float))
                else 0
            ),
            reverse=True,
        )
        return sorted_items[:n]

    def get_percentage_distribution(self, sizes: dict[str, int]) -> dict[str, float]:
        """
        Calculate percentage distribution of sizes.

        Args:
            sizes: Dictionary mapping names to sizes

        Returns:
            Dictionary mapping names to percentages (0-100)
        """
        total = sum(
            value for value in sizes.values() if isinstance(value, (int, float))
        )
        if total <= 0:
            return {key: 0.0 for key in sizes}

        return {
            key: float(value) / total * 100 if isinstance(value, (int, float)) else 0.0
            for key, value in sizes.items()
        }

    @staticmethod
    def format_size(size_bytes: int) -> str:
        """
        Format bytes to human-readable string.

        Args:
            size_bytes: Size in bytes

        Returns:
            Human-readable string (e.g., "1.5 GB")
        """
        size: float = float(size_bytes)
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"
