"""
Tests for BrewStanza storage analyzer.
"""

from pathlib import Path

from brewstanza.analyzer.storage import StorageAnalyzer
from brewstanza.scanner.disk import ScanResult, ScanSummary


def test_aggregate_calculates_totals_and_percentages() -> None:
    summary = ScanSummary(
        results=[
            ScanResult(path=Path("/Applications/App1.app"), size_bytes=200),
            ScanResult(path=Path("/Applications/App2.app"), size_bytes=100),
            ScanResult(path=Path("/opt/homebrew/Cellar/pkg1"), size_bytes=500),
            ScanResult(path=Path("/opt/homebrew/Cellar/pkg2"), size_bytes=200),
        ]
    )

    analyzer = StorageAnalyzer()
    report = analyzer.aggregate(summary, top_n=3)

    assert report["apps_total"] == 300
    assert report["homebrew_total"] == 700
    assert report["combined_total"] == 1000

    assert len(report["items"]) == 3

    # Check top 1
    assert report["items"][0]["name"] == "pkg1"
    assert report["items"][0]["size"] == 500
    assert report["items"][0]["type"] == "homebrew"
    assert report["items"][0]["percentage"] == 50.0

    # Check top 2 (stable sort means App1.app comes before pkg2 since it was first in results)
    assert report["items"][1]["name"] == "App1.app"
    assert report["items"][1]["size"] == 200
    assert report["items"][1]["type"] == "app"
    assert report["items"][1]["percentage"] == 20.0

    # Check top 3
    assert report["items"][2]["name"] == "pkg2"
    assert report["items"][2]["size"] == 200
    assert report["items"][2]["type"] == "homebrew"
    assert report["items"][2]["percentage"] == 20.0


def test_aggregate_empty_summary() -> None:
    summary = ScanSummary(results=[])
    analyzer = StorageAnalyzer()
    report = analyzer.aggregate(summary)

    assert report["apps_total"] == 0
    assert report["homebrew_total"] == 0
    assert report["combined_total"] == 0
    assert len(report["items"]) == 0


# ---------------------------------------------------------------------------
# format_size — cover all size units including PB (line 96)
# ---------------------------------------------------------------------------


def test_format_size_bytes() -> None:
    assert StorageAnalyzer.format_size(512) == "512.0 B"


def test_format_size_kb() -> None:
    assert StorageAnalyzer.format_size(2048) == "2.0 KB"


def test_format_size_mb() -> None:
    assert StorageAnalyzer.format_size(5 * 1024 * 1024) == "5.0 MB"


def test_format_size_gb() -> None:
    assert StorageAnalyzer.format_size(3 * 1024**3) == "3.0 GB"


def test_format_size_tb() -> None:
    assert StorageAnalyzer.format_size(2 * 1024**4) == "2.0 TB"


def test_format_size_pb() -> None:
    """Exercise the PB fallthrough at line 96."""
    assert "PB" in StorageAnalyzer.format_size(2 * 1024**5)


def test_format_size_zero() -> None:
    assert StorageAnalyzer.format_size(0) == "0.0 B"


# ---------------------------------------------------------------------------
# aggregate — zero combined_total branch (line 67->66)
# ---------------------------------------------------------------------------


def test_aggregate_zero_size_items_have_zero_percentage() -> None:
    """Items with size_bytes=0 should not raise ZeroDivisionError."""
    from pathlib import Path

    summary = ScanSummary(
        results=[ScanResult(path=Path("/opt/homebrew/Cellar/emptypkg"), size_bytes=0)]
    )
    analyzer = StorageAnalyzer()
    report = analyzer.aggregate(summary)
    # combined_total is 0 — percentage must stay 0.0, not raise
    assert report["items"][0]["percentage"] == 0.0

