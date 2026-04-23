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
