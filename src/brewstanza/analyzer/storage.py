"""
Storage Analyzer Module - Calculate and aggregate storage metrics.
"""

from typing import TypedDict

from brewstanza.scanner.disk import ScanSummary


class StorageItem(TypedDict):
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

    def aggregate(self, summary: ScanSummary, top_n: int = 10) -> StorageReport:
        """
        Aggregate a ScanSummary into a StorageReport.

        Args:
            summary: The raw disk scan results.
            top_n: Number of top consumers to include in the list.

        Returns:
            A structured StorageReport.
        """
        homebrew_total = 0
        apps_total = 0
        items: list[StorageItem] = []

        for result in summary.results:
            # We determine the type mostly by whether it's an .app bundle
            if result.path.suffix == ".app":
                item_type = "app"
                apps_total += result.size_bytes
            else:
                item_type = "homebrew"
                homebrew_total += result.size_bytes

            items.append(
                {
                    "name": result.path.name,
                    "size": result.size_bytes,
                    "type": item_type,
                    "percentage": 0.0,
                }
            )

        combined_total = homebrew_total + apps_total

        for item in items:
            if combined_total > 0:
                item["percentage"] = (item["size"] / combined_total) * 100.0

        items.sort(key=lambda x: x["size"], reverse=True)
        top_items = items[:top_n]

        return {
            "homebrew_total": homebrew_total,
            "apps_total": apps_total,
            "combined_total": combined_total,
            "items": top_items,
        }
